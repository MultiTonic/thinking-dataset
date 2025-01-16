# @file thinking_dataset/db/operations/query.py
# @description Defines a concrete class for executing a query on the database.
# @version 1.0.1
# @license MIT

from sqlalchemy import text
from .database_operation import DatabaseOperation
from thinking_dataset.utils.log import Log


class Query(DatabaseOperation):
    """
    A class to handle executing a query on the database.
    """

    def __init__(self, database, query: str):
        super().__init__(database)
        self.query = query
        Log.info("Query initialized successfully")

    def execute(self):
        try:
            with self.database.engine.connect() as connection:
                connection.execute(text(self.query))
                connection.commit()
                Log.info("Query executed successfully")
        except Exception as e:
            Log.error(f"Error executing query: {e}")
