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


class GetSession(DatabaseOperation):
    """
    A class to handle getting a database session.
    """

    def __init__(self, database):
        super().__init__(database)
        self.session_store = Session(database.engine)

    def execute(self):
        try:
            session = self.session_store.get()
            yield session
        except Exception as e:
            self.session_store.rollback()
            self.log_info(f"Session error: {e}")
