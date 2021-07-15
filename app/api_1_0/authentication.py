from flask import g, jsonify, session
from flask_httpauth import HTTPBasicAuth
from ..models import User
from .errors import unauthorized

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password) -> bool:
	if not email or not password:
		return False
	user = User.query.filter_by(email=email).first()
	if not user:
		return False
	g.current_user = user
	if 'email' not in session:
		session['email'] = email
	return user.check_password(password)


@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')
