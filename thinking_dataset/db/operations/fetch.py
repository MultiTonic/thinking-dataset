# @file thinking_dataset/db/operations/fetch.py
# @description Defines a concrete class for fetching data from the database.
# @version 1.0.1
# @license MIT

from sqlalchemy import text
from .database_operation import DatabaseOperation
from thinking_dataset.utils.log import Log


class Fetch(DatabaseOperation):
    """
    A class to handle fetching from the database.
    """

    def __init__(self, database, query: str):
        super().__init__(database)
        self.query = query

    def execute(self):
        try:
            with self.database.engine.connect() as connection:
                result = connection.execute(text(self.query)).fetchall()
                Log.info("Query executed successfully")
                return result
        except Exception as e:
            Log.error(f"Error fetching data: {e}")
            return []
