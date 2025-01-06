# Installation

## Overview

This document provides step-by-step instructions for setting up the development environment for the Thinking Dataset Project. Follow these steps to get the project up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10 or higher**: Download it from the [official Python website](https://www.python.org/downloads/).
- **Git**: Download it from the [official Git website](https://git-scm.com/downloads).
- **A cloud-based account (e.g., OpenAI) or a GPU (RTX 3090 or greater) for processing, or both**

## Setup Steps

### 1. Clone the Repository

First, clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/MultiTonic/thinking-dataset.git
cd thinking-dataset
```

### 2. Install `uv` Package Management Tool

Install the `uv` package management tool using `pip`:

```bash
pip install uv
```

### 3. Install Dependencies

Install the required packages using `uv` and `thinking-dataset.toml`:

```bash
uv install -f thinking-dataset.toml
```

### 4. Set Up Environment Variables

Copy the `.env.sample` file to `.env` and change the values as needed:

```bash
cp .env.sample .env
```

Edit the `.env` file to include your specific configuration settings. Here is an example of what you might include:

```plaintext
HF_TOKEN=your_huggingface_token
HF_DATASET=your_dataset_name
HF_ORGANIZATION=your_organization_name
ROOT_DIR=your_root_directory
DATA_DIR=your_data_directory
```

### 5. Initialize the CLI Tool

Initialize the CLI tool to set it up for use. The `init` command will prompt you to enter various configurations such as the dataset name and organization, similar to how `npm init` works:

```bash
thinking-dataset init
```

### 6. Download the Dataset

Download the required dataset using the CLI command:

```bash
thinking-dataset download
```

### 7. Load the Dataset

Load the dataset into the SQLite database:

```bash
thinking-dataset load
```

### 8. Clean the Data Directory (Optional)

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
