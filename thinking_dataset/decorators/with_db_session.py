# @file thinking_dataset/decorators/database_session.py
# @description Decorator to manage database session lifecycle.
# @version 1.0.0
# @license MIT

from functools import wraps
from thinking_dataset.db.database import Database
from thinking_dataset.utils.log import Log


def with_db_session(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        Log.info("Starting database session")
        with Database().get_session() as session:
            try:
                result = func(*args, session=session, **kwargs)
                Log.info("Closing database session")
                return result
            except Exception as e:
                Log.error(f"An error occurred: {str(e)}")
                raise

    return wrapper
