from . import main
from math import ceil

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

from .forms import SearchNeedPeopleForm
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


@main.route('/add-new-moderator/<int:id>/confirm', methods=['post', 'get'])
@login_required
@admin_required
def give_moderator(id):
	user = find_data.find_user(id)
	name = user.username
	msg = f'Вы действительно хотите поставить на модератора {name}?'
	if request.method == 'POST':
		if not user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES):
			# if you see how made func change_user_role you will see what i'm using **kwargs
			# that is why we must specify the data in the format name=name or for example
			# role_id=id first name will must the same with models data
			if change_data.change_user_role(user, name="Moderator"):
				return redirect(url_for('.admin_panel', page=1))
			return redirect(url_for('.give_moderator', id=id))
		else:
			logger.warning(f'Admin: {current_user.username} tried give moderator user: {name} but \
							 he is still moderator')
			flash(f'Человек: {name} уже модератор!')
			return redirect(url_for('.admin_panel', page=1))
	return render_template('confirm.html', user=user, msg=msg)


@main.route('/pick-up-moderator/<int:id>/confirm', methods=['POST', 'GET'])
@login_required
@admin_required
def pick_up_the_moderator(id):
	user = find_data.find_user(id)
	msg = f'Вы действительно хотите снять с админки {user.username}?'
	if request.method == 'POST':
		if user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES) and not user.is_administrator():
			# if you see how made func change_user_role you will see what i'm using **kwargs
			# that is why we must specify the data in the format name=name or for example
			# role_id=id first name will must the same with models data
			if change_data.change_user_role(user, name="User"):
				return redirect(url_for('.admin_panel', page=1))
			return redirect(url_for('.pick_up_the_moderator', id=id))
		else:
			flash(f'Человек: {user.username} не модератор!')
			logger.warning(f'Admin: {current_user.username} tried pick up moderator user: {user.username}')
			return redirect(url_for('.admin_panel', page=1))
	return render_template('confirm.html', msg=msg, user=user)
# -----------------------------------------
