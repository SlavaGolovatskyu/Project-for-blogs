import os, json

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = "Gijujgf43jk5o49g0.!fdgf44GhgdIKYUJMC4%gf/.!314ckdxcDGJ,LJN"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or \
                              'postgresql://postgres:1414@127.0.0.1/blogs'


class TestingConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or \
                              'postgresql://postgres:1414@127.0.0.1/blogs'


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI') or \
                              'postgresql://postgres:1414@127.0.0.1/blogs'
