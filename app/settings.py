import os

DATABASE_NAME = os.environ.get("DATABASE_NAME", "vle_db")
SECRET_KEY = os.environ.get("SECRET_KEY", "this_needs_to_be_more_secure")
