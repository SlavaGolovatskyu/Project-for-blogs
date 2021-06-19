from . import main

from flask import render_template


@main.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@main.errorhandler(403)
def permission_denied(e):
	return render_template('403.html'), 403
