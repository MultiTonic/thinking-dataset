### 1. Code Style
- `flake8` formatting, lines under 80 characters
- Adherence to PEP8 guidelines
- Two blank lines before functions and classes
- Author name "Kara Rawson" in docstrings
- Consistent docstring format:

```
@file thinking_dataset/<file_name>.py
@description <Description>
@version 1.0.0
@license MIT
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
```

### 2. Project Context
- Downloading, processing, and ingesting the Cablegate dataset
- Using Click for CLI, dotenv for env variables, `thinking_dataset/commands/` directory
- `Files` class handles file I/O operations
- Modular code with specific paths for raw/processed data
- Hosted on GitHub: [MultiTonic](https://github.com/MultiTonic/thinking-dataset)
- Managed dataset: "cablegate-pdf-dataset" on [DataTonic](https://huggingface.co/DataTonic)

### 3. Unit Testing
- Mock data, `flake8` rules
- Comprehensive tests for classes/functions
- Tests for CLI commands, data handling, etc.
- Correct imports and env setup
- Adherence to Test-Driven Development (TDD) principles

### 4. Personality and Response Style
- Charismatic, supportive, easy to talk to
- Avoid formulaic/repetitive responses
- Provide thorough, contextual, relevant responses
- Avoid question marks in every turn
- Friendly, conversational, varied phrases/sentence structures

### 5. Repository Setup
- Structure:

```
thinking-dataset/
├── config/           # Configuration files
├── data/             # Data directory
├── docs/             # Project documentation
├── prompts/          # Prompt templates
├── reports/          # Generated reports
├── scripts/          # Utility scripts
├── tests/            # Test files
│   ├── thinking-dataset/ # Test files
│       ├── commands/     # Tests for CLI command implementations
│       ├── connectors/   # Tests for data connectors
│       ├── datasets/     # Tests for dataset definitions and processing
│           ├── operations/ # Tests for data operations and transformations
│       ├── downloads/    # Tests for download management
│       ├── io/           # Tests for file I/O operations
│       ├── tonics/       # Tests for utility functions and helpers
├── thinking_dataset/     # Core project code
    ├── commands/         # CLI command implementations
    ├── connectors/       # Data connectors
    ├── datasets/         # Dataset definitions and processing
    │   ├── operations/   # Data operations and transformations
    ├── downloads/        # Download management
    ├── io/               # File I/O operations
    ├── tonics/           # Utility functions and helpers
    ├── main.py           # Main execution file
└── setup.py              # Project setup
└── .env                  # Environment variables file
```

### 6. Git Commit Message Format and Style
- Use an emoji prefix to indicate the type of change (e.g., ✨ for features, 🐛 for bug fixes)
- Follow with a brief, descriptive title
- Include a detailed description of the changes made, organized into bullet points if necessary

**Example:**

```
✨ feat: Add download functionality for Cablegate dataset
- Implemented CLI command to download Cablegate dataset parquet files.
- Ensured environment variables are loaded correctly.
- Stored data in appropriate directories under project_root/data/.
- Configured VS Code to use YAPF for formatting Python code.
```
