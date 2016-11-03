from app.lessons.subject_functions import create_subject_view, list_subject_view, subject_detail_view, subject_delete_view, \
    subject_update_view
from app.lessons.lesson_functions import lesson_create
from flask import Blueprint, request
from flask.ext.jwt import jwt_required

lessons_blueprint = Blueprint('lessons', __name__, url_prefix='/lessons')


@lessons_blueprint.route('/')
def index():
    return "Lessons Index"


@lessons_blueprint.route('/subject', methods=['POST', 'GET'])
@jwt_required()
def subject_list_or_create_view():
    if request.method == "POST":
        return create_subject_view(request)
    else:
        return list_subject_view(request)


@lessons_blueprint.route('/subject/<subject_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def subject_individual_view(subject_id):
    if request.method == 'GET':
        return subject_detail_view(request, subject_id=subject_id)
    if request.method == 'DELETE':
        return subject_delete_view(request, subject_id)
    if request.method == 'PUT':
        return subject_update_view(request, subject_id)


@lessons_blueprint.route('/lesson', methods=['POST', 'GET'])
@jwt_required()
def lesson_list_or_create_view():
    if request.method == "POST":
        return lesson_create(request)


@lessons_blueprint.route('/lesson/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def lesson_detail_view(id):
    pass