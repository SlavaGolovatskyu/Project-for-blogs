from app.models import User


class Validators:
	# IF we want change check we note regime True default False
	@staticmethod
	def check_length(length, word, regime: bool = False) -> bool:
		return len(word) <= length if not regime else length <= len(word)

	@staticmethod
	def validate_email(field: str) -> bool:
		return User.query.filter(User.email==field).first()

	@staticmethod
	def validate_username(field: str) -> bool:
		return User.query.filter(User.username == field).first()



