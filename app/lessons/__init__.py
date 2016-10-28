from flask import Blueprint, request
from flask.ext.jwt import jwt_required

from app.lessons.subject_functions import create_subject_view

lessons_blueprint = Blueprint('lessons', __name__, url_prefix='/lessons')


@lessons_blueprint.route('/')
def index():
    return "Lessons Index"


@lessons_blueprint.route('/subject', methods=['POST', 'GET'])
@jwt_required()
def subject_list_or_create_view():
    if request.method == "POST":
        return create_subject_view(request)


@lessons_blueprint.route('/subject/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def subject_detail_view(id):
    pass


@lessons_blueprint.route('/lesson', methods=['POST', 'GET'])
@jwt_required()
def lesson_list_or_create_view():
    pass


@lessons_blueprint.route('/lesson/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def lesson_detail_view(id):
    pass
