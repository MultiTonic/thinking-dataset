# Prompt Template for Work Specification

## Overview

Implement new features: critical pipeline components, data enrichment, and case study creation. Objectives include generating synthetic scenarios and case studies, managing file operations, and ensuring dynamic configuration.

## Details

### 1. Command Definition

Add a `generate` command with subcommands for generating synthetic cables, stakeholder personas, SitReps, and case studies. Include basic file management operations.

### 2. Configuration

Include the following configurations:
- **write_token**: Token for API authentication.
- **dataset_name**: Dataset for processing.
- **upload_path**: Path for process files.
- **Other Configurations**: Dynamic variables for file and directory operations.

### 3. Implementation

Implement the `generate` command with subcommands for generating synthetic data and managing files.

- **Command Names**: `generate`, `upload`, `ls`, `process`, `load`, `download`, `export`
- **Subcommands**: `persona`, `sitrep`, `cable`, `case_study`
- **File Paths**:
  - `thinking_dataset/commands/generate.py`
  - `thinking_dataset/io/files.py`
  - `thinking_dataset/tonics/data_tonic.py`
  - `thinking_dataset/pipelines/pipeline.py`
  - `thinking_dataset/pipes/pipe.py`
  - `thinking_dataset/db/database.py`
  - `thinking_dataset/datasets/dataset.py`
- **Description**:
  - Add the `generate` command with subcommands for generating synthetic data (cables, personas, SitReps, case studies).
  - Add commands for file and directory management.
- **Version**: 1.0.0
- **License**: MIT

### 4. Generation Command

Implement the `generate` command with subcommands:

1. **Initialize the Generation Command**:
    - Load configuration properties.

2. **Execute the Generation Command**:
    - Read configuration properties.
    - Route to appropriate subcommand.
    - Execute subcommand logic.

3. **Generate Subcommand Methods**:
    - Generate synthetic data for the specified subcommand.
    - Handle exceptions during the generation process.

### 5. File Management Commands

Implement basic file and directory commands:

1. **List All Files**: Command to list all files within a specified directory.
2. **List All Directories**: Command to list all directories within a specified directory.
3. **Check if File/Directory Exists**: Command to check existence within the repo.
4. **Create a New Directory**: Command to create a new directory within the repo.

### 6. Integration

Integrate the `generate` command and file management commands into the existing workflow. Use configuration similar to the download system to manage include/exclude files.

### 7. Focus on Current Work

Focus on:
- Creating pipelines for generating synthetic data.
- Adding `GenerateCablesPipe`, `GeneratePersonasPipe`, `GenerateSitRepsPipe`, `GenerateCaseStudiesPipe`.
- Ensuring dynamic configuration.
- Logging, performance optimization, error handling, validation, feedback, documentation, security.

### 8. Future Conversation

Next session, provide:
- Feedback on implementation and issues encountered.
- Additional requirements or enhancements.
- Any new features or changes based on progress.

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

### Developing Algorithms for Combining Seed Objects

We will focus on developing algorithms for combining seed objects to generate synthetic cables.

#### 1. Load Seed Objects from Database

Query the database to retrieve the seed objects along with their IDs:
```sql
SELECT id, content FROM cablegate_pdf WHERE LENGTH(content) BETWEEN 500 AND 10000;
```

#### 2. Random Selection

Randomly pick three seed objects. Assuming we have a list of seed objects obtained from the database query, we'll use the `select_random_objects` function:
```pseudo
FUNCTION select_random_objects(seed_objects, count):
    RETURN random.sample(seed_objects, count)
```
Using the function, we pick three random seed objects from the retrieved dataset:

#### 3. JSON Structure

Create a JSON structure to store the inspirations. Only include the content and ID:
```json
{
  "inspirations": [
    {
      "id": 1,
      "content": "Seed Object 1"
    },
    {
      "id": 2,
      "content": "Seed Object 2"
    },
    {
      "id": 3,
      "content": "Seed Object 3"
    }
  ]
}
```

---

**Your response only for this query in following order:**
- ***display table of current tasks and status***
- ***display list of suggested subtasks to work***
- ***display one short sentence what task we worked on last***
- ***display the text `Ready!🚀`***