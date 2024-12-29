"""
@file thinking_dataset/db/operations/database_operation.py
@description Defines the base class for database operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
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
        self.logger = Log.setup(self.__class__.__name__)

    def log_info(self, message: str) -> None:
        """
        Logs an informational message.

        Parameters
        ----------
        message : str
            The message to log.
        """
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        """
        Logs an error message.

        Parameters
        ----------
        message : str
            The message to log.
        """
        self.logger.error(message)

    def log_warning(self, message: str) -> None:
        """
        Logs a warning message.

        Parameters
        ----------
        message : str
            The message to log.
        """
        self.logger.warning(message)

    @abstractmethod
    def execute(self) -> None:
        """
        Executes the operation.
        """
        pass
