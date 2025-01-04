# Work Specification Template

## Overview

This template provides a detailed specification for implementing new features or specific changes to the project. In this case, it outlines the enhancement of the `Pipe` class to support multi-threaded processing.

## Specification Details

### 1. Class Definition

Enhance the existing base `Pipe` class to support multi-threaded processing of DataFrame columns.

### 2. Configuration

The configuration for this enhancement will not require changes to the existing configuration structure. The multi-threaded processing will be integrated seamlessly into the `Pipe` class.

### 3. Implementation

- **Class Name**: `Pipe`
- **File Path**: `thinking_dataset/pipeworks/pipes/pipe.py`
- **Description**: Enhance the base `Pipe` class to support multi-threaded processing.
- **Version**: 1.0.0
- **License**: MIT

### 4. Pipe Class

The `Pipe` class should be updated as follows:

```python
# @file project_root/thinking_dataset/pipeworks/pipes/pipe.py
# @description Defines BasePipe class for preprocessing tasks with logging and multi-threading support.
# @version 1.0.0
# @license MIT

import importlib
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from thinking_dataset.utilities.log import Log
from thinking_dataset.utilities.command_utils import CommandUtils as Utils


class Pipe(ABC):
    """
    Base class for preprocessing tasks.
    """

    def __init__(self, config: dict):
        self.config = config
        self.log = Log.setup(self.__class__.__name__)

    @abstractmethod
    def flow(self, df, log, **args):
        """
        Flow the DataFrame through the pipe. To be implemented by subclasses.
        """
        self.log.info(f"Flow -- {self.__class__.__name__}")
        pass

    @staticmethod
    def get_pipe(pipe_type):
        """
        Dynamically import and return the pipe class based on the pipe type.
        """
        module_name = "thinking_dataset.pipeworks.pipes." + Utils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError):
            raise ImportError(f"Error loading pipe class {pipe_type} from module {module_name}")

    def progress_apply(self, series, func, desc):
        """
        Apply a function to a pandas series with a progress bar.
        """
        tqdm.pandas(desc=desc)
        return series.progress_apply(func)

    def multi_threaded_apply(self, df, columns, func):
        """
        Apply a function to DataFrame columns using multi-threading.
        """
        def process_column(col):
            Log.info(self.log, f"Processing column: {col}")
            tqdm.pandas(desc=f"Processing {col}")
            df[col] = df[col].progress_apply(func)

        with ThreadPoolExecutor() as executor:
            executor.map(process_column, columns)
        return df
```

### 5. Integration

Integrate the enhanced `Pipe` class into existing pipes to ensure they leverage multi-threaded processing. Here’s how you can update the `NormalizeTextPipe` and `ExpandTermsPipe` classes:

#### `NormalizeTextPipe` Class

```python
# @file thinking_dataset/pipeworks/pipes/normalize_text_pipe.py
# @description Defines NormalizeTextPipe for normalizing text data.
# @version 1.0.0
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

        Log.info(log, "Starting NormalizeTextPipe")
        Log.info(log, f"Columns to normalize: {columns}")

        def normalize_text(text):
            text = text.lower()
            text = Text.expand_contractions(text, contractions)
            text = Text.remove_separators(text)
            text = Text.remove_special_characters(text)
            text = Text.normalize_numbers(text)
            text = Text.normalize_spaced_characters(text)
            text = Text.remove_partial_extract_intro(text)
            text = Text.remove_section_headers(text)
            text = Text.remove_initial_pattern(text)
            text = Text.remove_signoff(text)
            text = Text.remove_period_patterns(text)
            text = Text.remove_header(text)
            text = Text.remove_whitespace(text)
            return text

        df = self.multi_threaded_apply(df, columns, normalize_text)

        Log.info(log, "Finished NormalizeTextPipe")
        return df
```

#### `ExpandTermsPipe` Class

```python
# @file thinking_dataset/pipeworks/pipes/expand_terms_pipe.py
# @description Defines ExpandTermsPipe for expanding abbreviations and acronyms.
# @version 1.0.0
# @license MIT

import pandas as pd
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

        df = self.multi_threaded_apply(df, columns, expand_terms)

        Log.info(log, "Finished ExpandTermsPipe")
        return df
```

### Next Steps

1. **Implement Comprehensive Tests**:
   - Develop and expand unit tests for the `Pipe` class and derived pipes to ensure robustness.

2. **Update Documentation**:
   - Reflect the changes in the documentation to include multi-threaded processing capabilities.

3. **Integrate the Pipes**:
   - Ensure the multi-threaded pipes are part of the data processing workflow by updating the `Pipeline` class.

By enhancing the base `Pipe` class to support multi-threaded processing, we ensure all derived pipes benefit from this feature, improving overall performance and efficiency. Let’s get this integrated and test the new capabilities!
