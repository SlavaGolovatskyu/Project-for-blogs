from flask import Blueprint

main = Blueprint('main', __name__)

from . import (
	views, 
	views_account, 
	views_admin,
	views_articles,
	views_errors
)
