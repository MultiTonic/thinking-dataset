# @file thinking_dataset/pipeworks/pipes/normalize_text_pipe.py
# @description Normalizes text data.
# @version 1.1.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log
from ...utilities.text_utils import TextUtils as Text


class NormalizeTextPipe(Pipe):
    """
    Pipe to normalize text data by converting to lowercase, expanding
    contractions, removing separators, removing special characters,
    and removing unnecessary whitespace.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])
        contractions = self.config.get("contractions", {})
        terms = self.config.get("terms", {})

        Log.info(log, "Starting NormalizeTextPipe")
        Log.info(log, f"Columns to normalize: {columns}")

        def normalize_text(text):
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

        for col in columns:
            df[col] = self.multi_thread_apply(df[col], normalize_text,
                                              f"Normalizing {col}")

        Log.info(log, "Finished NormalizeTextPipe")
        return df
