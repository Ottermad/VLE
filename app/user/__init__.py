from flask import Blueprint, request, jsonify, g
from flask_jwt import jwt_required

from app.permissions.decorators import permissions_required

from .user_functions import user_listing, user_create

user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/")
def index_view():
    return "User Index"


@user_blueprint.route("/user", methods=["GET", "POST"])
@jwt_required()
@permissions_required({'CRUD_USERS'})
def user_listing_or_create_view():
    """Route to create User from a POST request."""
    if request.method == "GET":
        return user_listing(request)

    if request.method == "POST":
        return user_create(request)
