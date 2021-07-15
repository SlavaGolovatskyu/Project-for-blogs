from functools import wraps
from flask import g, session
from .errors import forbidden, unauthorized
from ..models import User


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if 'email' in session:
				email = session.get('email')
				user = User.query.filter_by(email=email).first()
				if user:
					g.current_user = user
				else:
					return forbidden('not found user')
				if not g.current_user.can(permission):
					return forbidden('Insufficient permissions')
				return f(*args, **kwargs)
			return unauthorized('unauthorized account')
		return decorated_function
	return decorator
