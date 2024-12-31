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
HF_HOME="~/.cache/huggingface"
HF_TOKEN="my_huggingface_access_token"
HF_PROJECT="thinking-dataset"
HF_DATASET="cablegate-pdf-dataset"
HF_ORGANIZATION="DataTonic"
HF_USER="my_huggingface_username"
```

### 6. Initialize the CLI Tool

Initialize the CLI tool to set it up for use:

```bash
thinking-dataset init
```

### 7. Download the Dataset

Download the required dataset using the CLI command:

```bash
thinking-dataset download
```

### 8. Load the Dataset

Load the dataset into the SQLite database:

```bash
thinking-dataset load
```

### 9. Clean the Data Directory (Optional)

If needed, clean the data directory and remove any leftovers:

```bash
thinking-dataset clean
```

## Troubleshooting

If you encounter any issues during the installation process, refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for common issues and their solutions.

## Contributing

We welcome contributions from the community! For more information on how to contribute, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for more details.
