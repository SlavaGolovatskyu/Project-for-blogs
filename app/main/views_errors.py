from app import db
from . import main

from flask import render_template

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')