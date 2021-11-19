from flask import json, jsonify, url_for
from ..models import ActiveIP, User
from . import api


@api.route('/users/active-ip/<string:ip>')
def find_active_ip(ip):
	ip = ActiveIP.query.filter_by(ip=ip).first()
	if ip:
		return jsonify(True)
	return jsonify(False)


@api.route('/users/check-password/<string:email>/<string:password>')
def check_exist_user_n_pass(email, password):
	user = User.query.filter_by(email=email).first()
	if user:
		if user.check_password(password):
			return jsonify(True)
	return jsonify(False)


@api.route('/users/find-by-ip/<string:ip>')
def find_user_by_ip(ip: str):
	user = User.query.filter_by(ip=ip).first()
	if user:
		return jsonify(True)
	return jsonify(False)


@api.route('/user/<int:id>')
def get_user(id):
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())


@api.route('/users/<int:page>')
def get_users(page):
	pagination = User.query.paginate(
		page, per_page=20,
		error_out=True
	)
	users = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_users', page=page - 1)
	next = None
	if pagination.has_next:
		next = url_for('api.get_users', page=page + 1)
	return jsonify({
		'users': [user.to_json() for user in users],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})