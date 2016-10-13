from flask import Blueprint

from .models import User

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/")
def index():
    return "User Index"
