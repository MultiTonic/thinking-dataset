"""Base Pipe Module.

This module provides the abstract base class for all pipeline processing pipes,
handling common functionality like progress tracking and multi-threading.

Functions:
    None

Classes:
    Pipe: Abstract base class for all processing pipes.
"""

import time
import threading
import importlib
import pandas as pd
from tqdm import tqdm
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.command_utils import CommandUtils as utils
import signal
import sys

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class Pipe(ABC):
    """Abstract base class for processing pipes.

    This class provides:
    1. Common functionality for all processing pipes
    2. Progress tracking and multi-threading support
    3. Signal handling for graceful interruption
    4. Dynamic pipe loading capabilities

    Attributes:
        abort_flag (Event): Threading event for interruption handling
        config (dict): Pipe configuration dictionary
    """

    abort_flag = threading.Event()

    def __init__(self, config: dict):
        """Initialize pipe with configuration.

        Args:
            config (dict): Configuration dictionary for the pipe
        """
        self.config = config
        signal.signal(signal.SIGINT, self.signal_handler)

    @abstractmethod
    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute main pipe processing flow.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: Processed DataFrame
        """
        Log.info(f"Flow -- {self.__class__.__name__}")
        pass

    @staticmethod
    def get_pipe(pipe_type: str) -> type:
        """Get pipe class by type name.

        Args:
            pipe_type (str): Name of pipe class to load

        Returns:
            type: Pipe class type

        Raises:
            ImportError: If pipe class cannot be loaded
        """
        module_name = "thinking_dataset.pipeworks.pipes." + \
            utils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError):
            raise ImportError(f"Error loading pipe class {pipe_type} "
                              f"from module {module_name}")

    def progress_apply(self, series: pd.Series, func, desc: str) -> pd.Series:
        """Apply function to series with progress bar.

        Args:
            series (pd.Series): Input series
            func: Function to apply
            desc (str): Progress bar description

        Returns:
            pd.Series: Transformed series
        """
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)

    def multi_thread_apply(self,
                           series: pd.Series,
                           func,
                           desc: str,
                           max_workers: int = 5) -> pd.Series:
        """Apply function to series using multiple threads.

        Args:
            series (pd.Series): Input series
            func: Function to apply
            desc (str): Progress bar description
            max_workers (int, optional): Max thread count. Defaults to 5.

        Returns:
            pd.Series: Transformed series
        """
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

    @staticmethod
    def signal_handler(sig, frame):
        """Handle interrupt signals.

        Args:
            sig: Signal number
            frame: Current stack frame
        """
        Log.error("Process aborted by user.")
        Pipe.abort_flag.set()
        sys.exit(0)

    def flush(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """Clear DataFrame contents.

        Args:
            df (pd.DataFrame): DataFrame to flush
            column_name (str): Column to include

        Returns:
            pd.DataFrame: Empty DataFrame with specified columns
        """
        columns = ['id', column_name]
        df = pd.DataFrame(columns=columns)
        df.loc[0] = [None, None]
        Log.info("DataFrame Flushed!")
        return df
