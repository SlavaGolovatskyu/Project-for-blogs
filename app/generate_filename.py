import uuid
import os


def random_filename(filename: str) -> str:
	ext = os.path.splitext(filename)[1]
	new_filename = uuid.uuid4().hex + ext
	return new_filename
