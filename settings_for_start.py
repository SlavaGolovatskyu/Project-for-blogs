import os
from app import create_app, db
from flask_login import current_user
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand
from flask_socketio import SocketIO, emit
from app.logg.logger import logger

from app.models import (
	User,
	Article,
	UsersWhichViewedPost,
	Comment,
	Role,
	Permission
)

app = create_app(os.getenv('FLASK_ENV') or 'config.DevelopementConfig')

manager = Manager(app)

#socket = SocketIO(app)


# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
	return dict(app=app, db=db, User=User, Article=Article, Role=Role, Permission=Permission,
				UsersWhichViewedPost=UsersWhichViewedPost, Comment=Comment)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

# ----------------WEB-CHAT---------------------#

# COUNT_ONLINE_USERS = 0
#
#
# @socket.on('connect')
# def connect_user():
# 	global COUNT_ONLINE_USERS
# 	COUNT_ONLINE_USERS += 1
# 	logger.info(f'User \"{current_user.username}\" connected')
# 	emit('get_online', COUNT_ONLINE_USERS, broadcast=True)
#
#
# @socket.on('disconnect')
# def test_disconnect():
# 	global COUNT_ONLINE_USERS
# 	COUNT_ONLINE_USERS -= 1
# 	logger.info(f'User \"{current_user.username}\" disconnected')
# 	emit('get_online', COUNT_ONLINE_USERS, broadcast=True)
#
#
# @socket.on('send_message')
# def send_message(data: dict):
# 	msg = data['msg']
# 	logger.info(f'User \"{current_user.username}\" send a message: {msg}')
# 	emit('take_msg', (current_user.username, msg), broadcast=True)

# ----------------WEB-CHAT---------------------#
