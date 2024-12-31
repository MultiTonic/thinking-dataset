"""
@file thinking_dataset/db/operations/query.py
@description Defines a concrete class for executing a query on the database.
@version 1.0.0
@license MIT
"""

from sqlalchemy import text
from .database_operation import DatabaseOperation
from ...utilities.log import Log


class Query(DatabaseOperation):
    """
    A class to handle executing a query on the database.
    """

    def __init__(self, database, query: str):
        """
        Constructs all the necessary attributes for the Query operation.
        """
        super().__init__(database)
        self.query = query
        self.log = Log.setup(self.__class__.__name__)

    def execute(self):
        """
        Executes the SQL query on the database.
        """
        try:
            with self.database.engine.connect() as connection:
                connection.execute(text(self.query))
                connection.commit()
                Log.info(self.log, "Query executed successfully")
        except Exception as e:
            Log.error(self.log, f"Error executing query: {e}")
