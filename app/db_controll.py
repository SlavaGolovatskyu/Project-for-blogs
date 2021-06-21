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
	def add_and_commit_obj(obj):
		db.session.add(obj)
		db.session.commit()

	def add_new_user(self, *args, **kwargs):
		try:
			new_user = User(**kwargs)
			new_user.set_password(*args)
			self.add_and_commit_obj(new_user)
		except Exception as e:
			logger.error(f'Account not registered. Error: {e}')
			flash(f'Error: {e}. Account not registered')
			return redirect(url_for('.sign_up'))

	def add_new_article(self, **kwargs):
		try:
			article = Article(**kwargs)
			self.add_and_commit_obj(article)
			return redirect(url_for('.posts', page=1))
		except Exception as e:
			logger.error(f'Article not created. Error: {e}')
			flash(f'Error: {e}. Article not created')
			return redirect(url_for('.create_article'))

	def add_new_comment(self, **kwargs):
		try:
			comment = Comment(**kwargs)
			self.add_and_commit_obj(comment)
		except Exception as e:
			logger.error(f'Comment not created. Error: {e}')
			flash(f'Error: {e}. Comment not created')
		finally:
			return redirect(url_for('.post_detail', id=kwargs['post_id']))
