# @file thinking_dataset/db/operations/get_session.py
# @description Handles getting a database session.
# @version 1.0.0
# @license MIT

from .database_operation import DatabaseOperation
from ..database_session import DatabaseSession
from ...utilities.log import Log


class GetSession(DatabaseOperation):
    """
    A class to handle getting a database session.
    """

    def __init__(self, database):
        super().__init__(database)
        self.log = Log._setup(self.__class__.__name__)
        self.session_store = DatabaseSession(database.engine)

    def __enter__(self):
        return self.session_store.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session_store.rollback()
            Log.error(self.log, f"Session error: {exc_val}")
        else:
            self.session_store.commit()

    def execute(self):
        try:
            with self:
                pass
        except Exception as e:
            Log.error(self.log, f"Failed to get session: {e}")
