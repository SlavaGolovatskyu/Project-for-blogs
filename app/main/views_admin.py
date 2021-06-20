from app import db
from . import main
from math import ceil

from flask import (
	render_template,
	redirect,
	flash,
	request
)

from flask_login import (
	login_required,
	current_user
)

from app.models import (
	User,
	Permission,
	Role
)

from .forms import SearchNeedPeopleForm
from app.logg.logger import logger
from app.decorators import (
	admin_required
)

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

	users_need = []

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
		return redirect('/admin-panel/1')

	return render_template('admin_panel.html', users=users_need[search_first_index: search_second_index],
						   form=form, count_dynamic_pages=count_dynamic_pages,
						   current_page=page,
						   max_users=MAX_COUNT_USERS_ON_PAGE,
						   username=username, email=email)


@main.route('/delete-user/<int:id>/confirm', methods=['get', 'post'])
@login_required
@admin_required
def delete_user(id):
	user = User.query.get_or_404(id)
	msg = f'Вы действительно хотите удалить аккаунт: {user.username}?'
	if request.method == 'POST':
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

	return render_template('confirm.html', user=user, msg=msg)


@main.route('/add-new-moderator/<int:id>/confirm', methods=['post', 'get'])
@login_required
@admin_required
def give_moderator(id):
	user = User.query.get_or_404(id)
	name = user.username
	msg = f'Вы действительно хотите поставить на модератора {name}?'
	if request.method == 'POST':
		if not user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES):
			try:
				user.role_id = Role.query.filter(Role.name=='Moderator').first().id
				db.session.commit()
				logger.info(f'User {current_user.username} success added new moderator: {name}')
				flash(f'Вы успешно поставили на модератора человека с никнеймом {name}')
				return redirect('/admin-panel/1')

			except Exception as e:
				logger.error(f'Error: {e}. Failed to add new moderator')
				flash(f'Произошла ошибка: {e}. Не удалось поставить {name} на админку.')
				return redirect('/admin-panel/1')
		else:
			logger.warning(f'Admin: {current_user.username} tried give moderator user: {name} but \
							 he is still moderator')
			flash(f'Человек: {name} уже модератор!')
			return redirect('/admin-panel/1')
	return render_template('confirm.html', user=user, msg=msg)


@main.route('/pick-up-moderator/<int:id>/confirm', methods=['POST', 'GET'])
@login_required
@admin_required
def pick_up_the_moderator(id):
	user = User.query.get_or_404(id)
	msg = f'Вы действительно хотите снять с админки {user.username}?'
	if request.method == 'POST':
		if user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES) and not user.is_administrator():
			try:
				user.role_id = Role.query.filter_by(default=True).first().id
				db.session.commit()
				logger.info(f'ADMIN {current_user.username} success took the moderator: {user.username}')
				flash(f'Человек {user.username} был успешно снят с админки.')
				return redirect('/admin-panel/1')

			except Exception as e:
				logger.error(f"""ADMIN {current_user.username} failed took the moderator: {user.username}.
								 Error: {e}""")
				flash(f'Ошибка: {e}. Не удалось снять человека с модераторки.')
				return redirect('/admin-panel/1')
		else:
			flash(f'Человек: {user.username} не модератор!')
			logger.warning(f'Admin: {current_user.username} tried pick up moderator user: {user.username}')
			return redirect('/admin-panel/1')
	return render_template('confirm.html', msg=msg, user=user)
# -----------------------------------------
