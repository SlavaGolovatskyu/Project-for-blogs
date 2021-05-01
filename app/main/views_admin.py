from app import db
from . import main
from math import ceil

from flask import (
	render_template, 
	url_for, 
	redirect, 
	flash, 
	request,
	session
)

from flask_login import (
	login_required,
	current_user
)

from app.models import User, Article
from .forms import SearchNeedPeopleForm


MAX_COUNT_USERS_ON_PAGE = 20


# Created decorator for checking if current user is admin
def user_is_admin(func):
	def wrapper(*args, **kwargs):
		# if user login in hiself account
		if not current_user.is_anonymous:
			# check if user admin
			if current_user.is_admin:
				# if we took arguments
				if kwargs or args:
					return func(kwargs if kwargs else args)
				return func()
			else:
				# This user not an admin!
				flash('You are not an admin!')
				return redirect('/profile/')
		else:
			return redirect(url_for('.index'))
	wrapper.__name__ = func.__name__
	return wrapper


#----------ROUTE ADMIN PANEL'S--------------
@main.route('/admin/')
@login_required
@user_is_admin
def admin():
	return render_template('admin.html')


@main.route('/add-new-admin/<int:page>', methods=['GET', 'POST'])
@login_required
@user_is_admin
def add_new_admin(page):
	form = SearchNeedPeopleForm()

	# if form submit we redirected user with arguments which he provided us
	if form.validate_on_submit():
		return redirect(f'/add-new-admin/1?username={form.username.data}&email={form.email.data}')

	"""
		* Search posts between first_index = page * 10 - 10 
		* to second_index = page * 10
		* for example: if page 1 = first_index = 1, second_index = 10 because page * 10
	"""
	search_first_index = page['page'] * MAX_COUNT_USERS_ON_PAGE - MAX_COUNT_USERS_ON_PAGE
	search_second_index = page['page'] * MAX_COUNT_USERS_ON_PAGE

	username = request.args.get('username', '')
	email = request.args.get('email', '')

	users_need = []

	count_all_user = []

	if username or email or username and email:
		users_need = User.query.filter(User.username.like(f'%{username}%'), 
									   User.email.like(f'%{email}%')).all()
	else:
		users_need = User.query.order_by(User.created_on.desc()).all() 

	count_all_user = len(users_need)

	# Search count pages with help count_all_posts
	count_dynamic_pages = ceil(count_all_user / MAX_COUNT_USERS_ON_PAGE)


	if page['page'] > count_dynamic_pages and count_all_user != 0 or page['page'] == 0:
		page = page['page']
		flash(f'Страницы {page} несуществует.')
		return redirect('/add-new-admin/1')

	return render_template('add_new_admin.html', users=users_need[search_first_index : search_second_index], 
						   form=form, count_dynamic_pages=count_dynamic_pages,
						   current_page = page['page'], 
						   max_users=MAX_COUNT_USERS_ON_PAGE,
						   username=username, email=email)


@main.route('/delete-user/<int:id>/confirm', methods=['get', 'post'])
@login_required
@user_is_admin
def delete_user(id):
	id = id['id']
	user = User.query.get_or_404(id)
	if request.method == 'POST':
		if current_user.lvl_of_admin == 2 and user.lvl_of_admin < 2:
			try:
				db.session.delete(user)
				db.session.commit()
				flash(f'Вы успешно удалили аккаунт: {user.username}')
				return redirect('/add-new-admin/1')

			except Exception as e:
				flash(f'Произошла ошибка: {e}. Не удалось удалить аккаунт')
				return redirect(f'/delete-user/{id}/confirm')
		else:
			flash("""Доступ запрещен. Нужна админка 2 уровня. Или же вы пытаетесь удалить 
				  админа 2 уровня будучи самим админом 2 уровня.""")
			return redirect('/add-new-admin/1')

	return render_template('confirm.html', user=user)


#-----------------------------------------