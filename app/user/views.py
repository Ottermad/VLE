from app.permissions import permissions_required
from app.user.form_functions import create_form, list_forms, edit_form, delete_form, form_detail
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


@user_blueprint.route("/form", methods=("POST", "GET"))
@jwt_required()
@permissions_required({'Administrator'})
def form_listing_or_create():
    if request.method == "POST":
        return create_form(request)
    return list_forms(request)


@user_blueprint.route("/form/<int:form_id>", methods=("GET", "PUT", "DELETE"))
@jwt_required()
@permissions_required({"Administrator"})
def form_detail_update_delete(form_id):
    if request.method == "GET":
        return form_detail(request, form_id)

    if request.method == "PUT":
        return edit_form(request, form_id)

    if request.method == "DELETE":
        return delete_form(request, form_id)
