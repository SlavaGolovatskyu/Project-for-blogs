from typing import Dict
from app import db, login_manager
from datetime import datetime

from flask import url_for

from flask_login import (
	UserMixin,
	AnonymousUserMixin
)

from werkzeug.security import generate_password_hash, check_password_hash

from .exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
	return db.session.query(User).get(user_id)


class Permission:
	USUAL_USER = 4
	MODERATE_COMMENTS_AND_ARTICLES = 8
	ADMINISTRATOR = 16


class Avatar(db.Model):
	__tablename__ = 'avatars'
	id = db.Column(db.Integer, primary_key=True)
	src_to_avatar = db.Column(db.String(300), nullable=True)
	filename = db.Column(db.String(300), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer(), primary_key=True, index=True)
	username = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True, index=True)
	password_hash = db.Column(db.String(100), nullable=False)
	role_id = db.Column(db.Integer)
	location = db.Column(db.String(64), nullable=True)
	ip = db.Column(db.String(30), nullable=True)
	real_location = db.Column(db.JSON)
	about_me = db.Column(db.Text, nullable=True)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

	avatar = db.relationship('Avatar', cascade='all,delete-orphan', lazy='dynamic')
	comments = db.relationship('Comment', cascade='all,delete-orphan', lazy='dynamic')
	posts = db.relationship('Article', cascade='all,delete-orphan', lazy='dynamic')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role_id is None:
			try:
				if self.email == 'slavik.golovatskyu@gmail.com':
					self.role_id = Role.query.filter_by(name='Administrator').first().id
				elif self.role_id is None:
					self.role_id = Role.query.filter_by(default=True).first().id
			except AttributeError:
				Role.insert_role()
				if self.email == 'slavik.golovatskyu@gmail.com':
					self.role_id = Role.query.filter_by(name='Administrator').first().id
				elif self.role_id is None:
					self.role_id = Role.query.filter_by(default=True).first().id

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(username=forgery_py.internet.user_name(True),
					 email=forgery_py.internet.email_address(),
					 location=forgery_py.address.city(),
					 about_me=forgery_py.lorem_ipsum.sentence())
			u.set_password('111111')
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	def ping(self) -> None:
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def get_src_to_avatar(self) -> str:
		# i'm using url_for so when i'm calling url_for() i'm input directory where he must search data
		# also i'm using defend in front-end
		# {% if user.get_src_to_avatar() %}
		# 	upload user image
		# {% else %}
		# 	upload default image
		# {% endif %}
		# url_for('static', filename=user.get_src_to_avatar())
		try:
			return f'users_avatars/{self.avatar[0].filename}'
		except IndexError:
			return ''

	def get_role(self):
		return Role.query.filter_by(id=self.role_id).first()

	def can(self, permissions) -> bool:
		r = self.get_role()
		return self.role_id is not None and \
			   (r.permissions & permissions) == permissions

	def is_administrator(self) -> bool:
		return self.can(Permission.ADMINISTRATOR)

	def to_json(self) -> Dict[str, str]:
		json_user = {
			'username': self.username,
			'email': self.email,
			'last_seen': self.last_seen,
			'member_since': self.created_on,
			'posts_count': self.posts.count(),
			'comments_count': self.comments.count(),
			'posts_url': url_for('api.get_user_posts', id=self.id, page=1),
			'comments_url': url_for('api.get_user_comments', id=self.id, page=1)
		}
		return json_user

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
	id = db.Column(db.Integer(), primary_key=True, index=True)
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

	@staticmethod
	def generate_fake(count=100):
		import forgery_py
		from random import seed, randint

		seed()
		user_count = User.query.count()

		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			a = Article(title='tetdatet',
						intro=forgery_py.lorem_ipsum.sentence(),
						text=forgery_py.lorem_ipsum.sentence(),
						author_name=u.username,
						user_id=u.id,
			)
			db.session.add(a)
			db.session.commit()

	def to_json(self) -> Dict[str, str]:
		json_post = {
			'title': self.title,
			'intro': self.intro,
			'text': self.text,
			'date': self.date,
			'count_views': self.count_views,
			'comments_count': self.comments.count(),
			'author_url': url_for('api.get_user', id=self.user_id),
			'comments_url': url_for('api.get_all_comments_from_post', id=self.id)
		}
		return json_post

	@staticmethod
	def from_json(json_post):
		try:
			title = json_post.get('title')
			intro = json_post.get('intro')
			text = json_post.get('text')
			if not text or not title or not intro:
				raise ValidationError('post does not have a text/title or intro')
			return Article(title=title, intro=intro, text=text)
		except:
			raise ValidationError('post does not have a text/title or intro')

	def __repr__(self):
		return "<Article %r>" % self.id


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer(), primary_key=True, index=True)
	text = db.Column(db.String(500), nullable=False)
	author = db.Column(db.String(50), nullable=False)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))

	def to_json(self) -> Dict[str, str]:
		json_comment = {
			'text': self.text,
			'author_url': url_for('api.get_user', id=self.user_id),
			'created_on': self.date,
			'post_id': self.post_id
		}
		return json_comment

	@staticmethod
	def from_json(json_comment):
		text = json_comment.get('text')
		if not text:
			raise ValidationError('post does not have a text')
		return Comment(text=text)

	def __repr__(self):
		return '<comment %r>' % self.id


class UsersWhichViewedPost(db.Model):
	__tablename__ = 'user_which_viewed_post'
	id = db.Column(db.Integer(), primary_key=True, index=True)
	user_id = db.Column(db.Integer(), nullable=False, index=True)
	post_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))

	def __repr__(self):
		return "<UserWhichViewedPost %r>" % self.id


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(64), unique=True, index=True)
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
