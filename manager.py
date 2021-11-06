#-*- coding: utf-8 -*-
import os

COVERAGE = True
COV = None

if COVERAGE:
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

import click
import sys
from flask_migrate import MigrateCommand
from flask_script import Manager, Shell
from flask_socketio import SocketIO, emit
from flask_login import current_user

from app import create_app, db
from app.models import (
	User,
	Article,
	UsersWhichViewedPost,
	Comment,
	Role,
	Permission,
	BannedIP
)

app = create_app(os.getenv('FLASK_ENV') or 'config.ProductionConfig')

manager = Manager(app)


# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
	return dict(app=app, db=db, User=User, Article=Article, Role=Role, Permission=Permission,
				UsersWhichViewedPost=UsersWhichViewedPost, Comment=Comment, BannedIP=BannedIP)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
			  help='Run tests under code coverage.')
@click.argument('test_names', nargs=-1)
@manager.command
def test(coverage=False, test_names=False):
	"""Run the unit tests."""
	if coverage and not COVERAGE:
		import subprocess
		os.environ['FLASK_COVERAGE'] = '1'
		sys.exit(subprocess.call(sys.argv))

	import unittest
	if test_names:
		tests = unittest.TestLoader().loadTestsFromNames(test_names)
	else:
		tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# socket = SocketIO(app)

# COUNT_ONLINE_USERS = 0


# @socket.on('connect')
# def connect_user():
#     global COUNT_ONLINE_USERS
#     COUNT_ONLINE_USERS += 1
#     emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


# @socket.on('disconnect')
# def disconnect_user():
#     global COUNT_ONLINE_USERS
#     COUNT_ONLINE_USERS -= 1
#     emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


# @socket.on('send_message')
# def send_message(data: dict):
#     msg = data['msg']
#     emit('receive_msg', (current_user.username, msg), broadcast=True)


if __name__ == '__main__':
	manager.run()