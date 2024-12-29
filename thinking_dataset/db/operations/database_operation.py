"""
@file thinking_dataset/db/operations/database_operation.py
@description Defines the base class for database operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import logging
from abc import ABC, abstractmethod


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

    def log_info(self, message):
        """
        Logs an informational message.

        Parameters
        ----------
        message : str
            The message to log.
        """
        logging.info(message)

    @abstractmethod
    def execute(self):
        """
        Executes the operation.
        """
        pass
