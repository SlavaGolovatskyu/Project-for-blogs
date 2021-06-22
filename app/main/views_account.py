from . import main

from flask import (
	render_template,
	url_for,
	redirect,
)

from flask_login import (
	login_required,
	login_user,
	logout_user
)

from .forms import (
	LoginForm,
	RegistrationForm
)

from .validators import Validators
from ..user_location.get_location import get_location

from ..db_controll import *
from ..decorators import is_auth

from ..db_controll import (
	AddNewData,
	FindData
)

add_data = AddNewData()
find_data = FindData()

validator = Validators()

# -----------------All actions with accounts, login, registration, logout----------------

# -------------LOGOUT FROM ACCOUNT-----------------


@main.route('/logout/', methods=['post', 'get'])
@login_required
def logout():
	logger.info(f'User {current_user.username} have been logged out.')
	logout_user()
	flash("You have been logged out.")
	return redirect(url_for('.login'))


# ----------------SIGN-UP ACCOUNT-----------------------
@main.route('/sign-up/', methods=['post', 'get'])
@is_auth
def sign_up():
	form = RegistrationForm()
	if form.validate_on_submit():
		email = validator.validate_email(form.email.data)
		if not email:
			if add_data.add_new_user(form.password.data,
									 username=form.username.data,
									 email=form.email.data,
									 real_location=get_location('146.120.168.159')):

				user = find_data.find_user(email=form.email.data)

				logger.info(f'User {user.username} success sign-up.')

				login_user(user, remember=form.remember.data)
				return redirect(url_for('.user_profile'))
			else:
				return redirect(url_for('.sign_up'))
		else:
			flash("Аккаунт с такой почтой уже существует.")
			return redirect(url_for('.sign_up'))

	return render_template('sign-up.html', form=form)


# -------------------------------------------------------


# ----------------SIGN-IN ACCOUNT------------------------
@main.route('/login/', methods=['post', 'get'])
@is_auth
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = find_data.find_user(email=form.email.data)
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember.data)
			logger.info(f'User {current_user.username} success sign-in.')
			return redirect(url_for('.user_profile'))

		logger.info(f'Anymouse user failed sign-in.')
		flash("Invalid email/password", 'error')
		return redirect(url_for('.login'))

	return render_template('login.html', form=form)


@main.route('/profile/')
@login_required
def user_profile():
	logger.info(f'User {current_user.username} watching himself profile.')
	user = User.query.get(current_user.id)
	return render_template('profile.html', user=user)
