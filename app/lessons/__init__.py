from flask import Blueprint

lessons_blueprint = Blueprint('lessons', __name__, url_prefix='/lessons')


@lessons_blueprint.route('/')
def index():
    return "Lessons Index"
