"""Base Pipe Module.

This module provides the abstract base class for all pipeline processing pipes,
handling common functionality like progress tracking and multi-threading.

Functions:
    None

Classes:
    Pipe: Abstract base class for all processing pipes.
"""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import importlib
import signal
import sys
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List, Type

import pandas as pd
from tqdm import tqdm

from thinking_dataset.utils.command_utils import CommandUtils as utils
from thinking_dataset.utils.log import Log


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

    abort_flag: threading.Event = threading.Event()
    pipeline_config: dict = {}

    def __init__(self, config: dict) -> None:
        """Initialize pipe with configuration.

        Args:
            config (dict): Configuration dictionary for the pipe
        """
        self.config = config or {}
        signal.signal(signal.SIGINT, self.signal_handler)

    @classmethod
    def set_pipeline_config(cls, config: dict) -> None:
        """Set the pipeline configuration for all pipes.

        Args:
            config (dict): Pipeline configuration dictionary
        """
        cls.pipeline_config = config or {}

    @classmethod
    def get_batch_size(cls) -> int:
        """Get batch size from current pipeline configuration.

        Returns:
            int: Configured batch size or default value of 1
        """
        return cls.pipeline_config.get('batch_size', 1)

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
        raise NotImplementedError("Pipe subclasses must implement flow()")

    @classmethod
    def get_pipe(cls, pipe_type: str) -> Type['Pipe']:
        """Get pipe class by type name.

        Args:
            pipe_type (str): Name of pipe class to load

        Returns:
            Type[Pipe]: Pipe class type

        Raises:
            ImportError: If pipe class cannot be loaded
        """
        module_name = \
            "thinking_dataset.pipeworks.pipes." + \
            utils.camel_to_snake(pipe_type)
        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Error loading pipe class {pipe_type} from "
                              f"module {module_name}") from e

    def progress_apply(self, series: pd.Series, func: Callable,
                       desc: str) -> pd.Series:
        """Apply function to series with progress bar.

        Args:
            series (pd.Series): Input series
            func (Callable): Function to apply
            desc (str): Progress bar description

        Returns:
            pd.Series: Transformed series
        """
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)

    @classmethod
    def multi_thread_apply(cls,
                           series: pd.Series,
                           func: Callable,
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
        completed = 0
        results: List[Any] = []

        with tqdm(total=total, desc=desc) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(func, value): i
                    for i, value in enumerate(series)
                }

                for future in as_completed(futures):
                    try:
                        results.append(future)
                        completed += 1
                        pbar.update(1)
                    except Exception as e:
                        raise RuntimeError(
                            f"Thread execution failed: {str(e)}") from e

        results.sort(key=lambda x: futures[x])
        return pd.Series([future.result() for future in results],
                         index=series.index)

    @staticmethod
    def signal_handler(sig: int, frame: Any) -> None:
        """Handle interrupt signals.

        Args:
            sig (int): Signal number
            frame (Any): Current stack frame
        """
        Log.error("\nProcess aborted by user.")
        Pipe.abort_flag.set()
        sys.exit(0)

    @classmethod
    def flush(cls,
              df: pd.DataFrame,
              use_all_columns: bool = False) -> pd.DataFrame:
        """Create a new DataFrame with the proper column structure.

        - If use_all_columns is True, return all columns,
            ensuring 'id' is first.
        - If False, return a DataFrame with a sequential 'id' column
            based on batch size.
        """
        if use_all_columns:
            if 'id' not in df.columns:
                columns = ['id'] + list(df.columns)
            else:
                columns = ['id'] + [col for col in df.columns if col != 'id']
            new_df = pd.DataFrame(columns=columns)
        else:
            # Create a DataFrame with sequential IDs from 1 to batch size.
            batch_size = cls.get_batch_size()
            new_df = pd.DataFrame({'id': list(range(1, batch_size + 1))})
        Log.info(f"Flushed DataFrame with columns: {new_df.columns.tolist()}")
        return new_df

    @classmethod
    def log_df_state(cls,
                     df: pd.DataFrame,
                     state: str = "",
                     show_head: bool = False) -> None:
        """Log the current state of a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to log information about
            state (str, optional): Description of current state. Default to "".
            show_head (bool, optional): Will show first row. Defaults to False.
        """
        prefix = f"{state} " if state else ""
        Log.info(f"{prefix}DataFrame shape: {df.shape}")
        Log.info(f"{prefix}DataFrame columns: {df.columns.tolist()}")
        if show_head and not df.empty:
            Log.info(
                f"{prefix}DataFrame head:\n{df.head(1).to_dict('records')}")
