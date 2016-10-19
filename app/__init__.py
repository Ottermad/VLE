import datetime

from flask import Flask, jsonify, current_app, g

from flask_bcrypt import check_password_hash
from flask_jwt import JWT, current_identity
from flask_sqlalchemy import SQLAlchemy

from .exceptions import CustomError
from .settings import DATABASE_NAME, SECRET_KEY

db = SQLAlchemy()
jwt = JWT()


@jwt.authentication_handler
def authenticate(username, password):
    from .user.models import User
    # Check username
    user = User.query.filter_by(username=username).first()
    if user is None:
        raise CustomError(401, message='Username or password were not found.')

    # Check password
    if not check_password_hash(user.password, password):
        raise CustomError(401, message='Username or password were not found.')

    return user.to_dict()


@jwt.identity_handler
def identity(payload):
    from .user.models import User
    user_id = payload['identity']
    user = User.query.get(user_id)
    if user is None:
        raise CustomError(404, 'User with id: {} was not found.'.format(id))
    g.user = user
    return user.to_dict()


@jwt.jwt_payload_handler
def payload_handler(identity):
    iat = datetime.datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    new_identity = identity['id']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': new_identity}


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@' \
        'localhost/{}'.format(DATABASE_NAME)
    app.config['SECRET_KEY'] = SECRET_KEY

    db.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(CustomError)
    def custom_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    from .school import school_blueprint
    app.register_blueprint(school_blueprint)
    from .permissions import permissions_blueprint
    app.register_blueprint(permissions_blueprint)
    from .user import user_blueprint
    app.register_blueprint(user_blueprint)

    return app
