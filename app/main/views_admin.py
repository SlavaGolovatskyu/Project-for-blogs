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
from app.logg.logger import logger


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
				logger.warning(f"""User {current_user.username} tried connected to admin-panel. 
								But he does not an admin""")
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
	logger.info(f'User {current_user.username} success connected to url-admin.')
	return render_template('admin.html')


@main.route('/admin-panel/<int:page>', methods=['GET', 'POST'])
@login_required
@user_is_admin
def admin_panel(page):
	logger.info(f'User {current_user.username} success connected to admin-panel.')
	form = SearchNeedPeopleForm()

	# if form submit we redirected user with arguments which he provided us
	if form.validate_on_submit():
		return redirect(f'/admin-panel/1?username={form.username.data}&email={form.email.data}')

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
		return redirect('/admin-panel/1')

	return render_template('admin_panel.html', users=users_need[search_first_index : search_second_index], 
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
	msg = f'Вы действительно хотите удалить аккаунт: {user.username}?'
	if request.method == 'POST':
		if current_user.lvl_of_admin == 2 and user.lvl_of_admin < 2:
			try:
				db.session.delete(user)
				db.session.commit()
				logger.info(f'User {current_user.username} success delete account: {user.username}.')
				flash(f'Вы успешно удалили аккаунт: {user.username}')
				return redirect('/admin-panel/1')

			except Exception as e:
				logger.error(f'failed to delete account from database. Error: {e}')
				flash(f'Произошла ошибка: {e}. Не удалось удалить аккаунт')
				return redirect(f'/delete-user/{id}/confirm')
		else:
			logger.warning(f'User {current_user.username} tried delete user account but he does not an admin.')
			flash("""Доступ запрещен. Нужна админка 2 уровня. Или же вы пытаетесь удалить 
				  админа 2 уровня будучи самим админом 2 уровня.""")
			return redirect('/admin-panel/1')

	return render_template('confirm.html', user=user, msg=msg)


@main.route('/add-new-admin/<int:id>/confirm', methods=['post', 'get'])
@login_required
@user_is_admin
def add_new_admin(id):
	id = id['id']
	user = User.query.get_or_404(id)
	name = user.username
	msg = f'Вы действительно хотите поставить на админку {name}?'
	if request.method == 'POST':
		if current_user.lvl_of_admin == 2 and user.lvl_of_admin == 0:
			try:
				user.lvl_of_admin = 1
				user.is_admin = True
				db.session.commit()
				logger.info(f'User {current_user.username} success added new admin: {name}')
				flash(f'Вы успешно поставили на админку человека с никнеймом {name}')
				return redirect('/admin-panel/1')
				
			except Exception as e:
				logger.error(f'Error: {e}. Failed to add new admin')
				flash(f'Произошла ошибка: {e}. Не удалось поставить {name} на админку.')
				return redirect('/admin-panel/1')
		else:
			logger.warning(f'User {current_user.username} wanted add admin: {name} but he does not admin.')
			flash("""Нужна админка 2 лвл. Или человек которого
				  вы хотите поставить на админку уже админ.""")
			return redirect('/admin-panel/1')

	return render_template('confirm.html', user=user, msg=msg)


@main.route('/take-admin/<int:id>/confirm', methods=['POST', 'GET'])
@login_required
@user_is_admin
def take_admin_user(id):
	id = id['id']
	user = User.query.get_or_404(id)
	msg = f'Вы действительно хотите снять с админки {user.username}?'
	if request.method == 'POST':
		if current_user.lvl_of_admin == 2 and user.lvl_of_admin == 1:
			try:
				user.is_admin = False
				user.lvl_of_admin = 0
				db.session.commit()
				logger.info(f'ADMIN {current_user.username} success took the admin: {user.username}')
				flash(f'Человек {user.username} был успешно снят с админки.')
				return redirect('/admin-panel/1')

			except Exception as e:
				logger.error(f"""ADMIN {current_user.username} failed took the admin: {user.username}.
								 Error: {e}""")
				flash(f'Ошибка: {e}. Не удалось снять человека с админки.')
				return redirect('/admin-panel/1')

		else:
			logger.warning(f"""User {current_user.username} failed took the admin: {user.username}""")
			flash('Человек которого хотите снять не админ или у вас нехватает прав доступа.')
			return redirect('/admin-panel/1')

	return render_template('confirm.html', msg=msg, user=user)
#-----------------------------------------