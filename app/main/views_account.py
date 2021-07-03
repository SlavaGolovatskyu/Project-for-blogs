from datetime import datetime
from .. import db
from . import main
from ..logg.logger import logger

from flask import (
	render_template,
	url_for,
	redirect,
	request,
	flash
)

from flask_login import (
	login_required,
	login_user,
	logout_user,
	current_user
)

from .forms import (
	LoginForm,
	RegistrationForm,
	ChangeUserData
)

from .validators import Validators
from ..user_location.get_location import get_location

from ..decorators import is_auth

from ..db_controll import (
	AddNewData,
	FindData
)

from werkzeug.datastructures import MultiDict

add_data = AddNewData()
find_data = FindData()

validator = Validators()

# -----------------All actions with accounts, login, registration, logout----------------

# -------------LOGOUT FROM ACCOUNT-----------------


@main.route('/logout/', methods=['post', 'get'])
@login_required
def logout():
	# user = find_data.find_user(current_user.id)
	# user.last_seen = datetime.utcnow
	current_user.last_seen = datetime.utcnow()
	db.session.commit()
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

		logger.info(f'user {user.username} & {user.id} id failed sign-in.')
		flash("Invalid email/password", 'error')
		return redirect(url_for('.login'))

	return render_template('login.html', form=form)


@main.route('/settings/', methods=['post', 'get'])
@login_required
def settings_profile():
	if request.method == 'GET':
		form = ChangeUserData(formdata=MultiDict({'username': f'{current_user.username}',
											  	  'email': f'{current_user.email}',
							  					  'city': f'{current_user.location}',
												  'about_me': f'{current_user.about_me}'}))
	else:
		form = ChangeUserData()

	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.location = form.city.data
		current_user.about_me = form.about_me.data
		email = form.email.data
		if find_data.find_user(email=email) and current_user.email != email:
			flash(f'Аккаунт с почтой {email} уже существует!')
		else:
			current_user.email = email
		db.session.commit()
		return redirect(url_for('.settings_profile'))

	return render_template('profile_settings.html',
						   form=form)


@main.route('/profile/', methods=['post', 'get'])
@login_required
def user_profile():
	return render_template('profile.html')


@main.route('/profile/<int:id>')
def check_user_profile(id):
	user = find_data.find_user(id)
	return render_template('other_profiles_users.html', user=user)
