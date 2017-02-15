from app.permissions.decorators import permissions_required
from app.timetable.week_functions import create_week
from flask import Blueprint, request, g
from flask_jwt import jwt_required
from .models import *

timetable_blueprint = Blueprint('timetable', __name__, url_prefix='/timetable')


@timetable_blueprint.route('/')
def index():
    return "Timetable Index"


@timetable_blueprint.route('/week', methods=("POST",))
@jwt_required()
@permissions_required({'Administrator'})
def week_create_or_list():
    if request.method == "POST":
        return create_week(request)
