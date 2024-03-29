import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
	SECRET_KEY = "Gijujgf43jk5o49g0.!fdgf44GhgdIKYUJMC4%1рараgf/.!314ckdxcDGJ,LJN"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SEND_FILE_MAX_AGE_DEFAULT = 0


class DevelopmentConfig(BaseConfig):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or \
							  'postgresql://postgres:1414@127.0.0.1/blogs'


class TestingConfig(BaseConfig):
	DEBUG = True
	WTF_CSRF_ENABLE = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or \
							  'sqlite:///test.db'


class ProductionConfig(BaseConfig):
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or \
							  'sqlite:///blog.db'
