from functools import wraps
from flask import g, session
from .errors import forbidden, unauthorized
from ..models import User


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
			return f(*args, **kwargs)
		return decorated_function
	return decorator
