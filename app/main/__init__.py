from flask import Blueprint
from app.models import Permission as Perm
from .validators import Validators as Val

main = Blueprint('main', __name__)

validator = Val()


@main.app_context_processor
def inject_permissions():
	return dict(Permission=Perm)


@main.app_context_processor
def inject_validator():
	return dict(validate_art_or_com_of_the_owner=validator.check_article_or_comment_of_the_owner)


from . import (
	views,
	views_account,
	views_admin,
	views_articles,
	views_errors
)
