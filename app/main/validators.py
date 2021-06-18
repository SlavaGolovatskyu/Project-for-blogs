from app.models import User


class Validators:
	# IF we want change check we note regime True default False
	def check_length(self, length, word, regime: bool = False) -> bool:
		return len(word) <= length if not regime else length <= len(word)
	
	def validate_email(self, field: str) -> bool:
		return User.query.filter(User.email==field).first()

	def validate_username(self, field: str) -> bool:
		return User.query.filter(User.username == field).first()



