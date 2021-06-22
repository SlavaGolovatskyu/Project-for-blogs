from app import db
from . import main
from math import ceil

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
	Article
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

MIN_LENGTH_TEXT = 300
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

					change_data.article_save_changes(
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
	comments_need = article.comments[::-1][search_first_index : search_second_index]

	# if user a note comment to the article
	if request.method == 'POST':
		text = request.form.get('text')

		# search comment like it in database
		check_on_spam = find_data.find_comment(article, count=True, text=text, post_id=id)

		if validator.check_length(max_length_comment, text):
			# If comments does not in database we will creating new comment
			if check_on_spam < 2:
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
											    name=current_user.username,
											    post_id=id)
			db.session.commit()

	return render_template('post_detail.html', article=article, comments=comments_need,
						   count_comments=current_count_comments_on_page, post_id=id,
						   const_count=CONST_COUNT)


@main.route('/posts/page/<int:page>')
def posts(page):
	username = current_user.username if current_user.is_authenticated else 'AnonymousUser'
	logger.info(f'User {username} watching all articles on the site')
	# Search count all posts in database
	count_all_posts = Article.query.count()

	# const method sorting if not other method
	method_for_sorting = 'date'

	if request.args.get('views', '') == 'True':
		method_for_sorting = 'views'

	# Search count pages with help count_all_posts
	count_dynamic_pages = ceil(count_all_posts / MAX_COUNT_POSTS_ON_PAGE)

	"""
		* Search posts between first_index = page * 10 - 10 
		* to second_index = page * 10
		* for example: if page 1 = first_index = 1, second_index = 10 because page * 10
	"""
	search_first_index = page * MAX_COUNT_POSTS_ON_PAGE - MAX_COUNT_POSTS_ON_PAGE
	search_second_index = page * MAX_COUNT_POSTS_ON_PAGE

	# Needed posts (max MAX_COUNT_POSTS_ON_PAGE)
	articles_need = find_data.find_articles_order_by(method_for_sorting,
													 search_first_index,
													 search_second_index)

	# If User input incorrect page in URL address'
	if page > count_dynamic_pages and count_all_posts != 0 or page == 0:
		flash(f"Page {page} does not exist")
		return redirect(url_for('.posts', page=1))
	else:
		return render_template('posts.html', articles=articles_need, current_page=page,
							   count_dynamic_pages=count_dynamic_pages,
							   method_sorting=method_for_sorting)


@main.route('/user/posts/<int:page>')
@login_required
def user_posts(page):
	logger.info(f'User {current_user.username} watching himself articles')
	user = find_data.find_user(current_user.id)

	all_posts_user = user.posts.count()

	count_dynamic_pages = ceil(all_posts_user / MAX_COUNT_POSTS_ON_PAGE)

	"""
		* Search posts between first_index = page * 10 - 10 
		* to second_index = page * 10	    * for example: if page 1 = first_index = 1,
		* second_index = 10 because page * 10
	"""
	search_first_index = page * MAX_COUNT_POSTS_ON_PAGE - MAX_COUNT_POSTS_ON_PAGE
	search_second_index = page * MAX_COUNT_POSTS_ON_PAGE

	# Needed posts (max MAX_COUNT_POSTS_ON_PAGE)
	# [::-1] reverse array and then search needed posts with help:
	# [search_first_index : search_second_index]
	articles_need = user.posts[::-1][search_first_index: search_second_index]

	# If User input incorrect page in URL address'
	if page > count_dynamic_pages and all_posts_user != 0 or page == 0:
		flash(f"Page {page} does not exist")
		return redirect(url_for('.posts', page=1))
	else:
		return render_template('user_posts.html', current_page=page, articles=articles_need,
							   count_dynamic_pages=count_dynamic_pages)


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
