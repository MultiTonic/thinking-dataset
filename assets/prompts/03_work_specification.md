## Overview

This template provides a detailed specification for implementing a new feature: a system for pushing processed data into the HF API dataset. The goal is to simplify the process by adding parquet files generated from our data/processed directory and ensuring a high-level configuration in the dataset YAML config.

## Specification Details

### 1. Class Definition

Add features to the `DataTonic` class to handle the uploading of processed parquet files to the HF API dataset.

### 2. Configuration

The configuration for this new system will include the following:
- **include_files**: Specific data to be included in the upload.
- **exclude_files**: Specific data to be excluded from the upload.

### 3. Implementation

- **Class Name**: `DataTonic`
- **File Path**: `thinking_dataset/tonics/data_tonic.py`
- **Description**: Add features to `DataTonic` class for uploading processed parquet files to the HF API dataset.
- **Version**: 1.0.0
- **License**: MIT

### 4. DataTonic Class

The `DataTonic` class should be extended as follows:

#### Algorithms and Pseudocode

1. **Initialize the DataTonic Class**:
    - Load configuration properties.

    ```pseudo
    CLASS DataTonic:
        FUNCTION __init__(config):
            self.config = config
    ```

2. **Push Processed Files**:
    - Read include/exclude files from config.
    - Iterate through processed directory.
    - Apply filters to include/exclude files.
    - Upload each valid file.

    ```pseudo
    FUNCTION push(processed_dir):
        INCLUDE_FILES = CONFIG.get("include_files")
        EXCLUDE_FILES = CONFIG.get("exclude_files")

        FOR EACH FILE IN processed_dir:
            IF FILE not IN EXCLUDE_FILES AND (INCLUDE_FILES is EMPTY OR FILE IN INCLUDE_FILES):
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

Integrate the extended `DataTonic` class into the existing workflow to ensure it processes and uploads the data files effectively. The new system will use configuration similar to the download system to manage include/exclude files.

## Itemized Task Todo List

| Task Overview                                           | Completed |
|---------------------------------------------------------|-----------|
| **Update Configuration Files**                          | ✅        |
| Move database config into `config.yaml`.                | ✅        |
| Move `HF_HOME` and `HF_DATASET` into `config.yaml`.     | ✅        |
| Remove the two env config properties and replace them with a single config path. | ✅ |
| **Modify Code to Read from Updated Configuration**      | ✅        |
| Ensure all relevant parts of the codebase read from the new `config.yaml` configuration. | ✅        |
| **Implement Database Export Functionality**             |           |
| Extract data from the database.                         |           |
| Convert extracted data to a DataFrame.                  |           |
| Apply include/exclude filters.                          |           |
| **Convert DataFrame to Parquet Files**                  |           |
| Save these parquet files in the processed directory.    |           |
| **Create the `DataTonic` Class for All Processing Tasks** |        |
| Develop methods for all necessary tasks within `DataTonic`, including data pushing. | ✅        |
| **Integrate the `DataTonic` Class into the Existing Workflow** |     |
| Replace existing implementations with the new `DataTonic` class methods. | ✅           |
| **Update Pipeline Configuration**                       |           |
| Ensure the updated configuration and new class are integrated correctly. | ✅           |
| **Develop and Run Comprehensive Unit Tests**            |           |
| Create unit tests to cover all new functionalities.     |           |
| **Verify the Functionality of the `DataTonic` Class**   |           |
| Make sure all methods in the `DataTonic` class work as expected. | ✅           |
| **Ensure Proper Handling of Configuration Properties**  |           |
| Verify that all properties are read and applied correctly. | ✅           |
| **Update the Documentation with Changes and New Options** | ✅        |
| Reflect all recent changes in the documentation, ensuring clarity and completeness. | ✅           |
| **Reflect Recent Changes in the Changelog**             |           |
| Document all changes and improvements for easy tracking.|           |
| **Ensure All Responses and Information are Verified and Grounded** | ✅           |
| Maintain accuracy and reliability in all code and documentation. | ✅        |

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