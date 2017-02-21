import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "this_needs_to_be_more_secure")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/{}'.format('vle_db')
    JWT_EXPIRATION_DELTA = datetime.timedelta(seconds=5000)


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'testing-database.sqlite')
    PRESERVE_CONTEXT_ON_EXCEPTION = False

config = {
    'development': Development,
    'testing': Testing,
    'default': Development
}
