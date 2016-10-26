import datetime
import logging

from flask import Flask, jsonify, current_app, g

from flask_bcrypt import check_password_hash
from flask_jwt import JWT
from flask_migrate import init, upgrade, Migrate
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from config import config

from .exceptions import CustomError
from .settings import DATABASE_NAME, SECRET_KEY

db = SQLAlchemy()
jwt = JWT()
migrate = Migrate()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')


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


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

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
    from .lessons import lessons_blueprint
    app.register_blueprint(lessons_blueprint)

    return app


def create_database():
    logging.info("Creating database")
    engine = create_engine("postgresql://postgres:postgres@localhost/postgres")
    conn = engine.connect()
    conn.execute("commit")

    try:
        conn.execute("create database {}".format(DATABASE_NAME))
        logging.info("Created database")
        init()
        logging.info("Setup database for migrations")
    except ProgrammingError:
        logging.info("Database already existed, continuing")
    finally:
        conn.close()
