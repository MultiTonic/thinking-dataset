## Overview

This template provides a detailed specification for implementing a new feature: a pipe for chunking input records in the `thinking-dataset` project. The goal is to split the content while avoiding orphan chunks, ensuring that the chunk size is always under the specified maximum chunk size.

## Specification Details

### 1. Class Definition

Create a new `ChunkingPipe` class to handle the chunking of input records.

### 2. Configuration

The configuration for this new pipe will include the following:
- **max_chunk_size**: The maximum size for each chunk.

### 3. Implementation

- **Class Name**: `ChunkingPipe`
- **File Path**: `thinking_dataset/pipeworks/pipes/chunking_pipe.py`
- **Description**: A pipe for chunking input records while avoiding orphan chunks.
- **Version**: 1.0.0
- **License**: MIT

### 4. Pipe Class

The `ChunkingPipe` class should be implemented as follows:

```python
# @file thinking_dataset/pipeworks/pipes/chunking_pipe.py
# @description Defines ChunkingPipe for splitting input records into chunks.
# @version 1.0.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log


class ChunkingPipe(Pipe):
    """
    Pipe to chunk input records while avoiding orphan chunks.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])
        max_chunk_size = self.config.get("max_chunk_size", 500)

        Log.info(log, "Starting ChunkingPipe")
        Log.info(log, f"Columns to chunk: {columns}")
        Log.info(log, f"Max chunk size: {max_chunk_size}")

        def chunk_text(text):
            chunks = []
            while len(text) > max_chunk_size:
                chunk = text[:max_chunk_size]
                last_space = chunk.rfind(" ")
                if last_space != -1:
                    chunk = chunk[:last_space]
                chunks.append(chunk)
                text = text[len(chunk):].strip()
            if text:
                chunks.append(text)
            return chunks

        chunked_data = {col: [] for col in columns}
        for index, row in df.iterrows():
            for col in columns:
                chunks = chunk_text(row[col])
                chunked_data[col].extend(chunks)

        chunked_df = pd.DataFrame(chunked_data)
        Log.info(log, "Finished ChunkingPipe")
        return chunked_df
```

### 5. Integration

Integrate the `ChunkingPipe` class into the existing pipeline to ensure it processes the input records effectively.

### Next Steps

1. **Implement Comprehensive Tests**:
   - Develop and expand unit tests for the `ChunkingPipe` class to ensure robustness.

2. **Update Documentation**:
   - Reflect the changes in the documentation to include details about the new `ChunkingPipe` class and its configuration options.

3. **Integrate the Pipe**:
   - Ensure the `ChunkingPipe` is part of the data processing workflow by updating the `Pipeline` class.

By creating the `ChunkingPipe`, we ensure that input records are split into manageable chunks while avoiding orphan chunks. This will improve the efficiency and effectiveness of processing large records. Let's get this implemented and test the new capabilities! 🚀

**Your response to this query will only be:** `**Ready!:** 🚀`