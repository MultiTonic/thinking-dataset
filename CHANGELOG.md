# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-08

### Added
- Enhanced `ExportTablesPipe` to use `EXPORT_PATH` for output directory.
- Updated `Pipeline` class to use `PROCESS_PATH` and `RAW_PATH` for accurate file management.
- Added detailed changelog inventory following the standard specification.

### Changed
- Ensured downloaded files are saved in `data/raw` and not in the root directory.
- Fixed Database initialization to remove unexpected config argument in `load.py`.
- Adjusted `_process_file` method in `Pipeline` class to raise `FileNotFoundError` instead of logging a warning.
- Ensured consistent path separators using `os.path.join` across the project.
- Utilized `Config.get_value` and `Config.get_env_value` for fetching configuration values throughout the code.
- Reviewed and ensured consistency across all pipes for logging, configuration usage, return types, and error handling.
- Updated docstrings and inline comments for clarity and consistency across all relevant files.

### Fixed
- Successfully tested `prepare`, `load`, and `export` commands to ensure proper functionality.
- Verified the execution of pipeline stages and correct file placements.
- Fixed and enhanced various components of the pipeline to ensure files are placed correctly and commands execute without errors.
- Ensured proper initialization and usage of configuration values.
- Improved error handling and logging across the project.
- Verified the functionality through thorough testing and debugging.

## [Unreleased] - 2025-01-07

### Added
- Updated prompt template for project to include directives for avoiding code hallucination.
- Modified AI to ensure it asks users for more context instead of making assumptions.
- Corrected errors in the end of the prompt template.

### Fixed
- Enhanced prompt template to improve clarity and accuracy.

## [Unreleased] - 2025-01-06

### Added
- Created `upload` command and associated pipeline for uploading process parquet files to the HF API dataset.
- Added `FileExtractorPipe` for directory access and file extraction.
- Added `FilterByNamePipe` for filtering files by name.
- Added `UploadPipe` for handling the upload of files to HF API.
- Improved text normalization through `NormalizeTextPipe` class and `TextUtils` methods.
- Enhanced logging for tracking pipeline running time.
- Conducted comprehensive testing for text normalization and data cleaning.
- Refactored classes and methods for better performance and error handling.

### Changed
- Moved sensitive information from `config.yaml` to `.env` for improved security.
- Updated `command_utils.py` to load environment variables properly.
- Adjusted `load_dotenv` function for better environment variable verification.
- Refactored `DataTonic` class to include `user` attribute.
- Updated various CLI commands to utilize updated configuration and environment variables.
- Enhanced logging and error handling across multiple components.
- Enhanced `Log` class and configuration for better file handling and logging.
- Refined `Dataset` class to utilize `Files` methods and adhere to PEP 8 standards.

### Fixed
- Addressed errors in `Files` class and improved directory handling.
- Fixed sorting issues and progress bar updates in `Pipe` class.
- Improved error handling in `clean` and `load` commands.
- Verified and resolved multiple attribute errors and bugs in various components.
- Ensured SQLAlchemy logging levels are set to `CRITICAL`.

## [Unreleased] - 2025-01-05

### Added

- Updated prompt for working on the project.
- Revised README.md with new subheading, streamlined usage section, and citation format.
- Enhanced INSTALLATION.md with detailed setup steps and package management.
- Improved OVERVIEW.md with updated project goals and key features.
- Refined ARCHITECTURE.md with a clear structure and updated schema diagram.
- Expanded DATASETS.md with detailed dataset descriptions and comparison table.
- Updated DATABASE.md to highlight schema design and benefits.
- Enhanced PIPELINE.md with a comprehensive overview of pipeline phases and tools.
- Revised DEPLOYMENT.md with detailed deployment steps and process manager setup.
- Added REFERENCES.md with key academic papers, books, and external tools.
- Updated ROADMAP.md with detailed milestones and timeline for 2025.
- Refined CONTRIBUTING.md with clear guidelines for reporting bugs, suggesting enhancements, and submitting pull requests.
- Added CITATIONS section to README.md with proper citation format.
- Updated the work specification template to output task list.

### Changed

- Removed `self.log` assignment and switched to using `Log.info` directly in `SessionStateMachine` class.
- Removed comments and updated header in `SessionStateMachine` class.
- Removed `self.log` assignment in `Pipe` class and updated to use `Log.get()`.
- Corrected `_open` method in `Pipeline` class.
- Ensured proper handling of directories and consistent logging using `Log` class in `Files` class.
- Removed incorrect call to `self.config.get("file")` in `_open` method of `Pipeline` class.
- Removed explicit database creation in `dataset.load` and ensured `Dataset` class is used correctly with the new API.
- Added checks to ensure files exist before loading in `load.py` command.
- Ensured absolute paths are used for loading files in `Dataset` class.
- Added `database.name` to the configuration and ensured `database_url` is formatted with the dataset name before initializing the `Database` instance.
- Added logging for the database URL during initialization in `Database` class.
- Updated `config.py` to include `database_name` and ensured the configuration is correctly used throughout the codebase.

### Fixed

- Updated `Files.get_processed_path` method to create the processed directory if it does not exist.
- Added logging to confirm the creation of the processed directory in `Files` class.
- Updated `load.py` to use the enhanced `Files` class for handling the processed directory path.
- Fixed sorting issue in the `multi_thread_apply` method within the `Pipe` class.
- Added debugging statements to inspect the contents of the `futures` dictionary and `results` list in `Pipe` class.
- Ensured the `results` list is properly sorted based on the `futures` keys in `Pipe` class.
- Verified the functionality of the `multi_thread_apply` method to confirm the fix resolves the issue.
- Updated docstrings and comments for clarity.
- Initialized and displayed the progress bar immediately with 0% progress in `tqdm`.
- Updated progress bar at 0.1-second intervals using a background thread.
- Ensured smoother and more frequent updates during multi-threaded operations in `tqdm`.

## [Unreleased] - 2025-01-04

### Added

- Added `database.name` to the configuration to ensure proper database naming.
- Updated `config.py` to include `database_name`.
- Developed methods for all necessary tasks in the `DataTonic` class, including data pushing to the HF API.
- Implemented pseudocode for reading configuration properties, handling dataset selection, and uploading files in the `DataTonic` class.
- Extracted data from the database and converted it to a DataFrame.
- Applied include/exclude filters to the DataFrame.
- Converted the DataFrame to parquet files.
- Saved parquet files in the processed directory.
- Integrated the extended `DataTonic` class into the existing workflow.
- Updated pipeline configuration to align with the new setup.
- Planned for comprehensive unit tests to cover all new functionalities.
- Ensured proper handling and validation of configuration properties.
- Updated documentation to reflect all recent changes and new options.
- Documented all changes and improvements for easy tracking.
- Ensured all responses and information are verified and grounded.

### Changed

- Removed `self.log` assignment and switched to using `Log.info` directly in `SessionStateMachine` class.
- Removed `self.log` assignment in `Pipe` class and updated to use `Log.get()`.
- Corrected `_open` method in `Pipeline` class.
- Ensured proper handling of directories and consistent logging using `Log` class in `Files` class.
- Removed incorrect call to `self.config.get("file")` in `_open` method of `Pipeline` class.
- Removed explicit database creation in `dataset.load` and ensured `Dataset` class is used correctly with the new API.
- Added checks to ensure files exist before loading in `load.py` command.
- Ensured absolute paths are used for loading files in `Dataset` class.
- Added logging for the database URL during initialization in `Database` class to ensure it's using the correct format.

### Fixed

- Added `database.name` to the configuration and ensured `database_url` is formatted with the dataset name before initializing the `Database` instance.
- Removed comments and updated the header in `SessionStateMachine` class.

## [Unreleased] - 2025-01-03

### Added

- Moved database processing logic to a new `process` method in the `Database` class.
- Updated `Pipeline` class to call `Database.process` for database processing.
- Added `skip_files` flag to `Pipeline.open` method to control file processing.
- Refactored `Files` class to handle configuration attributes correctly.
- Improved error handling and logging for better debugging.
- Added `NormalizeTextPipe` class to handle text normalization tasks, including converting text to lowercase, expanding contractions, removing separators and special characters, normalizing numbers and space-separated characters, removing partial extract intros, section headers, and sign-offs, removing initial patterns and period patterns, removing headers before the first occurrence of `subject:`, and cleaning unnecessary whitespace.
- Enhanced `TextUtils` class with new methods including `expand_contractions`, `remove_special_characters`, `remove_separators`, `remove_whitespace`, `normalize_numbers`, `normalize_spaced_characters`, `remove_partial_extract_intro`, `remove_section_headers`, `remove_signoff`, `remove_initial_pattern`, `remove_period_patterns`, and `remove_header`.
- Updated pipeline configuration to include the following pipes: `AddIdPipe`, `DropColumnsPipe`, `RemapColumnsPipe`, `RemoveDuplicatesPipe`, `HandleMissingValuesPipe`, `CleanWhitespacePipe`, `NormalizeTextPipe`, and `FilterBySizePipe`. Ensured normalization before filtering by size and added contraction mappings for text normalization.
- Implemented logging for tracking the total running time of the pipeline.
- Conducted comprehensive testing to ensure proper text normalization and data cleaning.
- Verified that normalized text fits within LLaMA's 128k context window.
- Ensured all changes align with defined goals and maintain code readability and efficiency.
- Added `ExpandTermsPipe` class to handle the expansion of abbreviations and acronyms, configured columns to expand and terms to use for expansion, utilized `TextUtils.expand_terms` method for term expansion, and ensured the removal of unnecessary whitespace using `TextUtils.remove_whitespace`.
- Worked on the following files:
- `thinking_dataset/commands/clean.py`: Enhanced cleanup processes and error handling.
- `thinking_dataset/commands/download.py`: Improved file handling and logging.
- `thinking_dataset/commands/load.py`: Ensured correct database loading and configuration usage.
- `thinking_dataset/commands/prepare.py`: Improved data preparation steps.
- `thinking_dataset/io/files.py`: Enhanced file I/O operations and directory management.
- `thinking_dataset/utilities/command_utils.py`: Added new utility functions for command operations.
- `thinking_dataset/pipeworks/pipes/normalize_text_pipe.py`: Created for text normalization tasks.
- `thinking_dataset/config/dataset_config.yaml`: Included new configuration options.
- `thinking_dataset/utilities/text_utils.py`: Added additional text processing utilities.
- `thinking_dataset/pipelines/pipeline.py`: Integrated new pipeline processing logic.

### Fixed

- Updated the `clean` command to check if the data directory exists before attempting to remove it.
- Added a check to log a message and exit gracefully if the directory does not exist, avoiding FileNotFoundError.
- Improved logging and error handling to provide clear feedback on the cleanup process.
- Added handling for PermissionError to skip files in use by other processes, with appropriate logging.
- Addressed `AttributeError: 'dict' object has no attribute 'root_path'` issue in `Files` class.
- Addressed `AttributeError: 'Config' object has no attribute 'get'` issue by accessing attributes directly.

### Changed

- Created a specification for implementing multi-threaded processing in the Pipe class.
- Updated the "Prompt Template for Recent Work" to improve structure and readability.
- Replaced all mentions of `preprocess` command with `prepare` command.
- Adjusted the order of sections to ensure optimal memory usage.
- Updated "Files Worked On" to include relevant files for the `pipeworks` pipeline, dataset configuration, and command enhancements.
- Enhanced the "Notes for Next Session" section to provide clear and actionable tasks.
- Refined the "Overview" section to ensure clear documentation of recent changes and improvements.

## [Unreleased] - 2025-01-02

### Added

- Added `logger` and `dotenv` decorators to `clean`, `download`, `load`, and `prepare` commands.
- Implemented progress tracking with `tqdm` for data preprocessing pipes.
- Enhanced logging for better traceability and human-readable output.
- Supported `auto` column detection for `RemoveDuplicatesPipe` and `HandleMissingValuesPipe`.
- Added `remove_partials` and `allow_empty` configurations for `HandleMissingValuesPipe`.
- Improved error handling for missing columns in preprocessing pipes.
- Broke down `_process_file` into smaller private methods within the `Pipeline` class.
- Introduced `Pipe` and `Pipeline` classes with dynamic pipe loading.
- Supported dynamic loading of processing pipes based on user-defined types.
- Updated the prompt template for project guidelines with detailed sections.
- Added `NormalizeTextPipe` class to handle text normalization tasks:
- Convert text to lowercase.
- Expand contractions.
- Remove separators and special characters.
- Normalize numbers and space-separated characters.
- Remove partial extract intros, section headers, and sign-offs.
- Remove initial patterns and period patterns.
- Remove headers before the first occurrence of `subject:`.
- Clean unnecessary whitespace.
- Enhanced `TextUtils` class with new methods:
- `expand_contractions`.
- `remove_special_characters`.
- `remove_separators`.
- `remove_whitespace`.
- `normalize_numbers`.
- `normalize_spaced_characters`.
- `remove_partial_extract_intro`.
- `remove_section_headers`.
- `remove_signoff`.
- `remove_initial_pattern`.
- `remove_period_patterns`.
- `remove_header`.
- Updated pipeline configuration to include:
- `AddIdPipe`, `DropColumnsPipe`, `RemapColumnsPipe`, `RemoveDuplicatesPipe`, `HandleMissingValuesPipe`, `CleanWhitespacePipe`, `NormalizeTextPipe`, `FilterBySizePipe`.
- Ensured normalization before filtering by size.
- Added contraction mappings for text normalization.
- Implemented logging for tracking the total running time of the pipeline.
- Conducted comprehensive testing to ensure proper text normalization and data cleaning.
- Verified that normalized text fits within LLaMA's 128k context window.
- Ensured all changes align with defined goals and maintain code readability and efficiency.

### Fixed

- Ensured robust error handling and accurate logging with correct timestamp format.
- Resolved deprecation warnings and ensured maintainable code.

### Changed

- Renamed `run_flows` method to `open` in `Pipeline` class to align with the pipe metaphor.
- Refactored `Pipeline` class for improved modularity and encapsulation.
- Improved `dataset_config.yaml` structure for better clarity and flexibility.
- Updated CLI commands (`prepare`, `download`) to utilize new pipeline methods.
- Enhanced documentation for improved clarity and readability.
- Revised and optimized the "Prompt Template for Recent Work" to improve structure and readability.
- Replaced all mentions of `preprocess` command with `prepare` command.
- Adjusted the order of sections to ensure optimal memory usage.
- Updated "Files Worked On" to include relevant files for the `pipeworks` pipeline, dataset configuration, and command enhancements.
- Enhanced the "Notes for Next Session" section to provide clear and actionable tasks.
- Refined the "Overview" section to ensure clear documentation of recent changes and improvements.

### [Unreleased] - 2025-01-01

### Added

- Added `logger` and `dotenv` decorators to `clean`, `download`, `load`, and `prepare` commands.
- Implemented progress tracking with `tqdm` for data preprocessing pipes.
- Enhanced logging for better traceability and human-readable output.
- Supported `auto` column detection for `RemoveDuplicatesPipe` and `HandleMissingValuesPipe`.
- Added `remove_partials` and `allow_empty` configurations for `HandleMissingValuesPipe`.
- Improved error handling for missing columns in preprocessing pipes.
- Broke down `_process_file` into smaller private methods within the `Pipeline` class.
- Introduced `Pipe` and `Pipeline` classes with dynamic pipe loading.
- Supported dynamic loading of processing pipes based on user-defined types.
- Updated the prompt template for project guidelines with detailed sections.

### Fixed

- Ensured robust error handling and accurate logging with the correct timestamp format.
- Resolved deprecation warnings and ensured maintainable code.

### Changed

- Renamed `run_flows` method to `open` in the `Pipeline` class to align with the pipe metaphor.
- Refactored `Pipeline` class for improved modularity and encapsulation.
- Improved `dataset_config.yaml` structure for better clarity and flexibility.
- Updated CLI commands (`prepare`, `download`) to utilize new pipeline methods.
- Enhanced documentation for improved clarity and readability.

### [Unreleased] - 2024-12-31

### Added

- Added `logger` decorator to `clean`, `download`, `load`, and `prepare` commands.
- Modified `dotenv` decorator to correctly handle logger setup.
- Updated `files.py` to include `log` argument in `make_dir` and `remove_dir` methods.
- Enhanced logging to use module classpath with dot notation.
- Added detailed logging for steps in the load process.
- Added `thinking_dataset/utilities/log.py` for unified logging with timestamps.
- Implemented `Pipe` and `Pipeline` classes with dynamic pipe loading.
- Integrated new `Pipe` and `Pipeline` classes into `preprocess.py` CLI command.
- Added sections for `huggingface`, `database`, `paths`, and `files` in `dataset_config.yaml`.
- Added comprehensive unit tests for new features and operations.
- Added support for dynamic loading of processing pipes based on user-defined types.
- Included display names and descriptions for better identification of processing steps.

### Fixed

- Fixed database name formatting issue in `DatasetConfig`.
- Fixed issues with dynamic pipe class loading in `command_utils.py`.
- Improved error handling and type annotations across various modules.
- Ensured thorough logging at each step for better traceability and debugging.
- Enhanced error handling in `DatabaseSession` and `Database` classes.
- Improved `GetFileList` operation to handle dataset configuration properly.
- Gracefully exited on file list retrieval errors to maintain consistency.
- Updated error reporting to match previous functions and simplified logging without rich traces.
- Ensured environment variables were loaded and validated successfully.
- Ensured correct file paths and use of local file system for listing files.

### Changed

- Refactored exception handling to use `log` parameter.
- Refactored `BaseDataset` to use the processed directory for loading files.
- Ensured proper database creation and loading of prepared parquet files.
- Improved file path construction in `Files` class.
- Removed unnecessary filtering for local files in the load process.
- Ensured accurate logging messages with the correct timestamp format.
- Refactored `thinking_dataset/io/files.py` to accept dataset config object for encapsulated logic.
- Renamed `touch` method to `make_dir` for clarity.
- Added full path construction using `self.config.ROOT_DIR`.
- Updated methods for consistency and modularity.
- Utilized dataset configuration paths for constructing file paths in preprocess and download commands.
- Created raw data directory if it didn't exist in the preprocess command.
- Improved logging to debug file paths and directory contents in the preprocess command.
- Improved logging for better traceability in the download command.
- Renamed method `load_data` to `read_data` in `command_utils.py` for consistency.
- Added `get_raw_path` method to `files.py` to construct raw data paths with multiple components.
- Improved directory and file management methods in `files.py`.
- Ensured correct file handling and error management in the preprocess command.
- Reorganized dataset config structure for better clarity and flexibility.
- Consolidated ROOT_DIR, DATA_DIR, and DB_DIR into `paths` section in `dataset_config.yaml`.
- Grouped INCLUDE_FILES and EXCLUDE_FILES into `files` section in `dataset_config.yaml`.
- Added `huggingface` and `database` sections in `dataset_config.yaml` for better organization.
- Updated `DatasetConfig` class to parse the new configuration structure.
- Updated `BaseDataset` class to utilize paths from the new configuration structure.
- Updated `download.py` command to correctly construct paths and apply filters.
- Updated `load.py` command to correctly apply and utilize filters when loading datasets.
- Refactored `CommandUtils` to include environment variable handling and path construction.
- Combined `try-except` blocks in `download.py`, `load.py`, and `clean.py` for better error handling.
- Ensured `clean.py` uses paths from `dataset_config.yaml` instead of environment variables.
- Enhanced logging to track the flow of operations and error handling more effectively.
- Updated changelog with recent changes and refactor details.
- Enhanced the most recent work template to reflect new operations, features, and fixed issues.
- Consolidated documentation to improve clarity and readability.
- Improved logging and error handling across various components.
- Refined database and session handling for better performance.
- Ensured all changes adhere to coding standards and style guidelines.
- Updated the prompt template for better clarity and comprehensiveness.
- Rewrote all documentation with the latest knowledge, including INSTALLATION.md, DEPLOYMENT.md, TESTING.md, TROUBLESHOOTING.md, FAQ.md, and PIPELINE.md.
- Enhanced the changelog to reflect all recent updates and improvements.

## [Unreleased] - 2024-12-30

### Added

- Implemented a new `Log` class for unified logging across the project.
- Configured `RichHandler` for rich logging and pretty errors.
- Ensured consistent formatting in log messages with customizable time format including milliseconds.
- Improved error handling in `DataTonic` and `Dataset` classes, added detailed exception logging with rich traceback, ensured the logger is initialized before any operation in the `Dataset` class, and handled missing configuration errors gracefully with clear error messages and immediate exits.
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
- Implemented the `DatabaseConfig` class for storing database configuration and added a validate method to ensure all configuration settings are valid.
- Created unit tests for instantiation, validation, default values, invalid data types, and edge cases. Tested initialization of `DatabaseConfig` with valid and invalid configurations, verified default values are set correctly when config options are omitted, ensured invalid data types for configuration settings raise appropriate errors, and tested edge cases for numerical values such as 0 for pool_size, max_overflow, connect_timeout, and read_timeout.
- Updated test fixtures and mocks for `ConfigLoader` to simulate different configuration scenarios and improved test coverage for the `DatabaseConfig` class to ensure robustness and reliability.
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
- Created `GetPermissions` operation class.
- Created tests for `GetPermissions` operation.
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
