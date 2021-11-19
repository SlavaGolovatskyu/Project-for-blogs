import os
from .. import db
from . import main

from ..models import (
	Avatar, 
	Permission, 
	User,
	BannedIP
)

from flask import (
	render_template,
	url_for,
	redirect,
	request,
	flash,
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


@main.before_app_request
def before_request():
	headers_list = request.headers.getlist("X-Forwarded-For")
	ip = headers_list[0] if headers_list else request.remote_addr

	ip_is_banned = BannedIP.query.filter_by(ip=ip).first()

	if ip_is_banned or (current_user.is_authenticated and current_user.is_banned):
		user = User.query.get_or_404(ip_is_banned.user_id if ip_is_banned else current_user.id)
		if user.check_auto_unban():
			return redirect(url_for('.index'))
		else:
			return render_template('info_about_ban.html', user=user)
	else:
		if current_user.is_authenticated:
			current_user.ping()


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
		headers_list = request.headers.getlist("X-Forwarded-For")
		ip = headers_list[0] if headers_list else request.remote_addr
		if not email:
			if add_data.add_new_user(form.password.data,
									 username=form.username.data,
									 email=form.email.data,
									 ip=ip,
									 real_location=get_location(ip)):
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
			new_password = form.new_pass.data

			if new_password:
				if current_user.check_password(new_password):
					flash('Вы указали старый пароль')
				else:
					current_user.set_password(new_password)
					flash('Вы успешно изменили пароль')

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

			db.session.commit()
			return redirect(url_for('.edit_profile'))

		except Exception as e:
			flash('При сбережении данных случилась ошибка. Пожалуйста повторите позднее.')
			return redirect(url_for('.settings_profile'))

	return render_template('edit_profile.html', form=form)


@main.route('/profile/<int:id>')
def user_profile(id):
	user = find_data.find_user(id)
	return render_template('profile.html', user=user)
