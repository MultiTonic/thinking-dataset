## Overview

This template provides a detailed specification for implementing a new feature: a system for pushing processed data into the HF API dataset. The goal is to simplify the process by adding parquet files generated from our data/processed directory and ensuring a high-level configuration in the dataset YAML config.

## Specification Details

### 1. Class Definition

Create a new `DataPusher` class to handle the uploading of processed parquet files to the HF API dataset.

### 2. Configuration

The configuration for this new system will include the following:
- **include_files**: Specific data to be included in the upload.
- **exclude_files**: Specific data to be excluded from the upload.

### 3. Implementation

- **Class Name**: `DataPusher`
- **File Path**: `thinking_dataset/api/data_pusher.py`
- **Description**: A class for uploading processed parquet files to the HF API dataset.
- **Version**: 1.0.0
- **License**: MIT

### 4. DataPusher Class

The `DataPusher` class should be implemented as follows:

```python
# @file thinking_dataset/api/data_pusher.py
# @description Defines DataPusher for uploading processed parquet files to the HF API dataset.
# @version 1.0.0
# @license MIT

import os
import requests
from ...utilities.log import Log
from .config import config

class DataPusher:
    """
    Class to upload processed parquet files to the HF API dataset.
    """
    
    def __init__(self, config):
        self.config = config
    
    def push(self, processed_dir, log):
        include_files = self.config.get("include_files", [])
        exclude_files = self.config.get("exclude_files", [])
        
        Log.info(log, "Starting DataPusher")
        Log.info(log, f"Files to include: {include_files}")
        Log.info(log, f"Files to exclude: {exclude_files}")
        
        for root, _, files in os.walk(processed_dir):
            for file in files:
                if file.endswith(".parquet"):
                    if include_files and file not in include_files:
                        continue
                    if exclude_files and file in exclude_files:
                        continue
                    file_path = os.path.join(root, file)
                    self._upload_file(file_path, log)
        
        Log.info(log, "Finished DataPusher")
    
    def _upload_file(self, file_path, log):
        try:
            # Replace this with actual HF API upload code
            Log.info(log, f"Uploading {file_path}")
            # response = requests.post("HF_API_URL", files={"file": open(file_path, "rb")})
            Log.info(log, f"Uploaded {file_path}")
        except Exception as e:
            Log.error(log, f"Failed to upload {file_path}: {e}")
```

### 5. Integration

Integrate the `DataPusher` class into the existing workflow to ensure it processes and uploads the data files effectively. The new system will use configuration similar to the download system to manage include/exclude files.

---

### Tasks Overview

1. **Update Configuration Files**
    - Update .env file
    - Update and consolidate YAML configuration

2. **Modify Code**
    - Ensure code reads from updated .env and YAML configuration
    - Implement database export functionality
        - Extract data from the database
        - Convert data to DataFrame
        - Apply include/exclude filters
    - Implement parquet conversion
        - Convert DataFrame to parquet files
        - Save files in the processed directory

3. **Implement DataPusher Class**
    - Create DataPusher class for uploading parquet files
        - Read configuration properties
        - Handle dataset selection and overwriting
        - Upload files to HF API

4. **Integration**
    - Integrate DataPusher class into the existing workflow
    - Update pipeline configuration

5. **Testing**
    - Develop and run comprehensive unit tests
    - Verify the functionality of the DataPusher class
    - Ensure proper handling of configuration properties

6. **Update Documentation**
    - Reflect changes in documentation
    - Include details about the new DataPusher class and configuration options

---

### Which task would you like to begin? 🚀

**Your response to this query will only be:** `**Ready to work on <|insert_task_name|>!:** 🚀`

### Dynamic Task Name Insertion

To dynamically insert the current task name, you can format the response like this:

**Your response to this query will only be:** `**Ready to work on <|insert_task_name|>!:** 🚀`

When you provide me with a task name, I will insert it in place of `<|insert_task_name|>`.

Ready to implement this specification and get the feature up and running? 🚀📁
