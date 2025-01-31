"""
Scrub Output Pipe Module.

This module provides functionality for scrubbing output data,
such as formatting or sanitizing.
"""

import pandas as pd

from .pipe import Pipe
from thinking_dataset.utils.log import Log

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class ScrubOutputPipe(Pipe):
    """Pipe for scrubbing output data, such as formatting or sanitizing."""

    def __init__(self, config: dict) -> None:
        """Initialize the ScrubOutputPipe with configuration settings.

        Args:
            config (dict): Configuration dictionary for the pipe.
        """
        super().__init__(config)

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Process the DataFrame by printing each row.

        Args:
            df (pd.DataFrame): Input DataFrame to process.

        Returns:
            pd.DataFrame: Unmodified DataFrame.
        """
        Log.info("Starting ScrubOutputPipe")
        Log.info(f"Format: {self.config.get('format')}")

        # debugging
        # for _, row in df.iterrows():
        #    print(row.to_dict())

        Log.info("Finished ScrubOutputPipe")
        return df
