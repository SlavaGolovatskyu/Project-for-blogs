from app import db
from . import main

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

# Created decorator for checking if current user is admin
def user_is_admin(func):
	def wrapper():
		if not current_user.is_anonymous:
			if current_user.is_admin:
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


@main.route('/add-new-admin/')
@login_required
@user_is_admin
def add_new_admin():
	return render_template('add_new_admin.html')


#-----------------------------------------