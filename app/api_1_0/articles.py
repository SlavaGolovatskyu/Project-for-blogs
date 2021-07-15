from flask import jsonify, url_for, request, g
from ..models import Article, User, Permission
from . import api
from app import db
from .decorators import permission_required


@api.route('/post/<int:id>')
def get_post(id):
	post = Article.query.get_or_404(id)
	return jsonify(post.to_json())


@api.route('/posts/<int:page>')
def get_posts(page):
	pagination = Article.query.paginate(
		page, per_page=20,
		error_out=True
	)
	posts = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_posts', page=page - 1)
	next = None
	if pagination.has_next:
		next = url_for('api.get_posts', page=page + 1)
	return jsonify({
		'posts': [post.to_json() for post in posts],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})


@api.route('/posts/user/<int:id>/page/<int:page>')
def get_user_posts(id, page):
	user = User.query.get_or_404(id)
	pagination = user.posts.paginate(
		page, per_page=20,
		error_out=True
	)
	user_posts = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_user_posts', id=id, page=page - 1)
	next = None
	if pagination.has_next:
		next = url_for('api.get_user_posts', id=id, page=page + 1)
	return jsonify({
		'posts': [user_post.to_json() for user_post in user_posts],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})


@api.route('/posts/new-post', methods=['post', 'get'])
@permission_required(Permission.USUAL_USER)
def new_post():
	post = Article.from_json(request.json)
	post.author_name = g.current_user.username
	post.user_id = g.current_user.id
	db.session.add(post)
	db.session.commit()
	return jsonify(post.to_json()), 201, \
			{'Location': url_for('api.get_post', id=post.id)}