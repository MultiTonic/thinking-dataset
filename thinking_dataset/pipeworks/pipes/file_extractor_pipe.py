# @file thinking_dataset/pipeworks/pipes/file_extractor_pipe.py
# @desc Extracts files from a directory based on a filter.
# @version 1.0.3
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files


class FileExtractorPipe(Pipe):
    """
    Pipe to extract files from a specified directory based on a filter
    and return a DataFrame.
    """

    def flow(self, df: None, **args) -> pd.DataFrame:
        path = self.config.get("path", "")
        filter_extension = self.config.get("filter", "")

        Log.info("Starting FileExtractorPipe")
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

        Log.info("DataFrame content preview:")
        Log.info(df.head().to_string())

        return df
