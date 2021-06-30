from flask_socketio import SocketIO, emit
from app.logg.logger import logger
from flask_login import current_user

socket = SocketIO()

COUNT_ONLINE_USERS = 0


@socket.on('connect')
def connect_user():
    global COUNT_ONLINE_USERS
    COUNT_ONLINE_USERS += 1
    logger.info(f'User \"{current_user.username}\" connected')
    emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


@socket.on('disconnect')
def test_disconnect():
    global COUNT_ONLINE_USERS
    COUNT_ONLINE_USERS -= 1
    logger.info(f'User \"{current_user.username}\" disconnected')
    emit('get_online', COUNT_ONLINE_USERS, broadcast=True)


@socket.on('send_message')
def send_message(data: dict):
    msg = data['msg']
    logger.info(f'User \"{current_user.username}\" send a message: {msg}')
    emit('take_msg', (current_user.username, msg), broadcast=True)
