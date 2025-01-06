# @file project_root/thinking_dataset/pipeworks/pipes/pipe.py
# @description Defines BasePipe class for preprocessing tasks with logging.
# @version 1.1.1
# @license MIT

import importlib
import pandas as pd
from tqdm import tqdm
from abc import ABC, abstractmethod
from thinking_dataset.utilities.log import Log
from concurrent.futures import ThreadPoolExecutor
from thinking_dataset.utilities.command_utils import CommandUtils as Utils


class Pipe(ABC):
    """
    Base class for preprocessing tasks.
    """

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def flow(self, df, **args):
        Log.info(f"Flow -- {self.__class__.__name__}")
        pass

    @staticmethod
    def get_pipe(pipe_type):
        module_name = "thinking_dataset.pipeworks.pipes." + \
            Utils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError):
            raise ImportError(f"Error loading pipe class {pipe_type} "
                              f"from module {module_name}")

    def progress_apply(self, series, func, desc):
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)

    def multi_thread_apply(self, series, func, desc, max_workers=16):
        tqdm.pandas(desc=desc)
        total = len(series)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func, value) for value in series]
            results = []
            for future in tqdm(futures, total=total, desc=desc):
                results.append(future.result())
        return pd.Series(results, index=series.index)
