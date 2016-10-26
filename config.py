import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "this_needs_to_be_more_secure")


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/{}'.format('vle_db')


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'testing-database.sqlite')
    PRESERVE_CONTEXT_ON_EXCEPTION = False

config = {
    'development': Development,
    'testing': Testing,
    'default': Development
}
