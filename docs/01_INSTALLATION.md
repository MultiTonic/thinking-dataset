# Installation

## Overview

This document provides step-by-step instructions for setting up the development environment for the "Dark Thoughts" thinking-dataset project. Follow these steps to get the project up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.7 or higher**: Download it from the [official Python website](https://www.python.org/downloads/).
- **Git**: Download it from the [official Git website](https://git-scm.com/downloads).

## Setup Steps

### 1. Clone the Repository

First, clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/MultiTonic/thinking-dataset.git
cd thinking-dataset
```

### 2. Create a Virtual Environment

Create a virtual environment to manage the project's dependencies:

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment:

- On **Windows**:
  ```bash
  .\.venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 4. Install Dependencies

With the virtual environment activated, install the project and its dependencies in editable mode:

```bash
pip install -e .
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root directory and add the necessary environment variables. You can copy the provided `.env.example` file and edit it as needed:

```bash
cp .env.example .env
```

Edit the `.env` file to include your specific configuration settings. Here is an example of what you might include:

```plaintext
HF_TOKEN=your_huggingface_token
HF_DATASET=your_dataset_name
HF_ORGANIZATION=your_organization_name
ROOT_DIR=your_root_directory
DATA_DIR=your_data_directory
```

### 6. Initialize the SQLite Database

Run the following script to initialize the SQLite database and create the necessary tables:

```bash
python scripts/init_db.py
```

### 7. Running the Application

To run the application, use the following command:

```bash
thinking-dataset
```

### 8. Deactivate the Virtual Environment (Optional)

Once you're done working with the project, you can deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

If you encounter any issues during the installation process, refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for common issues and their solutions.

## Contributing

We welcome contributions from the community! For more information on how to contribute, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for more details.
