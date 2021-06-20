from flask import Blueprint
from app.models import Permission as Perm
from .validators import Validators as Val

main = Blueprint('main', __name__)

validator = Val()


@main.app_context_processor
def inject_needed_function_and_more_other():
	return dict(Permission=Perm,
				validate_art_or_com_of_the_owner=validator.check_article_or_comment_of_the_owner)


from . import (
	views,
	views_account,
	views_admin,
	views_articles,
	views_errors
)
