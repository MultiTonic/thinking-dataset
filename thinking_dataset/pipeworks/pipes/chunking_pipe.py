"""Chunking Pipeline Module.

This module provides functionality for splitting input records into chunks
while avoiding orphan chunks.

Functions:
    None

Classes:
    ChunkingPipe: Handles splitting input records into chunks.
"""

from typing import Any, Dict, List

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class ChunkingPipe(Pipe):
    """Pipe to chunk input records while avoiding orphan chunks.

    This pipe:
    1. Validates column specifications
    2. Splits text into chunks based on specified sizes
    3. Maintains data integrity during processing

    Config:
        columns (List[str]): Columns to chunk
        max_chunk_size (int): Maximum size of each chunk
        min_chunk_size (int): Minimum size of each chunk
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize chunking pipe with configuration.

        Args:
            config (Dict[str, Any]): Configuration containing:
                columns (List[str]): Columns to chunk
                max_chunk_size (int): Maximum size of each chunk
                min_chunk_size (int): Minimum size of each chunk
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args: Any) -> pd.DataFrame:
        """Execute the chunking pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with chunked text
        """
        Log.info("Starting ChunkingPipe")

        columns = self.config.get("columns", [])
        max_chunk_size = self.config.get("max_chunk_size", 0)
        min_chunk_size = self.config.get("min_chunk_size", 0)

        Log.info(f"Columns to chunk: {columns}")
        Log.info(f"Max chunk size: {max_chunk_size}")
        Log.info(f"Min chunk size: {min_chunk_size}")

        chunked_df = self._chunk_dataframe(df, columns, max_chunk_size,
                                           min_chunk_size)

        Log.info("Finished ChunkingPipe")
        return chunked_df

    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate pipe configuration.

        Args:
            config (Dict[str, Any]): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            return

        columns = config.get("columns", [])
        if not isinstance(columns, list):
            raise ValueError("Columns must be specified as a list")

        max_chunk_size = config.get("max_chunk_size", 0)
        if not isinstance(max_chunk_size, int) or max_chunk_size < 0:
            raise ValueError("max_chunk_size must be a non-negative integer")

        min_chunk_size = config.get("min_chunk_size", 0)
        if not isinstance(min_chunk_size, int) or min_chunk_size < 0:
            raise ValueError("min_chunk_size must be a non-negative integer")

    @staticmethod
    def _chunk_text(text: str, max_chunk_size: int,
                    min_chunk_size: int) -> List[str]:
        """Chunk text into smaller pieces based on specified sizes.

        Args:
            text (str): Input text to chunk
            max_chunk_size (int): Maximum size of each chunk
            min_chunk_size (int): Minimum size of each chunk

        Returns:
            List[str]: List of chunked text pieces
        """
        chunks = []
        if max_chunk_size <= 0:
            chunks.append(text)
            return chunks

        while len(text) > max_chunk_size:
            chunk = text[:max_chunk_size]
            last_space = chunk.rfind(" ")
            if last_space != -1 and last_space >= min_chunk_size:
                chunk = chunk[:last_space]
            chunks.append(chunk)
            text = text[len(chunk):].strip()

        if text:
            chunks.append(text)
        return chunks

    @classmethod
    def _chunk_dataframe(cls, df: pd.DataFrame, columns: List[str],
                         max_chunk_size: int,
                         min_chunk_size: int) -> pd.DataFrame:
        """Chunk specified columns in the DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to chunk
            max_chunk_size (int): Maximum size of each chunk
            min_chunk_size (int): Minimum size of each chunk

        Returns:
            pd.DataFrame: DataFrame with chunked text
        """
        total_chunks = 0
        total_chunk_size = 0
        chunked_data = {col: [] for col in df.columns}

        for _, row in df.iterrows():
            for col in columns:
                chunks = cls._chunk_text(row[col], max_chunk_size,
                                         min_chunk_size)
                for chunk in chunks:
                    for other_col in df.columns:
                        if other_col not in columns:
                            chunked_data[other_col].append(row[other_col])
                    chunked_data[col].append(chunk)
                total_chunks += len(chunks)
                total_chunk_size += sum(len(chunk) for chunk in chunks)

        avg_chunk_size = (total_chunk_size //
                          total_chunks if total_chunks else 0)
        original_rows = len(df)
        new_chunks = total_chunks - original_rows
        chunked_df = pd.DataFrame(chunked_data)

        Log.info(f"Average chunk size: {avg_chunk_size} characters.")
        Log.info(f"Added {new_chunks} chunks ({total_chunks} total).")

        return chunked_df
