# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2024-12-29

### Added
- Created `VolumeManager` class to manage multiple SQLite database volumes.
- Implemented tests for `VolumeManager` class, ensuring correct volume creation and management.
- Added debug statements in `VolumeManager` for troubleshooting volume creation.

### Changed
- Refactored `VolumeManager` class to ensure proper initialization and volume switching logic.

## [Unreleased] - 2024-12-28

### Added
- Created `GetPermissions` operation class.
- Created tests for `GetPermissions` operation.

## [Unreleased] - 2024-12-27

### Added
- Created `GetDownloadUrls` operation class.
- Created tests for `GetDownloadUrls` operation.
- Added `GetFileList` operation class.
- Created tests for `GetFileList` operation.

### Changed
- Refactored `DatasetDownloads` class to remove deprecated methods.
- Updated `OperationTypes` enum to include new operations.
- Updated unit tests for `OperationTypes`.

### Fixed
- Updated test for `GetFileList` to reflect actual module names in log messages.
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
