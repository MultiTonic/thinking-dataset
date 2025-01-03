# Thinking Dataset Project

**Creating a comprehensive thinking dataset**

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

The Thinking Dataset Project is designed to build a comprehensive dataset focused on facilitating various data-driven tasks and analyses. Manage, process, and analyze a wide range of data efficiently.

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

- Python 3.6 or later
- Git

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/MultiTonic/thinking-dataset.git
    cd thinking-dataset
    ```

2. **Create and activate a virtual environment:**

    On macOS/Linux:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    On Windows:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -e .
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following variables:
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

### Cleaning the Data Directory

To clear and recreate the root data directory:
```bash
thinking-dataset clean
```

### Running Tests

To run all tests and generate a coverage report:
```bash
python scripts/run_tests_and_generate_report.py
```

## Database Operations

### Executing Queries

To execute a query on the database:
```python
database.query("YOUR_SQL_QUERY")
```

### Fetching Data

To fetch data from the database:
```python
result = database.fetch_data("YOUR_SQL_QUERY")
```

## Contributing

Contributions are welcome! Add an issue on Github, then fork the repository and create a pull request with your changes. Ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Kara Rawson** - Lead Developer
- **Joseph Pollack** - Creator
- **MultiTonic Team** - Support and Collaboration
- **Hugging Face** - Providing robust tools and infrastructure for dataset management
```
