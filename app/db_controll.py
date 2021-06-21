from app import db

from flask import (
	redirect,
	flash,
	url_for
)

from .models import (
	User,
	Article,
	Comment,
	UsersWhichViewedPost
)

from .logg.logger import logger


class AddNewData:
	@staticmethod
	def add_new_user(*args, **kwargs):
		try:
			new_user = User(**kwargs)
			new_user.set_password(*args)
			db.session.add(new_user)
			db.session.commit()
		except Exception as e:
			logger.error(f'Account not registered. Error: {e}')
			flash(f'Error: {e}. Account not registered')
			return redirect(url_for('.sign_up'))

