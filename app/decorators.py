from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user
from .models import Permission


def is_auth(f):
	@wraps(f)
	def decorate_func(*args, **kwargs):
		if current_user.is_authenticated:
			return redirect(url_for('.index'))
		return f(*args, **kwargs)
	return decorate_func


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorate_function(*args, **kwargs):
			if not current_user.can(permission):
				return abort(403)
			return f(*args, **kwargs)
		return decorate_function
	return decorator


def admin_required(f):
	return permission_required(Permission.ADMINISTRATOR)(f)
