import os
from app import create_app, db

from app.models import (
	User, 
	Article,
	UsersWhichViewedPost,
	Comment
)

from flask_script import Manager, Shell
from flask_migrate import MigrateCommand
from flask_login import current_user
from flask_socketio import SocketIO, emit

app = create_app(os.getenv('FLASK_ENV') or 'config.DevelopementConfig')

manager = Manager(app)

socket = SocketIO(app)

COUNT_ONLINE_USERS = 0


@socket.on('connect_user')
def connect_user(data):
    global COUNT_ONLINE_USERS
    COUNT_ONLINE_USERS += 1
    print(data)
    emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


@socket.on('disconnect')
def test_disconnect():
    global COUNT_ONLINE_USERS
    COUNT_ONLINE_USERS -= 1
    emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


@socket.on('send_message')
def send_message(data: dict):
    emit('take_msg', (current_user.username, data['msg']), broadcast=True)


# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
    return dict(app=app, db=db, User=User, Article=Article,
    		    UsersWhichViewedPost=UsersWhichViewedPost, Comment=Comment)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    socket.run(app)