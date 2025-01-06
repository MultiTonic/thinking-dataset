# Thinking Dataset Project

**Leveraging Real-World Data for Strategic Business Insights for STaR Case Study Generation**

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Directory Structure](#project-directory-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Citations](#citations)

## Overview

The Thinking Dataset Project is designed to build a comprehensive dataset focused on facilitating various data-driven tasks and analyses. This project aims to utilize cutting-edge technologies and frameworks to manage, process, and analyze a wide range of data efficiently.

## Features

- **Structured Data Management**: Centralized data storage using SQLite.
- **Enhanced Logging**: Integrated `rich` for robust console outputs and error handling.
- **Automated Downloads**: Fetch and download datasets using Hugging Face CLI.
- **Modular Codebase**: Organized scripts and modules for better readability and maintenance.
- **Environment Configuration**: Flexible management of directories and environment variables.
- **Database Operations**: Modularized database operations with finite state machine for session management.
- **Parquet File Processing**: Tooling for working with parquet files and ingesting them into database tables.

## Installation

### Prerequisites

- Python 3.10 or later
- Git
- A cloud-based account (e.g., OpenAI) or a GPU (RTX 3090 or greater) for processing, or both

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/MultiTonic/thinking-dataset.git
    cd thinking-dataset
    ```

2. **Install `uv` package management tool using `pip`:**

    ```bash
    pip install uv
    ```

3. **Install the required packages using `uv` and `thinking-dataset.toml`:**

    ```bash
    uv install -f thinking-dataset.toml
    ```

4. **Set up environment variables:**

    Copy the `.env.sample` file to `.env` and change the values as needed:
    ```bash
    cp .env.sample .env
    ```

    Update the `.env` file with the following variables:
    ```plaintext
    HF_TOKEN=your_huggingface_token
    HF_DATASET=your_dataset_name
    HF_ORGANIZATION=your_organization_name
    ROOT_DIR=your_root_directory
    DATA_DIR=your_data_directory
    ```

## Usage

### Running the Download Command

To download all parquet files from the Cablegate dataset using Hugging Face CLI:
```bash
thinking-dataset download
```

### Running All CLI Commands

To execute all CLI commands for the project:
```bash
python assets/scripts/run_cli_commands.py
```

For detailed usage instructions, please refer to the [05_USAGE.md](docs/05_USAGE.md) in the `docs` directory.

## Project Directory Structure

The following directory structure provides an overview of how the project is organized:

```
thinking-dataset/
├── config/                 # Configuration files
├── assets/                 # Assets directory for external resources
│   ├── prompts/            # Prompt templates
│   ├── scripts/            # Utility scripts
├── data/                   # Data directory
├── docs/                   # Project documentation
├── reports/                # Generated reports
├── tests/                  # Test files
├── thinking_dataset/       # Core project code
│   ├── commands/           # CLI command implementations
│   ├── connectors/         # Data connectors
│   ├── config/             # Configuration loaders and management
│   ├── datasets/           # Dataset definitions and processing
│   │   ├── operations/     # Data operations and transformations
│   ├── db/                 # Database support
│   │   ├── operations/     # Database operations and transactions
│   ├── io/                 # File I/O operations
│   ├── pipeworks/          # Pipelines and pipes for data processing
│   │   ├── pipelines/      # Pipeline management and control
│   │   ├── pipes/          # Pipes used for data frame processing
│   ├── tonics/             # Data utility functions and helpers
│   ├── utilities/          # General-purpose utility helpers
│   ├── main.py             # Main execution file
└── setup.py                # Project setup
└── .env                    # Private Environment variables file
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code adheres to the project's coding standards and includes appropriate tests. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Kara Rawson** - Lead Developer
- **Joseph Pollack** - Creator
- **MultiTonic Team** - Support and Collaboration
- **Hugging Face** - Providing robust tools and infrastructure for dataset management

## Citations

Please use the following citation format for referencing this project:

```plaintext
@misc{thinking-dataset,
  author = {Kara Rawson and Joseph Pollack and the MultiTonic Team},
  title = {Thinking Dataset Project: Leveraging Real-World Data for Strategic Business Insights and STaR Case Study Generation},
  year = {2025},
  howpublished = {\url{https://github.com/MultiTonic/thinking-dataset}},
  note = {Accessed: 2025-01-05}
}
```
