# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-1-1

### Added
- Add `logger` and `dotenv` decorators to `clean`, `download`, `load`, and `prepare` commands
- Implement progress tracking with `tqdm` for data preprocessing pipes
- Enhance logging for better traceability and human-readable output
- Support `auto` column detection for `RemoveDuplicatesPipe` and `HandleMissingValuesPipe`
- Added `remove_partials` and `allow_empty` configurations for `HandleMissingValuesPipe`
- Improve error handling for missing columns in preprocessing pipes
- Break down `_process_file` into smaller private methods within `Pipeline` class
- Introduce `Pipe` and `Pipeline` classes with dynamic pipe loading
- Support dynamic loading of processing pipes based on user-defined types
- Updated prompt template for project guidelines with detailed sections

### Fixed
- Ensure robust error handling and accurate logging with correct timestamp format
- Resolved deprecation warnings and ensured maintainable code

### Changed
- Rename `run_flows` method to `open` in `Pipeline` class to align with pipe metaphor
- Refactor `Pipeline` class for improved modularity and encapsulation
- Improved `dataset_config.yaml` structure for better clarity and flexibility
- Updated CLI commands (`prepare`, `download`) to utilize new pipeline methods
- Enhanced documentation for improved clarity and readability

## [Unreleased] - 2024-12-31

### Added
- Add `logger` decorator to `clean`, `download`, `load`, and `prepare` commands
- Modify `dotenv` decorator to correctly handle logger setup
- Update `files.py` to include `log` argument in `make_dir` and `remove_dir` methods
- Enhance logging to use module classpath with dot notation
- Add detailed logging for steps in the load process
- Add `thinking_dataset/utilities/log.py` for unified logging with timestamps
- Implement `Pipe` and `Pipeline` classes with dynamic pipe loading
- Integrated new `Pipe` and `Pipeline` classes into `preprocess.py` CLI command
- Add sections for `huggingface`, `database`, `paths`, and `files` in `dataset_config.yaml`
- Add comprehensive unit tests for new features and operations
- Add support for dynamic loading of processing pipes based on user-defined types
- Include display names and descriptions for better identification of processing steps

### Fixed
- Fix database name formatting issue in `DatasetConfig`
- Fixed issues with dynamic pipe class loading in `command_utils.py`
- Improve error handling and type annotations across various modules
- Ensure thorough logging at each step for better traceability and debugging
- Enhanced error handling in `DatabaseSession` and `Database` classes
- Improved `GetFileList` operation to handle dataset configuration properly
- Gracefully exit on file list retrieval errors to maintain consistency
- Updated error reporting to match previous functions and simplified logging without rich traces
- Ensured environment variables were loaded and validated successfully
- Ensure correct file paths and use local file system for listing files

### Changed
- Refactor exception handling to use `log` parameter
- Refactor `BaseDataset` to use processed directory for loading files
- Ensure proper database creation and loading of prepared parquet files
- Improve file path construction in `Files` class
- Remove unnecessary filtering for local files in the load process
- Ensure accurate logging messages with correct timestamp format
- Refactored `thinking_dataset/io/files.py` to accept dataset config object for encapsulated logic
- Renamed `touch` method to `make_dir` for clarity
- Added full path construction using `self.config.ROOT_DIR`
- Updated methods for consistency and modularity
- Utilize dataset configuration paths for constructing file paths in preprocess and download commands
- Create raw data directory if it doesn't exist in preprocess command
- Improve logging to debug file paths and directory contents in preprocess command
- Improved logging for better traceability in download command
- Rename method `load_data` to `read_data` in `command_utils.py` for consistency
- Add `get_raw_path` method to `files.py` to construct raw data paths with multiple components
- Improve directory and file management methods in `files.py`
- Ensure correct file handling and error management in preprocess command
- Reorganized dataset config structure for better clarity and flexibility
- Consolidated ROOT_DIR, DATA_DIR, and DB_DIR into `paths` section in `dataset_config.yaml`
- Grouped INCLUDE_FILES and EXCLUDE_FILES into `files` section in `dataset_config.yaml`
- Added `huggingface` and `database` sections in `dataset_config.yaml` for better organization
- Updated `DatasetConfig` class to parse new configuration structure
- Updated `BaseDataset` class to utilize paths from the new configuration structure
- Updated `download.py` command to correctly construct paths and apply filters
- Updated `load.py` command to correctly apply and utilize filters when loading datasets
- Refactored `CommandUtils` to include environment variable handling and path construction
- Combined `try-except` blocks in `download.py`, `load.py`, and `clean.py` for better error handling
- Ensured `clean.py` uses paths from `dataset_config.yaml` instead of environment variables
- Enhanced logging to track the flow of operations and error handling more effectively
- Updated changelog with recent changes and refactor details
- Enhanced most recent work template to reflect new operations, features, and fixed issues
- Consolidated documentation to improve clarity and readability
- Improved logging and error handling across various components
- Refined database and session handling for better performance
- Ensured all changes adhere to coding standards and style guidelines
- Updated the prompt template for better clarity and comprehensiveness
- Rewrote all documentation with the latest knowledge, including INSTALLATION.md, DEPLOYMENT.md, TESTING.md, TROUBLESHOOTING.md, FAQ.md, and PIPELINE.md
- Enhanced the changelog to reflect all recent updates and improvements

## [Unreleased] - 2024-12-30

### Added

- Implemented a new `Log` class for unified logging across the project.
- Configured `RichHandler` for rich logging and pretty errors.
- Ensured consistent formatting in log messages with customizable time format including milliseconds.
- Improved error handling in `DataTonic` and `Dataset` classes.
  - Added detailed exception logging with rich traceback.
  - Ensured the logger is initialized before any operation in the `Dataset` class.
  - Handled missing configuration errors gracefully with clear error messages and immediate exits.
- Fixed issues with repetitive log entries and improved log output clarity.
- Customized log messages to display the file name and line number on the right side.
- Enhanced the `download.py` script to exit on critical errors and validate environment variables efficiently.
- Improved the readability of log outputs by including only relevant information and removing redundancy.
- Added stack traces to error logs without disrupting existing formatting and style.
- Ensured all modifications maintain the project’s coding standards and style guidelines.
- Added `db_dir` to our `env.sample` for database directory configuration.
- Refactored database and session handling for better performance and readability.
- Created `dataset.py` class to encapsulate dataset operations.
- Updated connector logic and created YAML configurations for dataset and database configurations.
- Updated `load` and `download` commands to reflect the new logic and configurations.
- Implemented the `load` command to load downloaded dataset files into SQLite database.
- Updated `Files` class to include file extension filtering using `HF_DATASET_TYPE` from .env.
- Enhanced the `load` command to queue parquet files and process each one.
- Created unit tests for the `Files` class, including extension filtering.
- Added high-level tests for the `load` command in `test_main_function.py`.
- Created `test_load.py` to test the `load` command, ensuring proper functionality.
- Updated coverage reports to reflect new tests and enhancements.
- Implemented the `DatabaseConfig` class for storing database configuration.
- Added a validate method to ensure all configuration settings are valid.
- Created unit tests for instantiation, validation, default values, invalid data types, and edge cases.
  - Tested initialization of `DatabaseConfig` with valid and invalid configurations.
  - Verified default values are set correctly when config options are omitted.
  - Ensured invalid data types for configuration settings raise appropriate errors.
  - Tested edge cases for numerical values such as 0 for pool_size, max_overflow, connect_timeout, and read_timeout.
- Updated test fixtures and mocks for `ConfigLoader` to simulate different configuration scenarios.
- Improved test coverage for the `DatabaseConfig` class to ensure robustness and reliability.
- Refactored and enhanced `BaseDataset` class to leverage DataTonic operations for dataset information retrieval and file listing.
- Fixed errors in dataset download by replacing deprecated function calls with new operations.
- Updated `GetInfo` operation to handle missing keys gracefully.
- Modified `GetDownloadUrls` to use DataTonic's `get_info` operation for retrieving dataset information.
- Improved logging consistency across `BaseDataset`, `GetDownloadFile`, and other operations to ensure clear and structured logs.
- Removed `tqdm` to fix double logging of progress bars and ensure proper text alignment.
- Updated `clean.py` script to use Log setup similar to `download.py` for consistent logging.
- Organized and cleaned DataTonic class by initializing all operations, ensuring modularity and maintainability.
- Validated and printed environment configuration for better debugging and operational transparency.

## [Unreleased] - 2024-12-31

### Added
- Implemented a new `Log` class for unified logging across the project.
- Configured standard logging with timestamps for better traceability.
- Ensured all log messages, including those from SQLAlchemy, are prefixed with timestamps.
- Verified that the CLI load command works with proper logging and error messages.

### Fixed
- Addressed potential issues with the log handler configurations to avoid errors during logging.

### Recent Work
- Refactored and enhanced `BaseDataset` class to leverage DataTonic operations for dataset information retrieval and file listing.
- Fixed errors in dataset download by replacing deprecated function calls with new operations.
- Updated `GetInfo` operation to handle missing keys gracefully.
- Modified `GetDownloadUrls` to use DataTonic's `get_info` operation for retrieving dataset information.
- Improved logging consistency across `BaseDataset`, `GetDownloadFile`, and other operations to ensure clear and structured logs.
- Removed `tqdm` to fix double logging of progress bars and ensure proper text alignment.
- Updated `clean.py` script to use Log setup similar to `download.py` for consistent logging.
- Organized and cleaned DataTonic class by initializing all operations, ensuring modularity and maintainability.
- Validated and printed environment configuration for better debugging and operational transparency.

## [Unreleased] - 2024-12-29

### Added
- Created `VolumeManager` class to manage multiple SQLite database volumes.
- Implemented tests for `VolumeManager` class, ensuring correct volume creation and management.
- Added debug statements in `VolumeManager` for troubleshooting volume creation.

### Changed
- Refactored `VolumeManager` class to ensure proper initialization and volume switching logic.
- Refactored `Database` class to centralize database management and session handling.
- Created `Query` operation class to handle executing queries on the database.
- Created `FetchData` operation class to handle fetching data from the database.

### Added
- Created `GetPermissions` operation class.
- Created tests for `GetPermissions` operation.

### Added
- Created `GetDownloadUrls` operation class.
- Created tests for `GetDownloadUrls` operation.
- Added `GetFileList` operation class.
- Created tests for `GetFileList` operation.

### Changed
- Refactored `DatasetDownloads` class to remove deprecated methods.
- Updated `OperationTypes` enum to include new operations.
- Updated unit tests for `OperationTypes`.
- Moved dataset download logic to `commands/download.py`.

### Fixed
- Updated test for `GetFileList` to reflect actual module names in log messages.
- Corrected import paths and usage in test files to avoid real API calls.
- Updated test for `FetchData` to ensure accurate data retrieval.
- Corrected import paths and usage in test files to avoid real API calls.

## [Unreleased] - 2024-12-26

### Added
- Implemented structured comments and documentation across multiple scripts.
- Added tests for `activate_venv.py` and `run_tests_and_generate_report.py`.
- Integrated `rich` for enhanced console output and error handling.
- Set up SQLite as the central source of truth for data storage.

### Changed
- Refactored project structure for better readability and maintenance:
  - Enhanced error handling, structured logging, and console outputs in `download.py`.
  - Reorganized directory paths and class functions in `files.py` and `clean.py`.
  - Added robust directory permission handling in `clean.py`.
  - Updated environment configuration with `ROOT_DIR` and `DATA_DIR`.
  - Adjusted line lengths to adhere to PEP8 and flake8 standards.

### Fixed
- Corrected import error and updated test paths in `test_files.py` to resolve ImportError issues.
- Resolved `TypeError` in `get_dataset_download_urls` method by providing required `dataset_id` argument.

## [Unreleased] - 2024-10-29

### Added
- Discussed and planned the setup for cross-platform builds for Windows and Linux.
- Successfully built standalone executables for both Windows and Linux.
- Explored the idea of using devcontainers for consistent development environments.
- Reviewed Python scripts provided by a colleague to understand the desired functionality and user story.
- Planned how to replicate the logic from the Python scripts in our Semantic Kernel system.
- Created a development notes text file to keep track of our progress in a structured way.
- Added details about our system design, phases, and data structure to the development notes.

### Changed
- Decided to start by creating unit tests to prototype basic Ollama functionality.
- Planned to take a break and watch some episodes of SG1 for inspiration and to think about future actions.

### Fixed
- N/A

## [Unreleased] - 2024-10-28

### Added
- Created `ThinkingDatasetProject` directory.
- Installed Semantic Kernel and Ollama connector.
- Updated `.csproj` to target .NET 8.0.
- Cleared NuGet cache and did a clean build.
- Successfully restored and built the project with all dependencies.
- Discussed and planned the use of Serilog for logging with color output for readability.
- Explored the use of MediatR for an event-driven architecture to ensure loose coupling and scalability.
- Next steps: Start developing unit tests for basic Ollama functionality.

### Changed
- N/A

### Fixed
- N/A
