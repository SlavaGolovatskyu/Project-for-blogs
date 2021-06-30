from app import db, login_manager
from datetime import datetime

from .logg.logger import logger

from flask_login import (
	UserMixin,
	AnonymousUserMixin
)

from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
	return db.session.query(User).get(user_id)


class Permission:
	USUAL_USER = 4
	MODERATE_COMMENTS_AND_ARTICLES = 8
	ADMINISTRATOR = 16


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer(), primary_key=True)
	username = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password_hash = db.Column(db.String(100), nullable=False)
	role_id = db.Column(db.Integer)
	location = db.Column(db.String(64), nullable=True)
	real_location = db.Column(db.JSON)
	about_me = db.Column(db.Text, nullable=True)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

	comments = db.relationship('Comment', cascade='all,delete-orphan', lazy='dynamic')
	posts = db.relationship('Article', cascade='all,delete-orphan', lazy='dynamic')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role_id is None:
			try:
				if self.email == 'slavik.golovatskyu@gmail.com':
					self.role_id = Role.query.filter_by(name='Administrator').first().id
				if self.role_id is None:
					self.role_id = Role.query.filter_by(default=True).first().id
			except AttributeError:
				logger.error('При создании аккаунта произошла ошибка. Роль не была найдена.')
				self.role_id = 1

	def get_role(self):
		return Role.query.filter_by(id=self.role_id).first()

	def can(self, permissions) -> bool:
		r = self.get_role()
		return self.role_id is not None and \
			   (r.permissions & permissions) == permissions

	def is_administrator(self) -> bool:
		return self.can(Permission.ADMINISTRATOR)

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return "<Account %r>" % self.id


class AnonymousUser(AnonymousUserMixin):
	@staticmethod
	def can():
		return False

	@staticmethod
	def is_administrator():
		return False


login_manager.anonymous_user = AnonymousUser


class Article(db.Model):
	__tablename__ = "articles"
	id = db.Column(db.Integer(), primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	intro = db.Column(db.String(300), nullable=False)
	text = db.Column(db.Text, nullable=False)
	author_name = db.Column(db.String(50), nullable=False)
	count_views = db.Column(db.Integer(), default=0)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

	comments = db.relationship('Comment', backref='comments', cascade='all,delete-orphan', lazy='dynamic')
	users_which_viewed_post = db.relationship('UsersWhichViewedPost', backref='user_which_viewed_post',
											  cascade='all,delete-orphan', lazy='dynamic')

	def __repr__(self):
		return "<Article %r>" % self.id


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer(), primary_key=True)
	text = db.Column(db.String(500), nullable=False)
	author = db.Column(db.String(50), nullable=False)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))

	def __repr__(self):
		return '<comment %r>' % self.id


class UsersWhichViewedPost(db.Model):
	__tablename__ = 'user_which_viewed_post'
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	user_id = db.Column(db.Integer(), nullable=False)

	post_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))

	def __repr__(self):
		return "<UserWhichViewedPost %r>" % self.id


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)

	@staticmethod
	def insert_role():
		roles = {
			'User': (Permission.USUAL_USER, True),
			'Moderator': (Permission.USUAL_USER | Permission.MODERATE_COMMENTS_AND_ARTICLES, False),
			'Administrator': (Permission.USUAL_USER | Permission.MODERATE_COMMENTS_AND_ARTICLES |
							  Permission.ADMINISTRATOR, False)
		}

		for role in roles:
			# Variable will be or None or she will be have list with role
			new_role = Role.query.filter_by(name=role).first()
			if not new_role:
				new_role = Role(name=role)
			new_role.permissions = roles[role][0]
			new_role.default = roles[role][1]
			db.session.add(new_role)
		db.session.commit()

	def __repr__(self):
		return "<Role %r>" % self.id
