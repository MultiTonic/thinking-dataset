"""
@file project_root/thinking_dataset/pipeworks/pipes/pipe.py
@description Defines BasePipe class for preprocessing tasks with logging.
@version 1.0.0
@license MIT
"""

import importlib
from abc import ABC, abstractmethod
from tqdm import tqdm
from thinking_dataset.utilities.log import Log
from thinking_dataset.utilities.command_utils import CommandUtils as Utils


class Pipe(ABC):
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
        self.log.info(f"Flow -- {self.__class__.__name__}")
        pass

    @staticmethod
    def get_pipe(pipe_type):
        """
        Dynamically import and return the pipe class based on the pipe type.
        """
        module_name = "thinking_dataset.pipeworks.pipes." + \
            Utils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError):
            raise ImportError(f"Error loading pipe class {pipe_type} "
                              f"from module {module_name}")

    def progress_apply(self, series, func, desc):
        """
        Apply a function to a pandas series with a progress bar.
        """
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)
