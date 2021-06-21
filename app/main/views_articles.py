from app import db
from . import main
from math import ceil

from flask import (
	request,
	render_template,
	url_for,
	redirect,
	flash,
	abort
)

from flask_login import (
	login_required,
	current_user
)

from .validators import Validators

from app.models import (
	User,
	Article,
	UsersWhichViewedPost,
	Comment
)

from app.logg.logger import logger

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
				# an instance of the class that creates the new article
				article = Article(title=title, intro=intro,
								  text=text, author_name=current_user.username,
								  user_id=current_user.id)
				try:
					db.session.add(article)
					db.session.commit()
					logger.info(f'User {current_user.username} created article {title}')
					return redirect('/posts/page/1')
				except Exception as e:
					logger.error(f"""When user {current_user.username} tried create article an error occurred.
									 Error: {e}""")
					flash("Error. Сould not create article.")
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
	article = Article.query.get_or_404(article_id)

	# checking if founder user of this article or user is admin
	if validator.check_article_or_comment_of_the_owner(article.user_id):

		if request.method == 'POST':

			if (validator.check_length(max_length_title, request.form.get('title')) and
					validator.check_length(max_length_intro, request.form.get('intro'))):

				if (validator.check_length(MIN_LENGTH_TEXT, request.form.get('text'), True) and
						validator.check_length(MAX_LENGTH_TEXT, request.form.get('text'))):

					# note new data.
					article.title = request.form['title']
					article.intro = request.form['intro']
					article.text = request.form['text']

					try:
						# Saving changes
						db.session.commit()
						logger.info(f'User {current_user.username} success update article_id: {article.id}')
						flash('Статья была успешно обновлена.')
						return redirect('/posts/page/1')

					except Exception as e:
						logger.error(f"""When user {current_user.username} tried update article an error occurred.
										 Error: {e}""")
						flash(f'Не удалось обновить статью. Ошибка: {e}')
						return redirect(f'/posts/page/1')
				else:
					flash(f"""Длинна текста должна быть от {MIN_LENGTH_TEXT} до 
						   {MAX_LENGTH_TEXT} символов.""")
					return redirect(f'/posts/{article_id}/update')
			else:
				flash(f"""Максимальная длинна <title> {max_length_title}
					   Максимальная длинна <intro> {max_length_intro}""")
				return redirect(f'/posts/{article_id}/update')

		return render_template('update_post.html', article=article)

	else:
		logger.warning(f'User {current_user.username} \
         				wanted update article. But he does not admin or moderator, or founder')
		abort(403)


@main.route('/posts/<int:article_id>/delete')
@login_required
def delete_post_user(article_id):
	# Search needed article or 404
	article = Article.query.get_or_404(article_id)
	name = article.author_name
	# if current_user.id == article.user_id or user is admin we deleting article.
	if validator.check_article_or_comment_of_the_owner(article.user_id):
		try:
			db.session.delete(article)
			db.session.commit()
			logger.info(f'User {current_user.username} success delete user article with id: {article.id}')
			flash(f'Статья человека: {name} была успешно удалена.')
			return redirect('/posts/page/1')

		except Exception as e:
			logger.error(f"""When user {current_user.username} tried delete article has an error occurred.
							 Error: {e}""")
			flash(f'Не удалось удалить статью. Ошибка: {e}')
			return redirect('/posts/page/1')
	else:
		logger.warning(f'User {current_user.username} wanted delete article. But he does not admin, or founder')
		abort(403)


@main.route('/post/<int:id>/detail', methods=['get', 'post'])
def post_detail(id):
	article = Article.query.get_or_404(id)

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
	comments_need = article.comments[::-1][search_first_index: search_second_index]

	# if user a note comment to the article
	if request.method == 'POST':
		text = request.form.get('text')

		# search comment like it in database
		check_on_spam = article.comments.filter(Comment.text == text,
												Comment.post_id == id).count()

		if validator.check_length(max_length_comment, text):
			# If comments does not in database we will creating new comment
			if check_on_spam < 2:
				# create object with data
				comment = Comment(text=text, author=current_user.username,
								  user_id=current_user.id, post_id=id)
				# add us object
				db.session.add(comment)
				# save changes
				db.session.commit()
				logger.info(f'User {current_user.username} wrote a comment: {text}')
				return redirect(f'/post/{id}/detail')
			else:
				logger.warning(f"""Comment\' user {current_user.username} does not wrote.
								   Because user will spam.""")
				flash('Коментарий не был записан. Вы флудите или спамите.')
				return redirect(f'/post/{id}/detail')
		else:
			flash('Слишком длинный коментарий. Максимальная длинна 500 символов.')
			return redirect(f'/post/{id}/detail')

	# if user logged in himself account
	elif not current_user.is_anonymous:
		user_viewed = article.users_which_viewed_post.filter(UsersWhichViewedPost.user_id == current_user.id,
															 UsersWhichViewedPost.post_id == id).first()
		# checking if user watched article in past
		if not user_viewed and article.user_id != current_user.id:
			# Added one to count_views.
			article.count_views += 1

			# Added user in database what he saw this article
			viewed_post = UsersWhichViewedPost(user_id=current_user.id,
											   name=current_user.username,
											   post_id=id)
			# Added instance of the class to ours database
			db.session.add(viewed_post)
			# saving changes
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
	articles_need = Article.query.order_by((Article.date.desc() if method_for_sorting == 'date'
											else Article.count_views.desc())) \
											[search_first_index: search_second_index]

	# If User input incorrect page in URL address'
	if page > count_dynamic_pages and count_all_posts != 0 or page == 0:
		flash(f"Page {page} does not exist")
		return redirect(f'/posts/page/1?{method_for_sorting}=True')
	else:
		return render_template('posts.html', articles=articles_need, current_page=page,
							   count_dynamic_pages=count_dynamic_pages,
							   method_sorting=method_for_sorting)


@main.route('/user/posts/<int:page>')
@login_required
def user_posts(page):
	logger.info(f'User {current_user.username} watching himself articles')
	user = db.session.query(User).get(current_user.id)

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
		return redirect('/user/posts/1')
	else:
		return render_template('user_posts.html', current_page=page, articles=articles_need,
							   count_dynamic_pages=count_dynamic_pages)


@main.route('/comment/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user_comment(id):
	comment = Comment.query.get_or_404(id)
	# check if comment belongs user's or current user is_admin
	if validator.check_article_or_comment_of_the_owner(comment.user_id):
		try:
			# deleting comment
			db.session.delete(comment)
			db.session.commit()
			logger.info(f'User {current_user.username} has success delete comment {comment.id}.')
			flash(f'Коментарий человека: {comment.author} был успешно удален.')
			return redirect('/posts/page/1')

		except Exception as e:
			logger.error(f"""When user {current_user.username} was wanted delete comment. 
							 Has an error occurred. Error: {e}""")
			flash(f'При удалении коментария произошла ошибка: {e}')
			return redirect('/posts/page/1')
	else:
		logger.warning(f'User {current_user.username} wanted delete comment. But he does not admin.')
		abort(403)
