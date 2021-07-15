import unittest
import json
from app import create_app, db
from app.models import (
	User,
	Role
)
from flask import url_for
from base64 import b64encode
from app.user_location.get_location import get_location


class APITestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('config.TestingConfig')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_role()
		self.client = self.app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	@staticmethod
	def get_api_headers(username, password):
		return {
			'Authorization': 'Basic ' + b64encode(
				(username + ':' + password).encode('utf-8')).decode('utf-8'),
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		}

	def test_404(self):
		response = self.client.get(
			'/wrong/url/hahaha',
			headers=self.get_api_headers('email', 'password')
		)
		self.assertEqual(response.status_code, 404)

	def test_bad_auth(self):
		r = Role.query.filter_by(name='User').first()
		self.assertIsNotNone(r)
		u = User(username='slavik', email='john@example.com', real_location=get_location('146.120.168.159'))
		u.set_password('111111')
		db.session.add(u)
		db.session.commit()

		# authenticate with bad password
		response = self.client.get(
			'/api/v1.0/posts/new-post',
			headers=self.get_api_headers('john@example.com', '1111111416g')
		)
		self.assertEqual(response.status_code, 401)

	def test_anonymous(self):
		response = self.client.get(
			'/api/v1.0/posts/new-post',
			headers=self.get_api_headers('', '')
		)
		self.assertEqual(response.status_code, 401)

	def test_posts(self):
		r = Role.query.filter_by(name='User').first()

		self.assertIsNotNone(r)
		u = User(username='slavik', email='john@example.com', real_location=get_location('146.120.168.159'))
		u.set_password('111111')
		db.session.add(u)
		db.session.commit()

		response = self.client.post(
			'/api/v1.0/posts/new-post',
			headers=self.get_api_headers('john@example.com', '111111'),
			data=json.dumps({'title': '', 'intro': '', 'text': ''})
		)

		self.assertEqual(response.status_code, 404)

		response = self.client.post(
			'/api/v1.0/posts/new-post',
			headers=self.get_api_headers('john@example.com', '111111'),
			data=json.dumps({'title': '90ETRIHJFTRIOJHOIFYTRJIOFYRJHOIFYRJKYTFJOKYTGJOKYRFTJKOYTFJOLYT',
							 'intro': 'HDRTJYFUTKHYILHIKJLHIKUYIKUYTIKUYKUYKUHJGK',
							 'text': '1234567890FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'}))

		self.assertEqual(response.status_code, 201)
		url = response.headers.get('Location')
		self.assertIsNotNone(url)

		response = self.client.get(
			url,
			headers=self.get_api_headers('john@example.com', '111111')
		)
		self.assertEqual(response.status_code, 200)

