from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy

from .settings import DATABASE_NAME

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@' \
        'localhost/{}'.format(DATABASE_NAME)

    db.init_app(app)

    from .user import user_blueprint
    app.register_blueprint(user_blueprint)
    return app