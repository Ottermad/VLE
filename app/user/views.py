from app.permissions import permissions_required
from app.user.user_functions import user_listing, user_create, current_user_details, user_update, user_detail, \
    user_delete
from flask import Blueprint, request
from flask_jwt import jwt_required

user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/")
def index_view():
    return "User Index"


@user_blueprint.route("/user", methods=["GET", "POST"])
@jwt_required()
@permissions_required({'Administrator'})
def user_listing_or_create_view():
    """Route to create User from a POST request."""
    if request.method == "GET":
        return user_listing(request)

    if request.method == "POST":
        return user_create(request)


@user_blueprint.route("/user/<int:user_id>", methods=["PUT", "GET", "DELETE"])
@jwt_required()
def user_update_or_delete(user_id):
    if request.method == "PUT":
        return user_update(request, user_id)

    if request.method == "GET":
        return user_detail(request, user_id)

    if request.method == "DELETE":
        return user_delete(request, user_id)


@user_blueprint.route("/me")
@jwt_required()
def current_user_detail_view():
    return current_user_details(request)