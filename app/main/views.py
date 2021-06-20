from app import db
from . import main

from flask import (
	render_template
)

#--------OTHER VIEWS----------#


@main.route('/')
def index():
	return render_template('index.html')

