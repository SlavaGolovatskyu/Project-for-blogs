from app import db, socket
from . import main
from flask_socketio import emit

from flask import (
	render_template, 
	url_for, 
	redirect, 
	flash, 
	session,
)

from flask_login import (
	login_required,
	login_user, 
	logout_user,
	current_user
)

from app.models import User, Article

#--------OTHER VIEWS----------#
@main.route('/')
def index():
	return render_template('index.html')


@main.route('/socket.io/?transport=polling&EIO=4')
def test():
	return 5


