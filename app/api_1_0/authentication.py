from flask_httpauth import HTTPBasicAuth
from flask_login import login_user
from ..models import User
from .errors import unauthorized
from . import api


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password) -> bool:
	if not email or not password:
		return False
	user = User.query.filter_by(email=email).first()
	if user is None:
		return False
	if user.check_password(password):
		return user
	else:
		return False


@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')