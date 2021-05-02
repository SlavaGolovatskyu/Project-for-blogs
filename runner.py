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

app = create_app(os.getenv('FLASK_ENV') or 'config.ProductionConfig')
manager = Manager(app)

# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
    return dict(app=app, db=db, User=User, Article=Article,
    		    UsersWhichViewedPost=UsersWhichViewedPost, Comment=Comment)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()