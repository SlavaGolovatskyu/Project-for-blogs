import unittest
from app import create_app, db
from app.models import (
	User,
	Role
)
from flask import url_for


class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('config.TestingConfig')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_role()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)

	def test_register_and_login(self):
		response = self.client.post(url_for('.sign_up'), data={
			'email': 'test@gmail.com',
			'username': 'slavik',
			'password': '111111'
		})

		self.assertEqual(response.status_code, 200)

		response = self.client.post(url_for('.login'), data={
			"email": 'test@gmail.com',
			"password": '111111'
		})

		self.assertEqual(response.status_code, 200)
		response = self.client.get(url_for('.logout'), follow_redirects=True)
		self.assertEqual(response.status_code, 200)

