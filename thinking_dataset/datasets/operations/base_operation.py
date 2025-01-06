# @file thinking_dataset/datasets/operations/base_operation.py
# @description Defines the base class for dataset operations.
# @version 1.0.0
# @license MIT

from abc import ABC, abstractmethod


class Operation(ABC):
    """
    A base class for dataset operations.
    """

    def __init__(self, data_tonic, config=None):
        self.data_tonic = data_tonic
        self.config = config

    @abstractmethod
    def execute(self):
        pass
