"""
@file thinking_dataset/db/operations/get_session.py
@description Handles getting a database session.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .database_operation import DatabaseOperation
from ..session.session import Session
from ...utilities.log import Log


class GetSession(DatabaseOperation):
    """
    A class to handle getting a database session.
    """

    def __init__(self, database):
        """
        Constructs all the necessary attributes for the GetSession operation.

        Parameters
        ----------
        database : Database
            An instance of the Database class to perform operations on.
        """
        super().__init__(database)
        self.session_store = Session(database.engine)
        self.logger = Log.setup(__name__)

    def __enter__(self):
        """
        Enter the runtime context for the session, yielding the session.
        """
        return self.session_store.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context for the session, rolling back when exception.
        """
        if exc_type:
            self.session_store.rollback()
            Log.error(self.logger, f"Session error: {exc_val}")
        else:
            self.session_store.commit()

    def execute(self):
        """
        Execute getting a database session.
        """
        try:
            with self:
                pass
        except Exception as e:
            Log.error(self.logger, f"Failed to get session: {e}")
