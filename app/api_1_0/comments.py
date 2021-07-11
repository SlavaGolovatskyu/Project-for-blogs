from flask import jsonify, url_for
from ..models import Comment, User, Article
from . import api
from ..decorators import admin_required


@api.route('/comment/<int:id>')
def get_comment(id):
	comment = Comment.query.get_or_404(id)
	return jsonify(comment.to_json())


@api.route('/comments/user/<int:id>/page/<int:page>')
def get_user_comments(id, page):
	user = User.query.get_or_404(id)
	pagination = user.comments.paginate(
		page, per_page=20,
		error_out=True
	)
	user_comments = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_user_comments', id=id, page=page - 1)
	next = None
	if pagination.has_next:
		next = url_for('api.get_user_comments', id=id, page=page + 1)
	return jsonify({
		'posts': [user_comment.to_json() for user_comment in user_comments],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})


@api.route('/comments')
@admin_required
def get_all_comments():
	comments = Comment.query.all()
	return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/comments/user/<int:id>')
def get_all_user_comments(id):
	user = User.query.get_or_404(id)
	return jsonify({'comments': [comment.to_json() for comment in user.comments]})


@api.route('/comments/post/<int:id>')
def get_all_comments_from_post(id):
	post = Article.query.get_or_404(id)
	return jsonify({'comments': [comment.to_json() for comment in post.comments]})

