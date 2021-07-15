import os
import config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from .logg.logger import logger
from flask_moment import Moment

db = SQLAlchemy()
socket = SocketIO()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app(config):
	# создание экземпляра приложения
	app = Flask(__name__)
	app.config.from_object(config)

	db.init_app(app)
	socket.init_app(app)
	moment.init_app(app)
	migrate.init_app(app, db, render_as_batch=True)
	login_manager.init_app(app)

	from .main import main as main_blueprint
	from .api_1_0 import api as api_1_0_blueprint

	app.register_blueprint(main_blueprint)
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	return app
