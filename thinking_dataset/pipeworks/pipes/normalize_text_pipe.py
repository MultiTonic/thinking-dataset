"""Text Normalization Pipeline Module.

This module provides functionality for normalizing text data through various
cleaning and standardization operations.

Functions:
    None

Classes:
    NormalizeTextPipe: Handles text normalization operations.
"""

from typing import Dict, List, Optional, Callable

import pandas as pd

from thinking_dataset.utils.log import Log
from thinking_dataset.utils.text_utils import TextUtils as Text
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class NormalizeTextPipe(Pipe):
    """Pipe for normalizing text data through multiple operations.

    This pipe:
    1. Converts text to lowercase
    2. Removes headers and unnecessary sections
    3. Expands contractions and terms
    4. Normalizes numbers and special characters
    5. Cleans up whitespace and formatting
    6. Supports multi-threaded processing

    Config:
        columns (List[str]): Columns to normalize
        contractions (Dict[str, str]): Contraction mappings
        terms (Dict[str, str]): Term expansion mappings
    """

    def __init__(self, config: dict) -> None:
        """Initialize text normalization pipe with configuration.

        Args:
            config (dict): Configuration containing:
                columns (List[str]): Columns to process
                contractions (Dict[str, str]): Contraction mappings
                terms (Dict[str, str]): Term mappings
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the text normalization pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with normalized text
        """
        Log.info("Starting NormalizeTextPipe")

        columns = self.config.get("columns", [])
        contractions = self.config.get("contractions", {})
        terms = self.config.get("terms", {})

        normalize_func = self._create_normalizer(contractions, terms)

        self._log_start(columns)
        df = self._process_columns(df, columns, normalize_func)

        Log.info("Finished NormalizeTextPipe")
        return df

    @classmethod
    def _validate_config(cls, config: Optional[dict] = None) -> None:
        """Validate pipe configuration.

        Args:
            config (Optional[dict]): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            return

        columns = config.get("columns", [])
        if not isinstance(columns, list):
            raise ValueError("Columns must be specified as a list")

        contractions = config.get("contractions", {})
        if not isinstance(contractions, dict):
            raise ValueError("Contractions must be specified as a dictionary")

        terms = config.get("terms", {})
        if not isinstance(terms, dict):
            raise ValueError("Terms must be specified as a dictionary")

    @classmethod
    def _log_start(cls, columns: List[str]) -> None:
        """Log initialization details.

        Args:
            columns (List[str]): Columns to be processed
        """
        Log.info(f"Columns to normalize: {columns}")

    @classmethod
    def _process_columns(cls, df: pd.DataFrame, columns: List[str],
                         normalize_func: Callable[[str], str]) -> pd.DataFrame:
        """Process all specified columns with normalization function.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to process
            normalize_func (Callable[[str], str]): Normalization function

        Returns:
            pd.DataFrame: DataFrame with normalized text
        """
        for col in columns:
            df[col] = cls._normalize_column(df[col], normalize_func, col)
        return df

    @classmethod
    def _normalize_column(cls, series: pd.Series,
                          normalize_func: Callable[[str], str],
                          column_name: str) -> pd.Series:
        """Normalize a single column using multi-threading.

        Args:
            series (pd.Series): Column data to normalize
            normalize_func (Callable[[str], str]): Normalization function
            column_name (str): Name of column being processed

        Returns:
            pd.Series: Normalized column data
        """
        return cls.multi_thread_apply(series=series,
                                      func=normalize_func,
                                      desc=f"Normalizing {column_name}")

    @staticmethod
    def _create_normalizer(contractions: Dict[str, str],
                           terms: Dict[str, str]) -> Callable[[str], str]:
        """Create text normalization function with configured mappings.

        Args:
            contractions (Dict[str, str]): Contraction expansion mappings
            terms (Dict[str, str]): Term expansion mappings

        Returns:
            Callable[[str], str]: Text normalization function
        """

        def normalize_text(text: str) -> str:
            """Apply all normalization steps to input text."""
            if not isinstance(text, str):
                return str(text)

            text = text.lower()
            text = Text.remove_partial_extract_intro(text)
            text = Text.remove_header(text)
            text = Text.remove_initial_pattern(text)
            text = Text.remove_tiny_parentheses_content(text)
            text = Text.remove_separators(text)
            text = Text.remove_special_characters(text)
            text = Text.expand_contractions(text, contractions)
            text = Text.expand_terms(text, terms)
            text = Text.remove_section_headers(text)
            text = Text.remove_signoff(text)
            text = Text.remove_period_patterns(text)
            text = Text.normalize_numbers(text)
            text = Text.normalize_spaced_characters(text)
            text = Text.remove_weird_ids(text)
            text = Text.remove_weird_dates(text)
            text = Text.remove_whitespace(text)
            return text

        return normalize_text
