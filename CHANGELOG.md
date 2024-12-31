# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Fixed
- Renamed test class in `tests/thinking_dataset/utilities/test_execute.py` to `ExampleClass` to avoid `PytestCollectionWarning`.
- Verified that all tests pass successfully without warnings.
- Generated and updated HTML report and coverage report.
- Ensured comprehensive test coverage for new and existing functionality.
- Updated scripts to consistently run tests, generate reports, and measure coverage.
- Confirmed all tests adhere to `flake8` formatting and PEP8 guidelines.

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
