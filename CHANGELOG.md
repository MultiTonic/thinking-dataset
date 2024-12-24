# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2024-12-24

### Added
- Cloned the `thinking-dataset` repository and switched to the `dev-prototyping-alpha` branch.
- Updated the README to use `venv` instead of `.venv` for virtual environment setup.
- Installed basic project dependencies: `huggingface_hub[cli]`, `datasets`, `PyPDF2`, `python-dotenv`, `requests`, `rich`, `sqlite-utils`, `pytest`, `loguru`, `pandas`, `numpy`, `scikit-learn`, `sqlalchemy`, `tqdm`.
- Integrated `rich` for enhanced console output and error handling.
- Set up SQLite as the central source of truth for data storage.

### Changed
- Simplified `setup.py` to include only the necessary dependencies.
- Enhanced README for better clarity on the setup process.

### Fixed
- N/A

## [1.0.0] - 2024-10-29

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

## [0.0.1] - 2024-10-28

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
