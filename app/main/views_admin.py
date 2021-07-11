from . import main
from app import db

from flask import (
	render_template,
	request,
	url_for,
	redirect,
	flash,
	abort
)

from flask_login import (
	login_required,
	current_user
)

from ..models import (
	User,
	Permission,
	Role
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
def admin_panel(page: int = 1):
	logger.info(f'User {current_user.username} success connected to admin-panel.')
	form = SearchNeedPeopleForm()

	# if form submit we redirected user with arguments which he provided us
	if form.validate_on_submit():
		return redirect(f'/admin-panel/1?username={form.username.data}&email={form.email.data}')

	username = request.args.get('username', '')
	email = request.args.get('email', '')

	if not username and not email:
		pagination = User.query.order_by(User.created_on.desc()).paginate(
			page, per_page=MAX_COUNT_USERS_ON_PAGE,
			error_out=False
		)
	else:
		pagination = User.query.filter(User.username.like(f'%{username}%'),
									   User.email.like(f'%{email}%')).paginate(
			page, per_page=MAX_COUNT_USERS_ON_PAGE
		)

	users = pagination.items

	return render_template('admin_panel.html', users=users,
						   form=form,
						   max_users=MAX_COUNT_USERS_ON_PAGE,
						   username=username, email=email,
						   pagination=pagination)


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

	return render_template('confirm.html', id=user.id, msg=msg)


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
		role_id = form.role.data

		if role_id != Role.query.filter_by(name='Administrator').first().id:
			user.role_id = role_id
		else:
			flash('Вы не можете выдать роль администратора!')
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
