from . import main
from math import ceil
from app import db

from flask import (
	render_template,
	request,
	url_for,
	redirect,
	flash
)

from flask_login import (
	login_required,
	current_user
)

from ..models import (
	User,
	Permission
)

from .forms import (
	SearchNeedPeopleForm,
	EditProfileAdminForm
)

from werkzeug.datastructures import MultiDict

from app.decorators import (
	admin_required
)

from ..logg.logger import logger

from ..db_controll import (
	DeleteData,
	FindData,
	ChangeData
)

from .validators import Validators

find_data = FindData()
delete_data = DeleteData()
change_data = ChangeData()


MAX_COUNT_USERS_ON_PAGE = 20


# ----------ROUTE ADMIN PANEL'S--------------
@main.route('/admin/')
@login_required
@admin_required
def admin():
	logger.info(f'User {current_user.username} success connected to url-admin.')
	return render_template('admin.html')


@main.route('/admin-panel/<int:page>', methods=['GET', 'POST'])
@login_required
@admin_required
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
	search_first_index = page * MAX_COUNT_USERS_ON_PAGE - MAX_COUNT_USERS_ON_PAGE
	search_second_index = page * MAX_COUNT_USERS_ON_PAGE

	username = request.args.get('username', '')
	email = request.args.get('email', '')

	if username or email or username and email:
		users_need = User.query.filter(User.username.like(f'%{username}%'),
									   User.email.like(f'%{email}%')).all()
	else:
		users_need = User.query.order_by(User.created_on.desc()).all()

	count_all_user = len(users_need)

	# Search count pages with help count_all_posts
	count_dynamic_pages = ceil(count_all_user / MAX_COUNT_USERS_ON_PAGE)

	if page > count_dynamic_pages and count_all_user != 0 or page == 0:
		flash(f'Страницы {page} несуществует.')
		return redirect(url_for('.admin_panel', page=1))

	return render_template('admin_panel.html', users=users_need[search_first_index: search_second_index],
						   form=form, count_dynamic_pages=count_dynamic_pages,
						   current_page=page,
						   max_users=MAX_COUNT_USERS_ON_PAGE,
						   username=username, email=email)


@main.route('/delete-user/<int:id>/confirm', methods=['get', 'post'])
@login_required
@admin_required
def delete_user(id):
	user = find_data.find_user(id)
	msg = f'Вы действительно хотите удалить аккаунт: {user.username}?'
	if request.method == 'POST':
		if not user.is_administrator():
			if delete_data.delete_user(user):
				return redirect(url_for('.admin_panel', page=1))
			return redirect(url_for('.delete_user', id=id))
		else:
			flash(f'Человек: {user.username} админ!')
			logger.warning(f'Admin: {current_user.username} tried delete user: {user.username}')
			return redirect(url_for('.delete_user', id=id))

	return render_template('confirm.html', user=user, msg=msg)


@main.route('/edit-profile/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	if request.method == 'GET':
		form = EditProfileAdminForm(formdata=MultiDict({
			'email': f'{user.email}',
			'username': f'{user.username}',
			'role': f'{user.role_id}',
			'location': f'{user.location}',
			'about_me': f'{user.about_me}'
		}))
	else:
		form = EditProfileAdminForm()

	if form.validate_on_submit():
		user.role_id = form.role.data
		user.username = form.username.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		email = form.email.data
		if find_data.find_user(email=email) and user.email != email:
			flash(f'Аккаунт с почтой {email} уже существует!')
		else:
			user.email = email

		db.session.commit()
		return redirect(url_for('.edit_profile_admin', id=id))

	return render_template('edit_profile_admin.html',
						   form=form, user=user)
# -----------------------------------------
