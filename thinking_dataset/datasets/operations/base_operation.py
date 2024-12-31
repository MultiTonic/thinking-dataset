"""
@file thinking_dataset/datasets/operations/base_operation.py
@description Defines the base class for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|GitHub Repository}
"""

from abc import ABC, abstractmethod
from ...utilities.log import Log


class BaseOperation(ABC):
    """
    A base class for dataset operations.
    """

    def __init__(self, data_tonic, config=None):
        self.log = Log.setup(self.__class__.__name__)
        self.data_tonic = data_tonic
        self.config = config

    @abstractmethod
    def execute(self):
        """
        Executes the operation.
        """
        pass
