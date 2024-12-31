"""
@file project_root/thinking_dataset/pipes/base_pipe.py
@description Defines BasePipe class for preprocessing tasks with logging.
@version 1.0.0
@license MIT
"""

from abc import ABC, abstractmethod
from thinking_dataset.utilities.log import Log


class BasePipe(ABC):
    """
    Base class for preprocessing tasks.
    """

    def __init__(self, config: dict):
        self.config = config
        self.log = Log.setup(self.__class__.__name__)

    @abstractmethod
    def flow(self, df, log, **args):
        """
        Flow the DataFrame through the pipe. To be implemented by subclasses.
        """
        pass
