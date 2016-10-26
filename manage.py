import logging

from subprocess import call

from app import create_app, db
from app.settings import DATABASE_NAME

from flask_migrate import Migrate, MigrateCommand, init

from flask_script import Manager

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError


app = create_app()

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


# Get an instance of a logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')


@manager.command
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


@manager.command
def run():
    # call(["python", "manage.py", "create_database"])
    # call(["python", "manage.py", "db", "upgrade"])
    app.run(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    manager.run()