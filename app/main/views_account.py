import os
from .. import db
from . import main
from ..logg.logger import logger
from ..models import Avatar, Permission

from flask import (
	render_template,
	url_for,
	redirect,
	request,
	flash,
	g
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
	EditProfileForm
)

from .validators import Validators
from ..user_location.get_location import get_location

from ..decorators import is_auth

from ..db_controll import (
	AddNewData,
	FindData
)

from werkzeug.datastructures import MultiDict
from app.generate_filename import random_filename

add_data = AddNewData()
find_data = FindData()

validator = Validators()


# -----------------All actions with accounts, login, registration, logout----------------


# @main.before_app_request
# def before_request():
# 	if current_user.is_authenticated:
# 		current_user.ping()


@main.route('/logout/', methods=['get'])
@login_required
def logout():
	logout_user()
	flash("You have been logged out.")
	return redirect(url_for('.login'))


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
				login_user(user, remember=form.remember.data)
				return redirect(url_for('.index'))
			return redirect(url_for('.sign_up'))
		else:
			flash("Аккаунт с такой почтой уже существует.")
			return redirect(url_for('.sign_up'))

	return render_template('sign-up.html', form=form)


# ----------------SIGN-IN ACCOUNT------------------------
@main.route('/login/', methods=['post', 'get'])
@is_auth
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = find_data.find_user(email=form.email.data)
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('.index'))
		else:
			flash("Invalid email/password", 'error')
			return redirect(url_for('.login'))

	return render_template('login.html', form=form)


@main.route('/edit-profile/', methods=['post', 'get'])
@login_required
def edit_profile():
	upload_folder = 'app\\static\\users_avatars'
	if request.method == 'GET':
		form = EditProfileForm(formdata=MultiDict({
			'username': f'{current_user.username}',
			'email': f'{current_user.email}',
			'city': f'{current_user.location}',
			'about_me': f'{current_user.about_me}'
		}))
	else:
		form = EditProfileForm()

	if form.validate_on_submit():
		try:
			current_user.username = form.username.data
			current_user.location = form.city.data
			current_user.about_me = form.about_me.data
			email = form.email.data

			if find_data.find_user(email=email) and current_user.email != email:
				flash(f'Аккаунт с почтой {email} уже существует!')
			else:
				current_user.email = email

			if form.image.data:
				try:
					f = form.image.data
					filename = random_filename(f.filename)

					ext = os.path.splitext(filename)[1]

					file_path = os.path.join(
						upload_folder, filename
					)

					if not current_user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES) \
					   and ext == '.gif':
						flash('Извините но gif-анимации доступны только для админов и модераторов.')
					else:

						f.save(file_path)

						# 0 is False, 1 is True
						if not current_user.avatar.count():
							user_avatar = Avatar(src_to_avatar=file_path, filename=filename, user_id=current_user.id)
							db.session.add(user_avatar)
						else:
							os.remove(os.path.join(upload_folder, current_user.avatar[0].filename))
							user_avatar = current_user.avatar[0]
							user_avatar.src_to_avatar = file_path
							user_avatar.filename = filename

				except Exception as e:
					flash('Произошла ошибка. Не удалось загрузить фотографию.')
					logger.error(f'Error: {e}. Image not upload')

			db.session.commit()
			return redirect(url_for('.edit_profile'))

		except Exception as e:
			flash('При сбережении данных случилась ошибка. Пожалуйста повторите позднее.')
			logger.error(f'When app wanna to save data something to wrong. Error: {e}')
			return redirect(url_for('.settings_profile'))

	return render_template('edit_profile.html', form=form)


@main.route('/profile/<int:id>')
def user_profile(id):
	user = find_data.find_user(id)
	return render_template('profile.html', user=user)
