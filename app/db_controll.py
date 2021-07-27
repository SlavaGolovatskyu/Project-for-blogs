from app import db

from flask import (
	flash
)

from flask_login import (
	current_user
)

from .models import (
	User,
	Article,
	Comment,
	UsersWhichViewedPost,
	Role,
	Permission
)

from .logg.logger import logger


class AddNewData:
	@staticmethod
	def add_and_commit_obj(obj):
		db.session.add(obj)
		db.session.commit()

	def add_new_user(self, *args, **kwargs) -> bool:
		try:
			new_user = User(**kwargs)
			new_user.set_password(*args)
			self.add_and_commit_obj(new_user)
			return True
		except Exception as e:
			logger.error(f'Account not registered. Error: {e}')
			flash(f'Error: {e}. Account not registered')
			return False

	def add_new_article(self, **kwargs) -> bool:
		try:
			article = Article(**kwargs)
			self.add_and_commit_obj(article)
			logger.info(f'User {current_user.username} created article')
			return True
		except Exception as e:
			logger.error(f"""When user {current_user.username} tried create article an error occurred.
							 Error: {e}""")
			flash(f"Error: {e}. Could not create article.")
			return False

	def add_new_comment(self, **kwargs) -> bool:
		try:
			text, id = kwargs['text'], kwargs['post_id']
			comment = Comment(**kwargs)
			self.add_and_commit_obj(comment)
			logger.info(f'User {current_user.username} wrote a comment: {text} on post_id: {id}')
			return True
		except Exception as e:
			logger.error(f'Comment not created. Error: {e}')
			flash(f'Error: {e}. Comment not created')
			return False

	def add_user_which_viewed_post(self, **kwargs) -> bool:
		try:
			user_which_viewed_post = UsersWhichViewedPost(**kwargs)
			self.add_and_commit_obj(user_which_viewed_post)
			return True
		except Exception as e:
			logger.error(f'Something to wrong when app tried add user which viewed post. Error: {e}')
			return False


class DeleteData:
	@staticmethod
	def delete_and_commit_obj(obj):
		db.session.delete(obj)
		db.session.commit()

	def delete_user(self, user) -> bool:
		try:
			self.delete_and_commit_obj(user)
			logger.info(f'User {current_user.username} success delete account: {user.username}.')
			flash(f'Вы успешно удалили аккаунт: {user.username}')
			return True
		except Exception as e:
			logger.error(f'failed to delete account from database. Error: {e}')
			flash(f'Произошла ошибка: {e}. Не удалось удалить аккаунт')
			return False

	def delete_article(self, article) -> bool:
		try:
			self.delete_and_commit_obj(article)
			logger.info(f'User {current_user.username} success delete user article with id: {article.id}')
			flash(f'Статья человека: {article.author_name} была успешно удалена.')
			return True
		except Exception as e:
			logger.error(f"An error occurred while trying to delete the article. Error: {e}.")
			flash(f'Случилась ошибка при удалении поста. Ошибка: {e}')
			return False

	def delete_comment(self, comment) -> bool:
		try:
			self.delete_and_commit_obj(comment)
			logger.info(f'User {current_user.username} has success delete comment {comment.id}.')
			flash(f'Коментарий человека: {comment.author} был успешно удален.')
			return True
		except Exception as e:
			logger.error(f"""When user {current_user.username} was wanted delete comment. 
										 Has an error occurred. Error: {e}""")
			flash(f'При удалении коментария произошла ошибка: {e}')
			return False


class FindData:
	@staticmethod
	def find_articles_order_by(method_sort, f_index, s_index):
		if method_sort == 'date':
			return Article.query.order_by(Article.date.desc()).all()[f_index : s_index]
		elif method_sort == 'views':
			return Article.query.order_by(Article.count_views.desc()).all()[f_index : s_index]

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
		# if we want will to check how much there are comments we wrote count=True else False
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
	def article_update_changes(article, **kwargs) -> bool:
		try:
			article.title = kwargs['title']
			article.text = kwargs['text']
			article.intro = kwargs['intro']
			db.session.commit()
			logger.info(f'User {current_user.username} success update article_id: {article.id}')
			flash('Статья была успешно обновлена.')
			return True
		except Exception as e:
			logger.error(f"""When user {current_user.username} tried update article an error occurred.
							 Error: {e}""")
			flash(f'Не удалось обновить статью. Ошибка: {e}')
			return False
