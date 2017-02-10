from app.homework.essay_functions import create_essay, submit_essay
from app.homework.quiz_functions import create_quiz, submit_quiz
from app.permissions.decorators import permissions_required
from flask import Blueprint, request, g
from flask_jwt import jwt_required
from .models import *

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/')
def index():
    return "Homework Index"


# Quiz Routes
@homework_blueprint.route('/quiz', methods=("POST", "GET"))
@jwt_required()
def quiz_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_quiz(request)


@homework_blueprint.route('/quiz/<int:quiz_id>', methods=("POST",))
@jwt_required()
@permissions_required({'Student'})
def quiz_submit(quiz_id):
    return submit_quiz(request, quiz_id)


# Essay Routes
@homework_blueprint.route('/essay', methods=("POST",))
@jwt_required()
def essay_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_essay(request)


@homework_blueprint.route('/essay/<int:essay_id>', methods=("POST",))
@jwt_required()
def essay_submit(essay_id):
    return submit_essay(request, essay_id)
