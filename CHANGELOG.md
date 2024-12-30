# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2024-12-30

### Added
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
  - Test initialization of `DatabaseConfig` with valid and invalid configurations.
  - Verified default values are set correctly when config options are omitted.
  - Ensured invalid data types for configuration settings raise appropriate errors.
  - Tested edge cases for numerical values such as 0 for pool_size, max_overflow, connect_timeout, and read_timeout.
- Updated test fixtures and mocks for `ConfigLoader` to simulate different configuration scenarios.
- Improved test coverage for the `DatabaseConfig` class to ensure robustness and reliability.

### Fixed
- Renamed test class in `tests/thinking_dataset/utilities/test_execute.py` to `ExampleClass` to avoid `PytestCollectionWarning`.
- Verified that all tests pass successfully without warnings.
- Generated and updated HTML report and coverage report.
- Ensured comprehensive test coverage for new and existing functionality.
- Updated scripts to consistently run tests, generate reports, and measure coverage.
- Confirmed all tests adhere to `flake8` formatting and PEP8 guidelines.

### Added
- Implemented `Log` class in `thinking_dataset/utilities/log.py` for unified logging.
- Created `ConfigLoader` class in `thinking_dataset/utilities/config_loader.py` for loading configuration from YAML files.
- Added `execute` decorator in `thinking_dataset/utilities/execute.py` for executing database operations.
- Developed comprehensive unit tests for the `Log` class:
  - `tests/thinking_dataset/utilities/test_log.py`
  - Tested `info`, `error`, and `warn` logging methods.
  - Ensured exceptions are raised and log messages are captured.
- Created unit tests for the `execute` decorator:
  - `tests/thinking_dataset/utilities/test_execute.py`
  - Verified correct execution of mock operations and multiple calls.
- Added unit tests for the `ConfigLoader` class:
  - `tests/thinking_dataset/utilities/test_config_loader.py`
  - Tested loading valid configuration, file not found errors, YAML parsing errors, and retrieving non-existent sections.
- Ensured all tests pass successfully, adhering to `flake8` formatting and PEP8 guidelines.

### Added
- Initial project setup and database implementation.
- Added `DatabaseConfig` class for configuration management.
- Implemented `Database` class for database operations using SQLAlchemy.
- Created `Query` and `Fetch` classes for executing and fetching data.
- Added `GetSession` class for handling database sessions.
- Updated `ConfigLoader` class for loading YAML configuration.
- Added comprehensive YAML configuration file for the database.
- Improved and updated various documentation files:
  - `README.md`
  - `ARCHITECTURE.md`
  - `INSTALLATION.md`
  - `USAGE.md`
  - `TROUBLESHOOTING.md`
  - `FAQ.md`
  - `REFERENCES.md`
  - `IDEAS.md`
  - `DEVELOPMENT_NOTES.md`

- Added new sections and refined content in the documentation to enhance clarity and comprehensiveness.
- Added more detailed examples, new ideas, and expanded sections in `IDEAS.md` to cover a wider range of project enhancements.
- Updated `PROMPT_TEMPLATE.md` to reflect the latest changes and improvements in prompt templates for better AI model interactions.
- Revised the format, structure, and content of the documentation to ensure consistency and usability.
- Incorporated feedback and suggestions to refine the overall documentation quality and completeness.
- Refactored database handling and operations with FSM and decorators.
- Centralized database management in `Database` class with unified logging.
- Implemented session management using FSM (`SessionStateMachine`).
- Modularized database operations: `Query` and `Fetch`.
- Simplified operation execution with the `@execute` decorator.
- Ensured clean and concise code structure and maintainability.

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
