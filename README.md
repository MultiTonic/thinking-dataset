# Thinking Dataset: Leveraging Real-World Data for Strategic Business Insights and STaR Case Study Generation

[![Build Status](https://img.shields.io/github/workflow/status/MultiTonic/thinking-dataset/CI)](https://github.com/MultiTonic/thinking-dataset/actions)
[![License](https://img.shields.io/github/license/MultiTonic/thinking-dataset)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

## Table of Contents

- [**Overview**](#overview)
- [**Features**](#features)
- [**Installation**](#installation)
- [**Usage**](#usage)
- [**Quick Start**](#quick-start)
- [**Project Structure**](#project-structure)
- [**Contributing**](#contributing)
- [**Resources**](#resources)
- [**License**](#license)
- [**Citations**](#citations)
- [**Acknowledgements**](#acknowledgements)
- [**Contact**](#contact)

## Overview

The Thinking Dataset Project creates a dataset to help with various data tasks and analyses. The project uses advanced technologies and tools to manage, process, and analyze data efficiently. Our Thinking Dataset technology utilizes two key components: **STAR self-teaching** and **STaR Case Studies**.

**STAR self-teaching** is a method where the dataset acts as a model and uses other models (**Mixture of Models, MOM**) to generate new datasets. This process helps the model improve its evaluation scores and create synthetic datasets that are more accurate and effective than those created by humans.

**STaR Case Studies** (Situation, Task, Action, and Result) are structured narratives used to illustrate how specific business challenges were addressed and the outcomes achieved. These case studies apply to our various datasets like **Cablegate**, which provide real-world seed data for generating comprehensive business insights.

For more details, see the [**Overview**](docs/00_OVERVIEW.md).

## Features

- **Structured Data Management**: Centralized data storage using SQLite.
- **Enhanced Logging**: Integrated `rich` for robust console outputs and error handling.
- **Automated Download/Upload**: Fetch, download, upload, and create datasets using Hugging Face CLI.
- **Modular Codebase**: Organized scripts and modules for better readability and maintenance.
- **Environment Configuration**: Flexible management of directories and environment variables.
- **Database Operations**: Modularized SQL database operations with a finite state machine for session management.
- **Parquet File Processing**: Tooling for working with parquet files and ingesting them into database tables.

## Quick Start

### Prerequisites

- [**Python 3.12**](https://www.python.org/downloads/release/python-3128/) or later
- [**Git**](https://git-scm.com/)
- A **cloud-based account** (e.g., ***Huggingface***) or a **GPU** (***RTX 3090*** or greater) for processing, or both

### Setup

1. **Clone the [repository](https://github.com/MultiTonic/thinking-dataset.git):**

    ```bash
    git clone https://github.com/MultiTonic/thinking-dataset.git
    cd thinking-dataset
    ```

2. **Install [`uv`](https://docs.astral.sh/uv/) package manager:**
    ```bash
    pip install uv
    ```

3. **Set up the project:**
    ```bash
    uv run dev
    ```

This will create a virtual environment, install the project dependencies, and activate the virtual environment.

3. **Set up environment variables:**

    Copy the `.env.sample` file to `.env` and change the values as needed:
    ```bash
    cp .env.sample .env
    ```

    Update the `.env` file with your credentials:
    ```ini
    # Required settings
    HF_ORG="my_huggingface_organization"
    HF_USER="my_huggingface_username"
    HF_READ_TOKEN="my_huggingface_read_access_token"
    HF_WRITE_TOKEN="my_huggingface_write_access_token"

    # Required configuration
    CONFIG_PATH="config/config.yaml"

    # One or more providers
    OLLAMA_SERVER_URL="http://localhost:11434"
    OPENAI_API_TOKEN="your_openai_api_token"
    RUNPOD_API_TOKEN="your_runpod_api_token"
    ```

## Usage

### Virtual Environment

Activate the virtual environment using `uv`:
```bash
uv run dev
```

> **`uv`** will automatically setup and manage your virtual environment. For complete usage instructions and examples, see the [**Usage Guide**](docs/05_USAGE.md).

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

## Project Structure

The following directory structure provides an overview of how the project is organized:

```
thinking-dataset/
├── config/                 # Configuration files
├── assets/                 # Assets directory for external resources
│   ├── prompts/            # Prompt templates
│   ├── scripts/            # Utility scripts
│   ├── resources/          # External project data
│   ├── templates/          # JSON prompt templates
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
│   ├── dto/                # Data Transfer Objects (DTO)
│   ├── io/                 # File I/O operations
│   ├── pipeworks/          # Pipelines and pipes for data processing
│   │   ├── pipelines/      # Pipeline management and control
│   │   ├── pipes/          # Pipes used for data frame processing
│   ├── providers/          # AI data providers
│   ├── tonics/             # Data utility functions and helpers
│   ├── utils/              # General-purpose utility helpers
│   ├── main.py             # Main execution file
└── setup.py                # Project setup
└── .env                    # Private environment variables file
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code adheres to the project's coding standards and includes appropriate tests. See [Contributing](CONTRIBUTING.md) for detailed guidelines.

## Resources

- **[GitHub Repository](https://github.com/MultiTonic/thinking-dataset)**
- **[Python](https://www.python.org/downloads/)**
- **[Ollama](https://ollama.com/)**
- **[Discord: 🌟Tonic's Better Prompts](https://discord.gg/RgxcdVFjpz)**

## License

This dataset is licensed under the MIT License.

## Citations

Please use the following BibTeX entry to cite this dataset:

```bibtex
@software{thinking-dataset,
  author = {Kara Rawson, Joseph Pollack, and et al.},
  title = {Thinking-Dataset: Leveraging Real-World Data for Strategic Business Insights and STaR Case Study Generation},
  year = {2025},
  howpublished = {\url{https://github.com/MultiTonic/thinking-dataset}},
  note = {Accessed: 2025-01-25}
}
```

## Acknowledgements

Special thanks to our contributors:

- **Kara Rawson** - Lead Engineer
- **Joseph Pollack** - Creator & Business Leader
- **MultiTonic Team** - Support and Collaboration
- **Hugging Face** - Robust tools and infrastructure for dataset management

## Contact

For questions or support, please contact us at:

- **Email**: info@datatonic.ai
- **Discord**: [Join our Discord](https://discord.gg/RgxcdVFjpz)