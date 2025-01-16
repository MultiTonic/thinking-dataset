# 

> # **Thinking Dataset:** Leveraging Real-World Data for Strategic Business Insights and STaR Case Study Generation

## Table of Contents

- [**Overview**](#overview)
- [**Features**](#features)
- [**Installation**](#installation)
- [**Usage**](#usage)
- [**Project Structure**](#project-structure)
- [**Contributing**](#contributing)
- [**License**](#license)
- [**Acknowledgements**](#acknowledgements)
- [**Citations**](#citations)

## Overview

The Thinking Dataset Project creates a dataset to help with various data tasks and analyses. The project uses advanced technologies and tools to manage, process, and analyze data efficiently. Our Thinking Dataset technology utilizes two key components: **STAR self-teaching** and **STaR Case Studies**.

**STAR self-teaching** is a method where the dataset acts as a model and uses other models (**Mixture of Models, MOM**) to generate new datasets. This process helps the model improve its evaluation scores and create synthetic datasets that are more accurate and effective than those created by humans. 

**STaR Case Studies** (Situation, Task, Action, and Result) are structured narratives used to illustrate how specific business challenges were addressed and the outcomes achieved. These case studies apply to our various datasets like **Cablegate**, which provide real-world seed data for generating comprehensive business insights.

For more details, see the [**OVERVIEW**](docs/00_OVERVIEW.md).

## Features

- **Structured Data Management**: Centralized data storage using SQLite.
- **Enhanced Logging**: Integrated `rich` for robust console outputs and error handling.
- **Automated Download/Upload**: Fetch, download, upload, and create datasets using Hugging Face CLI.
- **Modular Codebase**: Organized scripts and modules for better readability and maintenance.
- **Environment Configuration**: Flexible management of directories and environment variables.
- **Database Operations**: Modularized SQL database operations with a finite state machine for session management.
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

2. **Install the `uv` package management tool using `pip`:**

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

For detailed usage instructions, please refer to the [**USAGE**](docs/05_USAGE.md) in the `docs` directory.

## Project Directory Structure

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
│   ├── io/                 # File I/O operations
│   ├── pipeworks/          # Pipelines and pipes for data processing
│   │   ├── pipelines/      # Pipeline management and control
│   │   ├── pipes/          # Pipes used for data frame processing
│   ├── tonics/             # Data utility functions and helpers
│   ├── utilities/          # General-purpose utility helpers
│   ├── main.py             # Main execution file
└── setup.py                # Project setup
└── .env                    # Private environment variables file
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code adheres to the project's coding standards and includes appropriate tests. See [**CONTRIBUTING**](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License. See the [**LICENSE**](LICENSE) file for details.

## Acknowledgements

- **Kara Rawson** - Lead Engineer
- **Joseph Pollack** - Creator & Business Leader
- **MultiTonic Team** - Support and Collaboration
- **Hugging Face** - Providing robust tools and infrastructure for dataset management

## Citations

Please use the following citation format for referencing this project:

```plaintext
@misc{thinking-dataset,
  author = {Kara Rawson, Joseph Pollack, and et al.},
  title = {Thinking-Dataset: Leveraging Real-World Data for Strategic Business Insights and STaR Case Study Generation},
  year = {2025},
  howpublished = {\url{https://github.com/MultiTonic/thinking-dataset}},
  note = {Accessed: 2025-01-05}
}
```
