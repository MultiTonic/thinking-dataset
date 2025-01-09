# @file thinking_dataset/pipeworks/pipes/pipe.py
# @description Defines BasePipe class for preprocessing tasks with logging.
# @version 1.1.2
# @license MIT

import time
import threading
import importlib
import pandas as pd
from tqdm import tqdm
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from thinking_dataset.utilities.log import Log
from thinking_dataset.utilities.command_utils import CommandUtils as utils


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
            utils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError):
            raise ImportError(f"Error loading pipe class {pipe_type} "
                              f"from module {module_name}")

    def progress_apply(self, series, func, desc):
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)

    def multi_thread_apply(self, series, func, desc, max_workers=5):
        total = len(series)
        pbar = tqdm(total=total, desc=desc)

        results = []
        completed = 0

        def progress_updater():
            while completed < total:
                pbar.n = completed
                pbar.refresh()
                time.sleep(0.1)

        updater_thread = threading.Thread(target=progress_updater)
        updater_thread.start()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(func, value): i
                for i, value in enumerate(series)
            }

            for future in as_completed(futures):
                results.append(future)
                completed += 1

        pbar.n = completed
        pbar.refresh()
        pbar.close()
        updater_thread.join()

        results.sort(key=lambda x: futures[x])

        return pd.Series([future.result() for future in results],
                         index=series.index)
