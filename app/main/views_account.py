import asyncio
from app import db
from . import main

from flask import (
	render_template,
	url_for,
	redirect,
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
	RegistrationForm
)

from .validators import Validators
from app.models import User
from app.logg.logger import logger
from app.user_location.get_location import get_location

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
def sign_up():
	# check if user login in himself account and if user is admin or no
	if current_user.is_authenticated:
		if current_user.is_administrator():
			return redirect(url_for('.admin'))
		else:
			return redirect(url_for('.user_profile'))

	user = False
	form = RegistrationForm()
	if form.validate_on_submit():
		email = validator.validate_email(form.email.data)
		if not email:
			try:
				person = User(username=form.username.data, email=form.email.data,
							  real_location=get_location('146.120.168.159'))
				person.set_password(form.password.data)
				db.session.add(person)
				db.session.commit()
				user = db.session.query(User).filter(User.email == form.email.data).first()

				logger.info(f'User {user.username} success sign-up.')

				login_user(user, remember=form.remember.data)
				return redirect(url_for('.user_profile'))

			except Exception as e:
				logger.error(f'Failed to register an account. Error: {e}')
				flash(f'Ошибка: {e}. Не удалось зарегистрировать аккаунт.')
				return redirect(url_for('.sign_up'))
		else:
			flash("Аккаунт с такой почтой уже существует.")
			return redirect(url_for('.sign_up'))

	return render_template('sign-up.html', form=form)


# -------------------------------------------------------


# ----------------SIGN-IN ACCOUNT------------------------
@main.route('/login/', methods=['post', 'get'])
def login():
	if current_user.is_authenticated:
		if current_user.is_administrator():
			return redirect(url_for('.admin'))
		else:
			return redirect(url_for('.user_profile'))

	form = LoginForm()
	if form.validate_on_submit():

		user = db.session.query(User).filter(User.email == form.email.data).first()
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember.data)
			logger.info(f'User {current_user.username} success sign-in.')

			if user.is_administrator():
				return redirect(url_for('.admin'))
			else:
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
