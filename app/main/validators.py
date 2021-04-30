class Validators:
	# IF we want change check we note regime True default False
	def check_length(self, length, word, regime=False) -> bool:
		return len(word) <= length if not regime else length <= len(word)

