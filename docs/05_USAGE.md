# Usage

## Usage Guide

This document provides detailed usage instructions for the "Dark Thoughts" thinking-dataset project, including how to interact with the application, examples of typical workflows, and common commands.

## Table of Contents
- [Running the Application](#running-the-application)
- [Using the CLI](#using-the-cli)
  - [Basic Commands](#basic-commands)
  - [Example Workflows](#example-workflows)
- [Interacting with Inference Adapters](#interacting-with-inference-adapters)
  - [Registering Adapters](#registering-adapters)
  - [Making Predictions](#making-predictions)
- [Data Management](#data-management)
  - [Adding Raw Data](#adding-raw-data)
  - [Generating Case Studies](#generating-case-studies)
- [Advanced Usage](#advanced-usage)
  - [Custom Configurations](#custom-configurations)
  - [Logging and Monitoring](#logging-and-monitoring)

## Running the Application

To start the application, ensure your virtual environment is activated and run the following command:

```bash
thinking-dataset
```

## Using the CLI

The Command Line Interface (CLI) of the "Dark Thoughts" thinking-dataset project allows you to perform various tasks and operations efficiently.

### Basic Commands

- **Initialize the Database**: Initialize the SQLite database and create necessary tables.
  ```bash
  python scripts/init_db.py
  ```

- **Run the Application**: Start the main application.
  ```bash
  thinking-dataset
  ```

### Example Workflows

#### Example 1: Data Ingestion and Preprocessing

1. **Add Raw Data**: Import raw data from a file.
   ```bash
   thinking-dataset add-data --file path/to/datafile.csv
   ```

2. **Clean and Normalize Data**: Perform data cleaning and normalization.
   ```bash
   thinking-dataset preprocess-data
   ```

#### Example 2: Case Study Generation

1. **Generate Seeds**: Create seed objects using predefined keywords.
   ```bash
   thinking-dataset generate-seeds --keywords "ethics, bias"
   ```

2. **Create Cables**: Combine seed objects to generate cables.
   ```bash
   thinking-dataset create-cables
   ```

3. **Generate Case Studies**: Use cables to create detailed case studies.
   ```bash
   thinking-dataset generate-case-studies
   ```

## Interacting with Inference Adapters

The project supports various inference adapters to interface with different serverless endpoints, providing flexibility and scalability.

### Registering Adapters

Register an adapter to use a specific inference endpoint (e.g., Hugging Face, Ollama).

```python
from thinking_dataset.adapters import HuggingFaceAdapter, InferenceManager

manager = InferenceManager()
manager.register_adapter(HuggingFaceAdapter())
```

### Making Predictions

Use registered adapters to make predictions based on input data.

```python
input_data = "Once upon a time..."
results = manager.predict_all(input_data)
print(results)
```

## Data Management

### Adding Raw Data

To add raw data to the SQLite database:

```bash
thinking-dataset add-data --file path/to/datafile.csv
```

### Generating Case Studies

To generate case studies from the data:

1. **Generate Seeds**:
   ```bash
   thinking-dataset generate-seeds --keywords "ethics, bias"
   ```

2. **Create Cables**:
   ```bash
   thinking-dataset create-cables
   ```

3. **Generate Case Studies**:
   ```bash
   thinking-dataset generate-case-studies
   ```

## Advanced Usage

### Custom Configurations

Custom configurations can be set using environment variables in the `.env` file. Update the file with your specific settings.

### Logging and Monitoring

Enhanced logging can be implemented using `loguru` for better monitoring and debugging.

Example usage:

```python
from loguru import logger

logger.add("file.log", format="{time} {level} {message}", level="INFO")

logger.info("Starting the application")
# Your main application code
logger.info("Application finished successfully")
```
