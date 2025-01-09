# @file thinking_dataset/pipeworks/pipes/chunking_pipe.py
# @description Defines ChunkingPipe for splitting input records into chunks.
# @version 1.3.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log


class ChunkingPipe(Pipe):
    """
    Pipe to chunk input records while avoiding orphan chunks.
    """

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])
        max_chunk_size = self.config.get("max_chunk_size", 0)
        min_chunk_size = self.config.get("min_chunk_size", 0)

        Log.info("Starting ChunkingPipe")
        Log.info(f"Columns to chunk: {columns}")
        Log.info(f"Max chunk size: {max_chunk_size}")
        Log.info(f"Min chunk size: {min_chunk_size}")

        def chunk_text(text):
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

        total_chunks = 0
        total_chunk_size = 0
        chunked_data = {col: [] for col in df.columns}
        for index, row in df.iterrows():
            for col in columns:
                chunks = chunk_text(row[col])
                for chunk in chunks:
                    for other_col in df.columns:
                        if other_col not in columns:
                            chunked_data[other_col].append(row[other_col])
                    chunked_data[col].append(chunk)
                total_chunks += len(chunks)
                total_chunk_size += sum(len(chunk) for chunk in chunks)

        if total_chunks == 0:
            avg_chunk_size = 0
        else:
            avg_chunk_size = total_chunk_size / total_chunks

        avg_chunk_size = round(avg_chunk_size)
        original_rows = len(df)
        new_chunks = total_chunks - original_rows
        chunked_df = pd.DataFrame(chunked_data)

        Log.info(f"Average chunk size: {avg_chunk_size} characters.")
        Log.info(f"Added {new_chunks} chunks ({total_chunks} total).")
        Log.info("Finished ChunkingPipe")

        return chunked_df
