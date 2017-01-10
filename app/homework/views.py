from app.homework.homework_functions import create_quiz
from flask import Blueprint, request, g
from flask_jwt import jwt_required
from .models import *

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/')
def index():
    return "Homework Index"


@homework_blueprint.route('/quiz', methods=("POST", "GET"))
@jwt_required()
def quiz_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_quiz(request)