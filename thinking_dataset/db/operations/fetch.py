"""
@file thinking_dataset/db/operations/fetch.py
@description Defines a concrete class for fetching data from the database.
@version 1.0.0
@license MIT
"""

from sqlalchemy import text
from .database_operation import DatabaseOperation
from ...utilities.log import Log


class Fetch(DatabaseOperation):
    """
    A class to handle fetching from the database.
    """

    def __init__(self, database, query: str):
        """
        Constructs all the necessary attributes for the Fetch operation.
        """
        super().__init__(database)
        self.query = query
        self.log = Log.setup(self.__class__.__name__)

    def execute(self):
        """
        Executes the SQL query to fetch data from the database.
        """
        try:
            with self.database.engine.connect() as connection:
                result = connection.execute(text(self.query)).fetchall()
                Log.info(self.log, "Query executed successfully")
                return result
        except Exception as e:
            Log.error(self.log, f"Error fetching data: {e}")
            return []
