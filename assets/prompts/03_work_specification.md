# Work Specification Template

## Overview

This template outlines the implementation of new features, including a system for uploading process data to the HF API dataset and basic file and directory commands for interacting with the dataset repository. The objective is to develop commands and pipelines that will manage the uploading of parquet files from the `./data/process` directory and provide file management utilities.

## Specification Details

### 1. Command Definition

Add new commands to handle the uploading of process parquet files to the HF API dataset and basic file management operations.

### 2. Configuration

The configuration for these new systems will include the following:

- **write_token**: Token for authenticating with the HF API.
- **dataset_name**: Name of the dataset to which the files will be uploaded.
- **upload_path**: Path where the process files are located.
- **Other Configurations**: Dynamic variables for file and directory operations.

### 3. Implementation

Implement the `upload` command and file management commands to handle the uploading of process parquet files to the HF API dataset and provide file management utilities.

- **Command Names**: `upload`, `list_files`, `list_dirs`, `check_exists`, `create_dir`
- **File Paths**: 
  - `thinking_dataset/commands/upload.py`
  - `thinking_dataset/commands/files.py`
- **Description**: 
  - Add a new command for uploading process parquet files to the HF API dataset.
  - Add new commands for listing files, listing directories, checking if a file or directory exists, and creating a new directory.
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
    - Iterate through the processed directory.
    - Upload each file to the HF API dataset.

    ```pseudo
    FUNCTION execute():
        WRITE_TOKEN = CONFIG.get("write_token")
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

### 5. File Management Commands

Implement basic file and directory commands for interacting with the dataset repository:

1. **List All Files in the Repository**:
    - Command to list all files within a specified directory in the repo and output to the console.

2. **List All Directories in the Repository**:
    - Command to list all directories within a specified directory in the repo and output to the console.

3. **Check if File or Directory Exists**:
    - Command to check if a specific file or directory exists within the repo.

4. **Create a New Directory**:
    - Command to create a new directory within the repo.

### 6. Integration

Integrate the `upload` command and file management commands into the existing workflow to ensure they process and manage the data files effectively. The new system will use configuration similar to the download system to manage include/exclude files.

### 7. Focus on Current Work

Currently, we are focusing on:
- Creating a new pipeline called `upload` for uploading process data.
- Adding a `FileExtractorPipe` to handle directory access and file extraction.
- Adding a `FilterByNamePipe` to filter files by name.
- Adding an `UploadPipe` to handle the file upload process.
- Ensuring the configuration is updated to support dynamic variable resolution.
- Adding detailed objectives for logging, performance optimization, error handling, validation, feedback, documentation, and security.

### 8. Future Conversation

In our next conversation, please provide:
- Feedback on the implementation and any issues encountered.
- Additional requirements or enhancements for the upload pipeline.
- Any new features or changes to be incorporated based on current progress.

### Itemized Task Todo List

| Task Overview                                           | Completed |
|---------------------------------------------------------|-----------|
| **Support Dynamic Variables in Configuration**          | ✅         |
| Implement dynamic variable resolution in `config.py`.   | ✅         |
| **Implement Configurations for Each Pipe**              | ✅         |
| Configure `FileExtractorPipe` for directory access.     | ✅         |
| Configure `UploadFilePipe` for file uploads.            | ✅         |
| **Implement Upload Command**                            | 🚧 In Progress |
| Create `UploadCommand` class in `upload.py`.            | 🚧 In Progress |
| Implement the `execute` method for the `UploadCommand` class. | 🚧 In Progress |
| Implement the `_upload_file` method for the `UploadCommand` class. | 🚧 In Progress |
| **Integrate Upload Command into Pipeline**              | ✅         |
| **Update `run_cli_command.py` Script**                  | ✅         |
| **Set Up Logging and Monitoring**                       | ✅         |
| **Optimize Pipeline Performance**                       | 🚧 In Progress |
| **Enhance Error Handling and Reporting**                | ✅         |
| **Implement Configuration Validation**                  | ✅         |
| **Comprehensive Documentation**                         | 🚧 In Progress |
| Develop detailed user guides and API documentation.     | 🚧 In Progress |
| **Security Enhancements**                               | ✅         |

---

## Updates from Recent Work

### Environment and Configuration Updates
- Moved sensitive information from `config.yaml` to `.env` for improved security.
- Ensured `HF_WRITE_TOKEN`, `HF_ORG`, and `HF_USER` are correctly set in the `.env` file.
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

### New Features
- **Basic File and Directory Commands**:
    - Created commands to list files and directories, check if a file or directory exists, and create a new directory within the dataset repository.

### Documentation and Changelog
- Updated documentation to reflect all recent changes and new options.
- Documented all changes and improvements for easy tracking.

---

**Your response for this query is only this following order:**
- ***display table of current tasks and status***
- ***display list of suggested subtasks to work***
- ***display one short sentence what task we worked on last***
- ***display the text `Ready!🚀`***