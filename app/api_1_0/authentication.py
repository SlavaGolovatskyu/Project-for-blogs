from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if email == '':
        return False
    if password == '':
        return False
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        return False
    g.current_user = user
    return user.check_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if g.current_user.is_anonymous:
        return unauthorized('unauthorized account')