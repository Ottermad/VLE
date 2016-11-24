from flask import Blueprint

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/')
def index():
    return "Homework Index"
