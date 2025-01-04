"""
@file thinking_dataset/pipeworks/pipes/expand_terms_pipe.py
@description Defines ExpandTermsPipe for expanding abbreviations and acronyms.
@version 1.0.0
@license MIT
"""

import pandas as pd
from tqdm import tqdm
from .pipe import Pipe
from ...utilities.log import Log
from ...utilities.text_utils import TextUtils as Text


class ExpandTermsPipe(Pipe):
    """
    Pipe to expand abbreviations and acronyms in the text.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])
        terms = self.config.get("terms", {})

        Log.info(log, "Starting ExpandTermsPipe")
        Log.info(log, f"Columns to expand: {columns}")

        def expand_terms(text):
            text = Text.expand_terms(text, terms)
            text = Text.remove_whitespace(text)
            return text

        for col in columns:
            Log.info(log, f"Expanding terms in column: {col}")
            tqdm.pandas(desc=f"Expanding terms in {col}")
            df[col] = df[col].progress_apply(expand_terms)

        Log.info(log, "Finished ExpandTermsPipe")
        return df
