"""
@file thinking_dataset/db/operations/query.py
@description Defines a concrete class for executing a query on the database.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import sqlite3
from .database_operation import DatabaseOperation
from ...utilities.log import Log


class Query(DatabaseOperation):
    """
    A class to handle executing a query on the database.
    """

    def __init__(self, database, query: str):
        """
        Constructs all the necessary attributes for the Query operation.

        Parameters
        ----------
        database : Database
            An instance of the Database class to perform operations on.
        query : str
            The SQL query to execute.
        """
        super().__init__(database)
        self.query = query
        self.logger = Log.setup_logger(__name__)

    def execute(self):
        """
        Executes the SQL query on the database.
        """
        with sqlite3.connect(self.database.url) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self.query)
                conn.commit()
                Log.info(self.logger, "Query executed successfully")
            except sqlite3.Error as e:
                Log.error(self.logger, f"SQLite error: {e}")
