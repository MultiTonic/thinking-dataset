"""Add ID Pipeline Module.

This module provides functionality for adding unique identifiers to DataFrame
rows, supporting both integer sequence and UUID generation.

Functions:
    None

Classes:
    AddIdPipe: Handles unique identifier generation and assignment.
"""

import uuid
from typing import Any, Dict, Union

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class AddIdPipe(Pipe):
    """Pipe for adding unique identifiers to DataFrame rows.

    This pipe:
    1. Validates DataFrame structure
    2. Generates unique identifiers (int sequence or UUID)
    3. Inserts ID column as first column
    4. Maintains data integrity during processing

    Config:
        id_type (str): Type of ID to generate ('int' or 'uuid')
        start_id (int): Starting number for integer sequence
        prefix (str): Optional prefix for generated IDs
    """

    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        """Initialize ID generation pipe with configuration.

        Args:
            config (Dict[str, Union[str, int]]): Configuration containing:
                id_type (str): Type of ID to generate
                start_id (int): Starting number for sequence
                prefix (str): Optional ID prefix
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args: Any) -> pd.DataFrame:
        """Execute the ID generation pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with added ID column
        """
        Log.info("Starting AddIdPipe")

        id_type = self.config.get("id_type", "int")
        start_id = self.config.get("start_id", 1)
        prefix = self.config.get("prefix", "")

        if id_type == "uuid":
            ids = [f"{prefix}{str(uuid.uuid4())}" for _ in range(len(df))]
        else:
            ids = [f"{prefix}{i}" for i in range(start_id, len(df) + start_id)]

        df.insert(0, 'id', ids)

        Log.info(f"Added unique {id_type} identifiers as the first column.")
        Log.info("Finished AddIdPipe")

        return df

    @classmethod
    def _validate_config(cls, config: Dict[str, Union[str, int]]) -> None:
        """Validate pipe configuration.

        Args:
            config (Dict[str, Union[str, int]]): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            return

        id_type = config.get("id_type", "int")
        if id_type not in ["int", "uuid"]:
            raise ValueError("id_type must be 'int' or 'uuid'")

        start_id = config.get("start_id", 1)
        if not isinstance(start_id, int) or start_id < 1:
            raise ValueError("start_id must be a positive integer")
