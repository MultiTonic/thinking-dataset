"""
@file thinking_dataset/db/operations/database_operation.py
@description Defines the base class for database operations.
@version 1.0.0
@license MIT
"""

from abc import ABC, abstractmethod
from ...utilities.log import Log


class DatabaseOperation(ABC):
    """
    A base class for database operations.
    """

    def __init__(self, database):
        """
        Constructs all the necessary attributes for the DatabaseOperation.

        Parameters
        ----------
        database : Database
            An instance of the Database class to perform operations on.
        """
        self.database = database
        self.log = Log.setup(self.__class__.__name__)

    @abstractmethod
    def execute(self) -> None:
        """
        Executes the operation.
        """
        pass
