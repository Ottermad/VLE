from app.school.school_functions import signup_school
from flask import Blueprint, request, jsonify

from .school_functions import create_school

school_blueprint = Blueprint("school", __name__, url_prefix="/school")


@school_blueprint.route("/")
def index_view():
    return "School Index"


@school_blueprint.route("/school", methods=["POST"])
def create_view():
    return create_school(request)


@school_blueprint.route('/signup', methods=("POST",))
def signup():
    return signup_school(request)
