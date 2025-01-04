# Usage Guide

## Overview

This document offers detailed usage instructions for the "Dark Thoughts" thinking-dataset project. It covers how to interact with the application, provides examples of typical workflows, and outlines common commands. This guide ensures users can efficiently navigate the application and leverage its powerful features for generating and analyzing complex hypothetical scenarios.

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
- [Conclusion](#conclusion)

## Running the Application

To start the application, ensure your virtual environment is activated and run the following command:

```bash
thinking-dataset
```

## Using the CLI

The Command Line Interface (CLI) of the "Dark Thoughts" thinking-dataset project allows you to efficiently perform various tasks and operations.

### Basic Commands

- **Initialize the Database**: Initialize the SQLite database and create necessary tables.
  ```bash
  python scripts/init_db.py
  ```

- **Run the Application**: Start the main application.
  ```bash
  thinking-dataset
  ```

- **Download Data**: Download raw data from specified sources.
  ```bash
  thinking-dataset download --source <source_name>
  ```

- **Clean Data**: Perform data cleaning and normalization.
  ```bash
  thinking-dataset clean --file path/to/datafile.csv
  ```

### Example Workflows

#### Example 1: Data Ingestion and Preprocessing

1. **Download Raw Data**: Download raw data from a specified source.
   ```bash
   thinking-dataset download --source wikileaks
   ```

2. **Add Raw Data**: Import raw data from a file.
   ```bash
   thinking-dataset add-data --file path/to/datafile.csv
   ```

3. **Clean and Normalize Data**: Perform data cleaning and normalization.
   ```bash
   thinking-dataset clean --file path/to/datafile.csv
   ```

#### Example 2: Case Study Generation

1. **Generate Seeds**: Create seed objects using predefined keywords.
   ```bash
   thinking-dataset generate-seeds --keywords "strategy, ethics"
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

To register an adapter for a specific inference endpoint (e.g., LLama.cpp, Ollama):

1. **Initialize the `InferenceManager`**.
2. **Register the desired adapter** (e.g., `LLamaCppAdapter`) with the `InferenceManager`.

### Making Predictions

To make predictions using registered adapters:

1. **Provide input data**.
2. **Use the `InferenceManager`** to predict results from all registered adapters.
3. **Display the results**.

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
   thinking-dataset generate-seeds --keywords "strategy, ethics"
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

**Algorithm**:
1. **Add logging configuration** with the desired format and level.
2. **Log important events** during the application's execution for better traceability.

## Conclusion

The "Dark Thoughts" thinking-dataset project offers robust tools for generating and analyzing complex scenarios. By following this guide, users can efficiently use CLI commands, manage data, interact with inference adapters, and configure settings. This ensures the project is versatile, user-friendly, and supports diverse research in AI and cognitive science.