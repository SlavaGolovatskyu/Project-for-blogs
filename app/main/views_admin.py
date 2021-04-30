from app import db
from . import main
from math import ceil

from flask import (
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

from app.models import User, Article


MAX_COUNT_USERS_ON_PAGE = 20


# Created decorator for checking if current user is admin
def user_is_admin(func):
	def wrapper(*args, **kwargs):
		if not current_user.is_anonymous:
			if current_user.is_admin:
				if kwargs or args:
					return func(kwargs if kwargs else args)
				return func()
			else:
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


@main.route('/add-new-admin/<int:page>')
@login_required
@user_is_admin
def add_new_admin(page):
	count_all_user = User.query.count()

	# Search count pages with help count_all_posts
	count_dynamic_pages = ceil(count_all_user / MAX_COUNT_USERS_ON_PAGE)

	"""
		* Search posts between first_index = page * 10 - 10 
		* to second_index = page * 10
		* for example: if page 1 = first_index = 1, second_index = 10 because page * 10
	"""
	search_first_index = page['page'] * MAX_COUNT_USERS_ON_PAGE - MAX_COUNT_USERS_ON_PAGE
	search_second_index = page['page'] * MAX_COUNT_USERS_ON_PAGE

	users_need = User.query.order_by(User.created_on.desc()) \
				 [search_first_index : search_second_index]

	return render_template('add_new_admin.html', users=users_need)


#-----------------------------------------