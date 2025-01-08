# @file thinking_dataset/datasets/operations/operation.py
# @description Defines the base class for dataset operations.
# @version 1.0.0
# @license MIT

from abc import ABC, abstractmethod
from ...utilities.log import Log


class Operation(ABC):
    """
    A base class for dataset operations.
    """

    def __init__(self, data_tonic):
        self.data_tonic = data_tonic

    def _execute(self, *args, **kwargs):
        try:
            return self.execute(*args, **kwargs)
        except Exception as e:
            Log.error(f"Error executing operation: {e}", exc_info=True)
            raise e

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
