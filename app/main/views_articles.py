from app import db
from . import main

from flask import (
	request,
	render_template,
	abort,
	redirect,
	url_for,
	flash
)

from flask_login import (
	login_required,
	current_user
)

from ..models import (
	Article,
	Comment
)

from .validators import Validators
from ..db_controll import (
	FindData,
	DeleteData,
	AddNewData,
	ChangeData,
	logger
)

find_data = FindData()
delete_data = DeleteData()
add_data = AddNewData()
change_data = ChangeData()

validator = Validators()

# If you want to increase count posts on page 
# You must do change only this variable: MAX_COUNT_POSTS_ON_PAGE
# And count posts on page will be changed
# CONSTANT VARIABLE
MAX_COUNT_POSTS_ON_PAGE = 20

MIN_LENGTH_TEXT = 30
MAX_LENGTH_TEXT = 15000
max_length_title = 100
max_length_intro = 300
max_length_comment = 500


@main.route('/create-article/', methods=['get', 'post'])
@login_required
def create_article():
	if request.method == 'POST':
		title = request.form.get('title')
		intro = request.form.get('intro')
		text = request.form.get('text')

		if (validator.check_length(max_length_title, title) and
				validator.check_length(max_length_intro, intro)):

			if (validator.check_length(MIN_LENGTH_TEXT, text, True) and
					validator.check_length(MAX_LENGTH_TEXT, text)):
				if add_data.add_new_article(title=title, intro=intro,
											text=text, author_name=current_user.username,
											user_id=current_user.id):
					return redirect(url_for('.posts', page=1))
				return redirect(url_for('.create_article'))
			else:
				flash(f"""Длинна текста должна быть от {MIN_LENGTH_TEXT} до 
					   {MAX_LENGTH_TEXT} символов.""")
				return redirect(url_for('.create_article'))
		else:
			flash(f"""Максимальная длинна <title> {max_length_title}
					   Максимальная длинна <intro> {max_length_intro}""")
			return redirect(url_for('.create_article'))

	return render_template('create_article.html')


@main.route('/posts/<int:article_id>/update', methods=['post', 'get'])
@login_required
def update_user_post(article_id):
	article = find_data.find_article(article_id)

	# checking if founder user of this article or user is admin
	if validator.check_article_or_comment_of_the_owner(article.user_id):

		if request.method == 'POST':

			if (validator.check_length(max_length_title, request.form.get('title')) and
					validator.check_length(max_length_intro, request.form.get('intro'))):

				if (validator.check_length(MIN_LENGTH_TEXT, request.form.get('text'), True) and
						validator.check_length(MAX_LENGTH_TEXT, request.form.get('text'))):

					change_data.article_update_changes(
							article,
							title=request.form['title'],
							intro=request.form['intro'],
							text=request.form['text']
					)
					return redirect(url_for('.posts', page=1))
				else:
					flash(f"""Длинна текста должна быть от {MIN_LENGTH_TEXT} до 
						   {MAX_LENGTH_TEXT} символов.""")
					return redirect(url_for('.update_user_post', article_id=article_id))
			else:
				flash(f"""Максимальная длинна <title> {max_length_title}
					   Максимальная длинна <intro> {max_length_intro}""")
				return redirect(url_for('.update_user_post', article_id=article_id))

		return render_template('update_post.html', article=article)

	else:
		logger.warning(f'User {current_user.username} \
         				wanted update article. But he does not admin or moderator, or founder')
		abort(403)


@main.route('/posts/<int:article_id>/delete')
@login_required
def delete_post_user(article_id):
	# Search needed article or 404
	article = find_data.find_article(article_id)
	# if current_user.id == article.user_id or user is admin we deleting article.
	if validator.check_article_or_comment_of_the_owner(article.user_id):
		delete_data.delete_article(article)
		return redirect(url_for('.posts', page=1))
	else:
		logger.warning(f'User {current_user.username} wanted delete article. But he does not admin, or founder')
		abort(403)


@main.route('/post/<int:id>/detail', methods=['get', 'post'])
def post_detail(id):
	article = find_data.find_article(id)

	current_count_comments_on_page = 15

	# if user will want upload more comments each time flask upload + 10 comment to current_count
	CONST_COUNT = 15

	page = 1

	# takes argument from url address'
	data = request.args.get('count', '')
	# checking if there are data and if data is number
	if data and data.isdigit():
		# change count comments which we upload on page
		current_count_comments_on_page = int(data)

	# first and second index'es important for us because we search information in database
	# after this we took array with information and after this we search need info
	# from first index to second index
	search_first_index = page * current_count_comments_on_page - current_count_comments_on_page
	search_second_index = page * current_count_comments_on_page

	# [::-1] reverse array and search need data
	comments_need = article.comments.order_by(Comment.date.desc()).limit(current_count_comments_on_page) \
																  .offset((page-1) * current_count_comments_on_page) \
																  .all()

	# if user a note comment to the article
	if request.method == 'POST':
		text = request.form.get('text')

		# search comment like it in database
		check_on_spam = article.comments.filter_by(text=text).count()

		if validator.check_length(max_length_comment, text):
			# If comments does not in database we will creating new comment
			if check_on_spam < 1:
				add_data.add_new_comment(text=text, author=current_user.username,
										 user_id=current_user.id, post_id=id)
				return redirect(url_for('.post_detail', id=id))
			else:
				logger.warning(f"""Comment\' user {current_user.username} does not wrote.
								   Because user will spam.""")
				flash('Коментарий не был записан. Вы флудите или спамите.')
				return redirect(url_for('.post_detail', id=id))
		else:
			flash('Слишком длинный коментарий. Максимальная длинна 500 символов.')
			return redirect(url_for('.post_detail', id=id))

	# if user logged in himself account
	elif not current_user.is_anonymous:
		user_viewed = find_data.find_user_which_viewed_post(article, user_id=current_user.id, post_id=id)
		# checking if user watched article in past
		if not user_viewed and article.user_id != current_user.id:
			# Added one to count_views.
			article.count_views += 1

			# Added user in database what he saw this article
			add_data.add_user_which_viewed_post(user_id=current_user.id,
											    post_id=id)
			db.session.commit()

	return render_template('post_detail.html', article=article, comments=comments_need,
						   count_comments=current_count_comments_on_page, post_id=id,
						   const_count=CONST_COUNT)


@main.route('/posts/page/<int:page>')
def posts(page: int = 1):
	# const method sorting if not other method
	method_for_sorting = 'date'

	if request.args.get('views', '') == 'True':
		method_for_sorting = 'views'

	pagination = Article.query.order_by(Article.date.desc() \
										if method_for_sorting == 'date' else \
										Article.count_views.desc()) \
										.paginate(
											page, per_page=MAX_COUNT_POSTS_ON_PAGE
										)

	articles = pagination.items

	return render_template('posts.html', articles=articles,
							method_sorting=method_for_sorting,
							pagination=pagination)


@main.route('/user/posts/<int:page>')
@login_required
def user_posts(page: int = 1):
	logger.info(f'User {current_user.username} watching himself articles')
	user = find_data.find_user(current_user.id)

	pagination = user.posts.order_by(Article.date.desc()).paginate(
		page, per_page=MAX_COUNT_POSTS_ON_PAGE
	)

	articles = pagination.items
	return render_template('user_posts.html',
							articles=articles,
							pagination=pagination)


@main.route('/comment/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user_comment(id):
	comment = find_data.find_comment(id)
	# check if comment belongs user's or current user is_admin
	if validator.check_article_or_comment_of_the_owner(comment.user_id):
		delete_data.delete_comment(comment)
		return redirect(url_for('.post_detail', id=comment.post_id))
	else:
		logger.warning(f'User {current_user.username} wanted delete comment. But he does not admin.')
		abort(403)
