# @file thinking_dataset/pipeworks/pipes/file_extractor_pipe.py
# @desc Extracts files from a directory based on a filter.
# @version 1.0.4
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files
from thinking_dataset.utils.text_utils import TextUtils as utils


class FileExtractorPipe(Pipe):
    """
    Pipe for extracting files from a directory with filtering.

    This pipe:
    1. Recursively scans specified directory path
    2. Filters files based on extension configuration
    3. Creates DataFrame with file information
    4. Assigns unique IDs to each file

    Config:
        path (str): Directory path to scan
        filter (str): File extension to filter by
    """

    def flow(self, df: None, **args) -> pd.DataFrame:
        Log.info("Starting FileExtractorPipe")

        path = self.config.get("path", "")
        filter_extension = self.config.get("filter", "")

        Log.info(f"Path to extract files from: {path}")
        Log.info(f"Filter extension: {filter_extension}")

        if not path:
            raise ValueError("Path is required for FileExtractorPipe")

        extracted_files = Files.list_files_recursive(path, filter_extension)

        Log.info(f"Total extracted files: {len(extracted_files)}")

        df = pd.DataFrame({
            "id": range(1,
                        len(extracted_files) + 1),
            "file_path": extracted_files
        })

        Log.info("DataFrame created with the following columns:")
        for column in df.columns:
            Log.info(f"Column: {column}")

        for _, row in df.iterrows():
            file_id = row["id"]
            file_path = row["file_path"]
            Log.info(f"Row: {file_id} - {utils.shorten_path(file_path, 100)}")

        return df
