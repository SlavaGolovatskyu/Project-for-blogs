from flask import Blueprint

main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)


from . import (
	views,
	views_account,
	views_admin,
	views_articles,
	views_errors
)
