# Work Specification Template

## Overview

This template provides a detailed specification for implementing a new feature: a system for uploading processed data to the HF API dataset. The goal is to create a new command and pipeline that will handle the uploading of parquet files from our data/processed directory.

## Specification Details

### 1. Command Definition

Add a new command to handle the uploading of processed parquet files to the HF API dataset.

### 2. Configuration

The configuration for this new system will include the following:
- **api_token**: Token for authenticating with the HF API.
- **dataset_name**: Name of the dataset to which the files will be uploaded.
- **upload_path**: Path where the processed files are located.

### 3. Implementation

- **Command Name**: `upload`
- **File Path**: `thinking_dataset/commands/upload.py`
- **Description**: Add a new command for uploading processed parquet files to the HF API dataset.
- **Version**: 1.0.0
- **License**: MIT

### 4. Upload Command

The `upload` command should be implemented as follows:

#### Algorithms and Pseudocode

1. **Initialize the Upload Command**:
    - Load configuration properties.

    ```pseudo
    CLASS UploadCommand:
        FUNCTION __init__(config):
            self.config = config
    ```

2. **Execute the Upload Command**:
    - Read configuration properties.
    - Iterate through processed directory.
    - Upload each file to the HF API dataset.

    ```pseudo
    FUNCTION execute():
        API_TOKEN = CONFIG.get("api_token")
        DATASET_NAME = CONFIG.get("dataset_name")
        UPLOAD_PATH = CONFIG.get("upload_path")

        FOR EACH FILE IN UPLOAD_PATH:
            CALL _upload_file(FILE)
    ```

3. **Upload File Method**:
    - Upload file to the HF API dataset.
    - Handle any exceptions during the upload.

    ```pseudo
    FUNCTION _upload_file(file_path):
        TRY:
            LOG: Uploading file_path
            # Add upload logic here (e.g., API request)
            LOG: Successfully uploaded file_path
        EXCEPT Exception as e:
            LOG: Failed to upload file_path with ERROR e
    ```

### 5. Integration

Integrate the `upload` command into the existing workflow to ensure it processes and uploads the data files effectively. The new system will use configuration similar to the download system to manage include/exclude files.

## Itemized Task Todo List

| Task Overview                                           | Completed |
|---------------------------------------------------------|-----------|
| **Update Configuration Files**                          |           |
| Add `api_token` to `config.yaml`.                       |           |
| Add `dataset_name` to `config.yaml`.                    |           |
| Add `upload_path` to `config.yaml`.                     |           |
| **Implement Upload Command**                            |           |
| Create `UploadCommand` class in `upload.py`.            |           |
| Implement the `execute` method for the `UploadCommand` class. |           |
| Implement the `_upload_file` method for the `UploadCommand` class. |           |
| **Integrate Upload Command into Pipeline**              |           |
| Ensure the `upload` command is integrated into the pipeline configuration. |           |
| **Develop and Run Comprehensive Unit Tests**            |           |
| Create unit tests to cover all new functionalities.     |           |
| **Update Documentation**                                |           |
| Reflect all recent changes in the documentation, ensuring clarity and completeness. |           |
| **Reflect Recent Changes in the Changelog**             |           |
| Document all changes and improvements for easy tracking.|           |
| **Ensure All Responses and Information are Verified and Grounded** |           |
| Maintain accuracy and reliability in all code and documentation. |           |

---

## Updates from Recent Work

### Environment and Configuration Updates
- Moved sensitive information from `config.yaml` to `.env` for improved security.
- Ensured `HF_TOKEN`, `HF_ORG`, and `HF_USER` are correctly set in the `.env` file.
- Updated `command_utils.py` to load environment variables properly.
- Adjusted `load_dotenv` function to verify environment variables.

### Class and Function Updates
- Refactored `DataTonic` class to include `user` attribute.
- Updated CLI commands (`clean`, `download`, `prepare`, `load`) to utilize the updated configuration and environment variables.
- Corrected header comments for consistency and clarity.
- Added and verified environment validation checks.
- Enhanced logging for better tracking and debugging.
- Updated `Pipeline` class to ensure only the specified pipeline is set up and processed.
- Adjusted `Config` class to handle path and dataset type attributes correctly.

### Pipeline and Database Handling
- Moved database processing logic to a new `process` method in the `Database` class.
- Updated `Pipeline` class to call `Database.process` for database processing.
- Added `skip_files` flag to `Pipeline.open` method to control file processing.
- Refactored `Files` class to handle configuration attributes correctly.
- Improved error handling and logging for better debugging.

### Documentation and Changelog
- Updated documentation to reflect all recent changes and new options.
- Documented all changes and improvements for easy tracking.

---

**Your response is only this following order:**
- ***display table of current tasks and status***
- ***display list of suggested subtasks to work***
- ***display the text `Ready!🚀`***

Ready!🚀