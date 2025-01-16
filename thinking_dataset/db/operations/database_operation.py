# @file thinking_dataset/db/operations/database_operation.py
# @description Defines the base class for database operations.
# @version 1.0.1
# @license MIT

from abc import ABC, abstractmethod


class DatabaseOperation(ABC):
    """
    A base class for database operations.
    """

    def __init__(self, database):
        self.database = database

    @abstractmethod
    def execute(self) -> None:
        pass
