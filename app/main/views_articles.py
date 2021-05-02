from app import db
from . import main
from math import ceil

from flask import (
	request,
	render_template, 
	url_for, 
	redirect, 
	flash, 
	session
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
		if (validator.check_length(max_length_title, request.form.get('title')) and 
			validator.check_length(max_length_intro, request.form.get('intro'))):

			if (validator.check_length(MIN_LENGTH_TEXT, request.form.get('text'), True) and 
				validator.check_length(MAX_LENGTH_TEXT, request.form.get('text'))):
				# an instance of the class that creates the new article
				article = Article(title=request.form.get('title'), intro=request.form.get('intro'), 
								  text=request.form.get('text'), author_name=current_user.username,
								  user_id=current_user.id)
				try:
					db.session.add(article)
					db.session.commit()
					return redirect('/posts/page/1')
				except:
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
	if current_user.id == article.user_id or current_user.is_admin:

		if request.method == 'POST':

			if (validator.check_length(max_length_title, request.form.get('title')) and 
				validator.check_length(max_length_intro, request.form.get('intro'))):

				if (validator.check_length(MIN_LENGTH_TEXT, request.form.get('text'), True) and 
					validator.check_length(MAX_LENGTH_TEXT, request.form.get('text'))):

					# Saving new data.
					article.title = request.form['title']
					article.intro = request.form['intro']
					article.text = request.form['text']

					try:
						# Saving changes
						db.session.commit()
						flash('Статья была успешно обновлена.')
						return redirect('/posts/page/1')
								
					except Exception as e:
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
		return redirect('/posts/page/1')


@main.route('/posts/<int:article_id>/delete')
@login_required
def delete_post_user(article_id):
	# Search needed article or 404
	article = Article.query.get_or_404(article_id)
	name = article.author_name
	# if current_user.id == article.user_id or user is admin we deleting article.
	if current_user.id == article.user_id or current_user.is_admin:
		try:
			db.session.delete(article)
			db.session.commit()
			flash('Ваша статья была успешно удалена.' if not current_user.is_admin else
				  f'Статья человека: {name}, была успешно удалена.')
			return redirect('/posts/page/1')

		except Exception as e:
			flash(f'Не удалось удалить статью. Ошибка: {e}')
			return redirect('/posts/page/1')
	else:
		return redirect('/posts/page/1')


@main.route('/post/<int:id>/detail', methods=['get', 'post'])
def post_detail(id):
	article = Article.query.get_or_404(id)

	count_comments_on_article = article.comments.count()


	CURRENT_COUNT_COMMENTS_ON_PAGE = 15

	# if user will want upload more comments each time flask upload + 10 comment to current_count
	CONST_COUNT = 15

	page = 1

	try:
		data = request.args.get('count', '')
		if data and data.isdigit():
			CURRENT_COUNT_COMMENTS_ON_PAGE = int(request.args.get('count', ''))

	except Exception as e:
		flash(f'Ошибка: {e}')
		return redirect(f'/post/{id}/detail')

	search_first_index = page * CURRENT_COUNT_COMMENTS_ON_PAGE - CURRENT_COUNT_COMMENTS_ON_PAGE
	search_second_index = page * CURRENT_COUNT_COMMENTS_ON_PAGE


	comments_need = article.comments[::-1][search_first_index : search_second_index]

	# if user a note comment to the article
	if request.method == 'POST':
		text = request.form.get('text')

		check_on_spam = Comment.query.filter(Comment.text == text,
											 Comment.post_id == id).count()


		if validator.check_length(max_length_comment, text):
			if check_on_spam < 2:
				comment = Comment(text=text, author=current_user.username,
								  author_id=current_user.id, 
								  user_id=current_user.id, post_id=id)
				db.session.add(comment)
				db.session.commit()
				return redirect(f'/post/{id}/detail')
			else:
				flash('Коментарий не был записан. Вы флудите или спамите.')
				return redirect(f'/post/{id}/detail')
		else:
			flash('Слишком длинный коментарий. Максимальная длинна 500 символов.')
			return redirect(f'/post/{id}/detail')

	# if user loged in hiself account
	elif not current_user.is_anonymous:
		user_viewed = UsersWhichViewedPost.query.filter(UsersWhichViewedPost.user_id == current_user.id,
														UsersWhichViewedPost.post_id == id).first()
		# checking if user watched article in past
		if not user_viewed and article.user_id != current_user.id:
			# Added one to count_views.
			article.count_views += 1

			# Added user in database what he saw this article
			viewed_post = UsersWhichViewedPost(user_id=current_user.id,
											   name=current_user.username,
											   post_id=id)
			# Added instance of the class to our's database
			db.session.add(viewed_post)
			# saving changes
			db.session.commit()

	return render_template('post_detail.html', article=article, comments=comments_need,
							count_comments=CURRENT_COUNT_COMMENTS_ON_PAGE, post_id=id,
							const_count=CONST_COUNT)


@main.route('/posts/page/<int:page>')
def posts(page):
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
	articles_need = Article.query.order_by( 
					(Article.date.desc() if method_for_sorting == 'date'
					else Article.count_views.desc())) \
					[search_first_index : search_second_index]

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
	articles_need = user.posts[::-1][search_first_index : search_second_index]
 
	# If User input incorrect page in URL address'
	if (page > count_dynamic_pages and all_posts_user != 0 or page == 0):
		flash(f"Page {page} does not exist")
		return redirect('/user/posts/1')
	else:
		return render_template('user_posts.html', current_page=page, articles=articles_need,
							   count_dynamic_pages=count_dynamic_pages)


@main.route('/comment/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user_comment(id):
	comment = Comment.query.get_or_404(id)
	if current_user.id == comment.author_id or current_user.is_admin:
		try:
			db.session.delete(comment)
			db.session.commit()
			flash('Ваш коментарий был успешно удален.' if not current_user.is_admin
				  else f'Коментарий {comment.author} был успешно удален.')
			return redirect('/posts/page/1')
		except Exception as e:
			flash(f'При удалении коментария произошла ошибка: {e}')
			return redirect('/posts/page/1')
	else:
		flash('Нет доступа.')
		return redirect('/posts/page/1')