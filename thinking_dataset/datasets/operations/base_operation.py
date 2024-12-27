"""
@file thinking_dataset/datasets/operations/base_operation.py
@description Defines the base class for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import logging
from abc import ABC, abstractmethod


class BaseOperation(ABC):
    """
    A base class for dataset operations.
    """

    def __init__(self, data_tonic):
        self.data_tonic = data_tonic

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
