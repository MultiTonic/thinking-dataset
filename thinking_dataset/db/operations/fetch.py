"""
@file thinking_dataset/db/operations/fetch_data.py
@description Defines a concrete class for fetching data from the database.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from sqlalchemy import text
from .database_operation import DatabaseOperation
from ...utilities.log import Log


class Fetch(DatabaseOperation):
    """
    A class to handle fetching data from the database.
    """

    def __init__(self, database, query: str):
        """
        Constructs all the necessary attributes for the Fetch operation.

        Parameters
        ----------
        database : Database
            An instance of the Database class to perform operations on.
        query : str
            The SQL query to fetch data.
        """
        super().__init__(database)
        self.query = query
        self.logger = Log.setup(__name__)

    def execute(self):
        """
        Executes the SQL query to fetch data from the database.
        """
        try:
            with self.database.engine.connect() as connection:
                result = connection.execute(text(self.query)).fetchall()
                Log.info(self.logger, "Query executed successfully")
                return result
        except Exception as e:
            Log.error(self.logger, f"Error fetching data: {e}")
            return []
