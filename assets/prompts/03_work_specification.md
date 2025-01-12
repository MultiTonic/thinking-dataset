# Promot Template for Work Specification

## Overview

This template outlines the implementation of new features, including the development of critical pipeline components, data enrichment, and case study creation. The objective is to generate synthetic scenarios and case studies, manage file operations, and ensure dynamic configuration for efficient processing and integration.

## Details

### 1. Command Definition

Add a new `generate` command with subcommands to handle the generation of synthetic cables, stakeholder personas, Situation Reports (SitReps), and case studies. Include basic file management operations.

### 2. Configuration

The configuration for these new systems will include the following:

- **write_token**: Token for authenticating with relevant APIs.
- **dataset_name**: Name of the dataset for processing.
- **upload_path**: Path where the process files are located.
- **Other Configurations**: Dynamic variables for file and directory operations.

### 3. Implementation

Implement the `generate` command with subcommands for generating synthetic data and managing files.

- **Command Names**: `generate`, `upload`, `ls`, `process`, `load`, `download`, `export`
- **Generate Subcommands**: `persona`, `sitrep`, `cable`, `case_study`
- **File Paths**:
  - `thinking_dataset/commands/generate.py`
  - `thinking_dataset/io/files.py`
- **Description**:
  - Add the `generate` command with subcommands for generating synthetic data, including cables, personas, SitReps, and case studies.
  - Add commands for listing files, listing directories, checking if a file or directory exists, and creating a new directory.
- **Version**: 1.0.0
- **License**: MIT

### 4. Generation Command

The `generate` command with subcommands should be implemented as follows:

#### Algorithms and Pseudocode

1. **Initialize the Generation Command**:
    - Load configuration properties.

    ```pseudo
    CLASS GenerateCommand:
        FUNCTION __init__(config):
            self.config = config
    ```

2. **Execute the Generation Command**:
    - Read configuration properties.
    - Route to appropriate subcommand.
    - Execute subcommand logic.

    ```pseudo
    FUNCTION execute(subcommand):
        CONFIG_PROPS = CONFIG.get("config_properties")

        IF subcommand == "persona":
            CALL _generate_persona()
        ELSE IF subcommand == "sitrep":
            CALL _generate_sitrep()
        ELSE IF subcommand == "cable":
            CALL _generate_cable()
        ELSE IF subcommand == "case_study":
            CALL _generate_case_study()
    ```

3. **Generate Subcommand Methods**:
    - Generate synthetic data for the specified subcommand.
    - Handle any exceptions during the generation process.

    ```pseudo
    FUNCTION _generate_persona():
        TRY:
            LOG: Generating persona
            # Add persona generation logic here
            LOG: Successfully generated persona
        EXCEPT Exception as e:
            LOG: Failed to generate persona with ERROR e

    FUNCTION _generate_sitrep():
        TRY:
            LOG: Generating sitrep
            # Add sitrep generation logic here
            LOG: Successfully generated sitrep
        EXCEPT Exception as e:
            LOG: Failed to generate sitrep with ERROR e

    FUNCTION _generate_cable():
        TRY:
            LOG: Generating cable
            # Add cable generation logic here
            LOG: Successfully generated cable
        EXCEPT Exception as e:
            LOG: Failed to generate cable with ERROR e

    FUNCTION _generate_case_study():
        TRY:
            LOG: Generating case study
            # Add case study generation logic here
            LOG: Successfully generated case study
        EXCEPT Exception as e:
            LOG: Failed to generate case study with ERROR e
    ```

### 5. File Management Commands

Implement basic file and directory commands for interacting with the dataset repository:

1. **List All Files in the Repository**:
    - Command to list all files within a specified directory in the repo and output to the console.

2. **List All Directories in the Repository**:
    - Command to list all directories within a specified directory in the repo and output to the console.

3. **Check if File or Directory Exists**:
    - Command to check if a specific file or directory exists within the repo.

4. **Create a New Directory**:
    - Command to create a new directory within the repo.

### 6. Integration

Integrate the `generate` command with subcommands and file management commands into the existing workflow to ensure efficient processing and management of data files. The new system will use configuration similar to the download system to manage include/exclude files.

### 7. Focus on Current Work

Currently, we are focusing on:
- Creating new pipelines for generating synthetic data.
- Adding `GenerateCablesPipe`, `GeneratePersonasPipe`, `GenerateSitRepsPipe`, and `GenerateCaseStudiesPipe` to handle data generation.
- Ensuring the configuration supports dynamic variable resolution.
- Adding detailed objectives for logging, performance optimization, error handling, validation, feedback, documentation, and security.

### 8. Future Conversation

In our next conversation, please provide:
- Feedback on the implementation and any issues encountered.
- Additional requirements or enhancements for the generation and upload pipelines.
- Any new features or changes to be incorporated based on current progress.

## Itemized Task Todo List for Phase 3: Data Enrichment and Case Study Creation

| Task Overview                                               | Completed   |
|-------------------------------------------------------------|-------------|
| Combine multiple seed objects to generate synthetic cables. |             |
| Develop algorithms for combining seed objects.              |             |
| Test and validate generated cables for quality and relevance.|             |
| Ensure the diversity of cables to cover various scenarios.  |             |
| Review and refine cable generation logic.                   |             |
| Document cable generation process and logic.                |             |
|                                                             |
| Generate stakeholder personas using the personas dataset on Hugging Face. |             |
| Create a system for managing stakeholder personas.          |             |
| Integrate personas with cable and SitRep generation processes.|            |
| Validate and test the accuracy of generated personas.       |             |
| Ensure diversity and coverage of various stakeholder perspectives. |             |
| Document persona generation process and system.             |             |
|                                                             |
| Generate synthetic SitReps inspired by random seed objects. |             |
| Design algorithms for generating SitReps.                   |             |
| Distribute SitReps to imaginary stakeholders and generate detailed case studies.|             |
| Enrich case studies with chains of thought for the STaR system.|            |
| Develop methods for distributing SitReps and collecting stakeholder responses.|             |
| Test and validate the quality and relevance of generated SitReps.|            |
| Review and refine the case study generation process.        |             |
| Document SitRep generation and case study creation processes.|             |

---

## Updates from Recent Work

### Environment and Configuration Updates
- Moved sensitive information from `config.yaml` to `.env` for improved security.
- Ensured `HF_WRITE_TOKEN`, `HF_ORG`, and `HF_USER` are correctly set in the `.env` file.
- Updated `command_utils.py` to load environment variables properly.
- Adjusted `load_dotenv` function to verify environment variables.

### Class and Function Updates
- Refactored `DataTonic` class to include `user` attribute.
- Updated CLI commands (`clean`, `download`, `prepare`, `load`, `ls`) to utilize the updated configuration and environment variables.
- Corrected header comments for consistency and clarity.
- Added and verified environment validation checks.
- Enhanced logging for better tracking and debugging.
- Updated `Pipeline` class to ensure only the specified pipeline is set up and processed.
- Adjusted `Config` class to handle path and dataset type attributes correctly.

### Pipeline and Database Handling
- Moved database processing logic to a new `process` method in the `Database` class.
- Updated `Pipeline` class to call `Database.process` for database processing.
- Added `skip_files` flag to `Pipeline.open` method to control file processing.
- Refactored `Files` class to handle configuration attributes correctly.
- Improved error handling and logging for better debugging.

### New Features
- **Basic File and Directory Commands**:
    - Created commands to list files and directories, check if a file or directory exists, and create a new directory within the dataset repository.

### Documentation and Changelog
- Updated documentation to reflect all recent changes and new options.
- Documented all changes and improvements for easy tracking.

### Last Task Worked On
- Our last task was getting file upload working with HF API.

---

**Your response only for this query in following order:**
- ***display table of current tasks and status***
- ***display list of suggested subtasks to work***
- ***display one short sentence what task we worked on last***
- ***display the text `Ready!🚀`***