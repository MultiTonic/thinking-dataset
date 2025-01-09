# @file thinking_dataset/db/operations/database_operation.py
# @description Defines the base class for database operations.
# @version 1.0.0
# @license MIT

from abc import ABC, abstractmethod
from thinking_dataset.utils.log import Log


class DatabaseOperation(ABC):
    """
    A base class for database operations.
    """

    def __init__(self, database):
        self.database = database
        self.log = Log._setup(self.__class__.__name__)

    @abstractmethod
    def execute(self) -> None:
        pass
