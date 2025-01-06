# Usage Guide

## Overview

This document offers detailed usage instructions for the Thinking Dataset Project. It covers how to interact with the application, provides examples of typical workflows, and outlines common commands. This guide ensures users can efficiently navigate the application and leverage its powerful features for generating strategic business insights and STaR case studies.

## Table of Contents

- [Running the Application](#running-the-application)
- [Using the CLI](#using-the-cli)
  - [Basic Commands](#basic-commands)
  - [Example Workflows](#example-workflows)
- [Advanced Usage](#advanced-usage)
  - [Custom Configurations](#custom-configurations)
  - [Logging and Monitoring](#logging-and-monitoring)
- [Conclusion](#conclusion)

## Running the Application

To start the application, ensure your environment variables are set up correctly and run the following command:

```bash
thinking-dataset --version
```

## Using the CLI

The Command Line Interface (CLI) of the Thinking Dataset Project allows you to efficiently perform various tasks and operations.

### Basic Commands

- **Download Data**: Download all parquet files from the Cablegate dataset using Hugging Face CLI.
  ```bash
  thinking-dataset download
  ```

- **Process Data**: Process the downloaded data to load into the database.
  ```bash
  thinking-dataset process
  ```

- **Load Data**: Load the prepared data downloaded from Hugging Face CLI.
  ```bash
  thinking-dataset load
  ```

- **Enrich Data**: Enrich the prepared data using AI.
  ```bash
  thinking-dataset enrich
  ```

- **Export Data**: Export the enriched data from the database.
  ```bash
  thinking-dataset export
  ```

- **Upload Data**: Upload the exported data to the specified location.
  ```bash
  thinking-dataset upload
  ```

- **Clean Data Directory**: Clear the root data directory and start fresh.
  ```bash
  thinking-dataset clean
  ```

### Example Workflows

#### Example 1: Data Ingestion and Preprocessing

1. **Download Data**: Download all parquet files from the Cablegate dataset.
   ```bash
   thinking-dataset download
   ```

2. **Process Data**: Process the downloaded data to load into the database.
   ```bash
   thinking-dataset process
   ```

3. **Load Data**: Load the prepared data downloaded from Hugging Face CLI.
   ```bash
   thinking-dataset load
   ```

4. **Enrich Data**: Enrich the prepared data using AI.
   ```bash
   thinking-dataset enrich
   ```

5. **Export Data**: Export the enriched data from the database.
   ```bash
   thinking-dataset export
   ```

6. **Upload Data**: Upload the exported data to the specified location.
   ```bash
   thinking-dataset upload
   ```

7. **Clean Data Directory**: Clear the root data directory and start fresh.
   ```bash
   thinking-dataset clean
   ```

## Advanced Usage

### Custom Configurations

Custom configurations can be set using environment variables in the `.env` file. Update the file with your specific settings. You can also change custom project-dependent configuration settings in the file `./config/config.yaml`.

### Logging and Monitoring

Enhanced logging can be implemented using `loguru` for better monitoring and debugging.

**Algorithm**:
1. **Add logging configuration** with the desired format and level.
2. **Log important events** during the application's execution for better traceability.

## Conclusion

The Thinking Dataset Project offers robust tools for generating strategic business insights and STaR case studies. By following this guide, users can efficiently use CLI commands, manage data, interact with inference adapters, and configure settings. This ensures the project is versatile, user-friendly, and supports diverse business and research needs.
