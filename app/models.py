from app import db, login_manager
from datetime import datetime

from flask_login import (
	UserMixin
)

from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
	return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer(), primary_key=True)
	username = db.Column(db.String(50), nullable=False, unique=True)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password_hash = db.Column(db.String(100), nullable=False)
	is_admin = db.Column(db.Boolean(), default=False)
	lvl_of_admin = db.Column(db.Integer(), default=0)
	is_banned = db.Column(db.Boolean(), default=False)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)	

	comments = db.relationship('Comment', cascade='all,delete-orphan', lazy='dynamic')
	posts = db.relationship('Article', cascade='all,delete-orphan', lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return "<Account %r>" % self.id


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

