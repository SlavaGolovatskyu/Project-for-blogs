from app.models import (
	User,
	Permission
)

from flask_login import current_user


class Validators:
	# IF we want change check we note regime True default False
	@staticmethod
	def check_length(length: int, word: str, regime: bool = False) -> bool:
		return len(word) <= length if not regime else length <= len(word)

	@staticmethod
	def validate_email(field: str) -> bool:
		return User.query.filter(User.email == field).first()

	@staticmethod
	def validate_username(field: str) -> bool:
		return User.query.filter(User.username == field).first()

	@staticmethod
	def is_owner(user_id: int) -> bool:
		return (current_user.id == user_id or current_user.is_administrator()
				or current_user.can(Permission.MODERATE_COMMENTS_AND_ARTICLES))



