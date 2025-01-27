# Usage Guide

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
  - [Virtual Environment](#virtual-environment)
  - [Environment Configuration](#environment-configuration)
- [Basic Usage](#basic-usage)
  - [Command Line Interface](#command-line-interface)
  - [Common Workflows](#common-workflows)
- [Advanced Usage](#advanced-usage)
  - [Using Different Model Providers](#using-different-model-providers)
  - [CUDA Support](#cuda-support)
  - [Development Tools](#development-tools)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [Additional Resources](#additional-resources)

## Development Environment Setup

> **Note:** This package requires Python 3.12 or later.

### Virtual Environment

The virtual environment is created automatically during installation:

```bash
# Install package (creates and configures virtual environment automatically)
pip install --editable .

# Activate virtual environment
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS
```

### Environment Configuration

1. Copy the sample environment file:
   ```bash
   cp .env.sample .env
   ```

2. Configure your environment variables:
   ```ini
   # Required settings
   HF_ORG="my_huggingface_organization"
   HF_USER="my_huggingface_username"
   HF_READ_TOKEN="my_huggingface_read_access_token"
   HF_WRITE_TOKEN="my_huggingface_write_access_token"

   # Required configuration
   CONFIG_PATH="config/config.yaml"

   # One or more providers required
   OLLAMA_SERVER_URL="http://localhost:11434"
   OPENAI_API_TOKEN="your_openai_api_token"
   RUNPOD_API_TOKEN="your_runpod_api_token"
   ```

## Basic Usage

### Command Line Interface

The package provides a CLI tool `thinking-dataset` with the following commands:

```bash
# View version and help
thinking-dataset --version
thinking-dataset --help

# Data operations
thinking-dataset download   # Download dataset
thinking-dataset process    # Process downloaded data
thinking-dataset load       # Load data into database
thinking-dataset enrich     # Enrich data using AI
thinking-dataset export     # Export processed data
thinking-dataset upload     # Upload to HuggingFace
thinking-dataset clean      # Clean data directory
```

### Common Workflows

#### 1. Initial Setup and Data Download
```bash
# Download and prepare dataset
thinking-dataset download
thinking-dataset process
thinking-dataset load
```

#### 2. Data Enrichment and Export
```bash
# Enrich and export data
thinking-dataset enrich
thinking-dataset export
```

#### 3. Upload to HuggingFace
```bash
# Upload processed dataset
thinking-dataset upload
```

## Advanced Usage

### Using Different Model Providers

The package supports multiple model providers:

1. **Ollama** (Default, local):
   ```bash
   # Ensure Ollama is running
   ollama serve
   ```

2. **OpenAI**:
   ```bash
   # Set OpenAI API token in .env
   OPENAI_API_TOKEN="your_token"
   ```

3. **RunPod**:
   ```bash
   # Set RunPod API token in .env
   RUNPOD_API_TOKEN="your_token"
   ```

### CUDA Support

For GPU acceleration, install with CUDA support:
```bash
# Within your activated virtual environment
pip install --editable ".[cuda]"
```

This will replace the CPU version of PyTorch with the CUDA-enabled version.

> **Note:** Make sure you have NVIDIA CUDA drivers installed on your system.

### Development Tools

Install development dependencies:
```bash
uv pip install ".[dev,test,docs]"
```

## Troubleshooting

For common issues and solutions, see [Troubleshooting](06_TROUBLESHOOTING.md).

## Uninstallation

To completely remove the thinking-dataset package from your system:

1. **Deactivate the virtual environment:**
   ```bash
   deactivate
   ```

2. **Remove the package:**
   ```bash
   uv pip uninstall thinking-dataset
   ```

3. **Clean up (optional):**
   ```bash
   # Remove virtual environment
   rm -rf .venv

   # Remove data directory
   thinking-dataset clean

   # Remove downloaded datasets
   rm -rf data/

   # Remove environment file
   rm .env
   ```

## Additional Resources

- [Project Documentation](https://github.com/MultiTonic/thinking-dataset/tree/main/docs)
- [API Reference](docs/04_API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
