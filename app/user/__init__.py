from flask import Blueprint

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/")
def index():
    return "User Index"
