import datetime

from app import db

from flask import (
	flash
)

from .models import (
	User,
	Article,
	Comment,
	UsersWhichViewedPost,
	Role,
	BannedIP
)


class AddNewData:
	@staticmethod
	def add_and_commit_obj(obj, error_msg=None) -> bool:
		try:
			db.session.add(obj)
			db.session.commit()
		except:
			if error_msg is not None:
				flash('Произошла ошибка при добавление данных. Не удалось создать ', error_msg)
			return False
		return True

	def add_new_user(self, *args, **kwargs) -> bool:
		new_user = User(**kwargs)
		new_user.set_password(*args)
		return self.add_and_commit_obj(new_user, 'аккаунт')

	def add_new_article(self, **kwargs) -> bool:
		article = Article(**kwargs)
		return self.add_and_commit_obj(article, 'пост')

	def add_new_comment(self, **kwargs) -> bool:
		comment = Comment(**kwargs)
		return self.add_and_commit_obj(comment, 'коментарий')

	def add_user_which_viewed_post(self, **kwargs) -> bool:
		user_which_viewed_post = UsersWhichViewedPost(**kwargs)
		return self.add_and_commit_obj(user_which_viewed_post)


class DeleteData:
	@staticmethod
	def delete_and_commit_obj(obj, error_msg=None) -> bool:
		try:
			db.session.delete(obj)
			db.session.commit()
		except:
			if error_msg is not None:
				flash('Произошла ошибка при удалении ', error_msg)
			return False
		return True

	def delete_user(self, user) -> bool:
		return self.delete_and_commit_obj(user, 'аккаунта')

	def delete_article(self, article) -> bool:
		return self.delete_and_commit_obj(article, 'поста')

	def delete_comment(self, comment) -> bool:
		return self.delete_and_commit_obj(comment, 'коментария')


class FindData:
	@staticmethod
	def find_user(*args, **kwargs):
		if args:
			return User.query.get_or_404(*args)
		return User.query.filter_by(**kwargs).first()

	@staticmethod
	def find_article(*args, **kwargs):
		if args:
			return Article.query.get_or_404(*args)
		return Article.query.filter_by(**kwargs).first()

	@staticmethod
	def find_comment(*args):
		return Comment.query.get_or_404(*args)

	@staticmethod
	def find_user_which_viewed_post(article, **kwargs):
		return article.users_which_viewed_post.filter_by(**kwargs).first()

	@staticmethod
	def find_role(**kwargs):
		return Role.query.filter_by(**kwargs).first()


class ChangeData:
	def __init__(self):
		self.find_data = FindData()
	
	
	@staticmethod
	def catch_error(obj, keys: dict, **kwargs) -> bool:
		try:
			pass
			# for key in keys.keys():
			# 	keys[key] = kwargs.get(key)
		except:
			flash('Произошла ошибка при обновлении данных')
			return False
		return True


	# def get_data_from_kwargs(self, keys: dict, **kwargs) -> dict:
	# 	for key in keys.keys():
	# 		keys[key] = kwargs.get(key)
	# 	return keys


	@staticmethod
	def article_update_changes(article, **kwargs) -> bool:
		try:
			article.title = kwargs.get('title')
			article.text = kwargs.get('text')
			article.intro = kwargs.get('intro')
			db.session.commit()
		except:
			flash('При обновлении статьи произошла ошибка.')
			return False
		return True