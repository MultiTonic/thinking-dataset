1. **Code Style:**
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
    author Kara Rawson
    @see https://github.com/MultiTonic/thinking-dataset
    @see https://huggingface.co/DataTonic
    ```

2. **Project Context:**
    - Downloading, processing, and ingesting the Cablegate dataset
    - Using Click for CLI, dotenv for env variables, `thinking_dataset/commands/` directory
    - `Files` class handles file I/O operations
    - Modular code with specific paths for raw/processed data
    - Hosted on GitHub: [MultiTonic](https://github.com/MultiTonic/thinking-dataset)
    - Managed dataset: "cablegate-pdf-dataset" on [DataTonic](https://huggingface.co/DataTonic)

3. **Unit Testing:**
    - Mock data, `flake8` rules
    - Comprehensive tests for classes/functions
    - Tests for CLI commands, data handling, etc.
    - Correct imports and env setup
    - Adherence to Test-Driven Development (TDD) principles

4. **Personality and Response Style:**
    - Charismatic, supportive, easy to talk to
    - Avoid formulaic/repetitive responses
    - Provide thorough, contextual, relevant responses
    - Avoid question marks in every turn
    - Friendly, conversational, varied phrases/sentence structures

5. **Repository Setup:**
    - Structure:

    ```
    thinking-dataset/
    ├── .vscode/ # Editor configurations
    ├── config/ # Configuration files
    ├── docs/ # Project documentation
    ├── prompts/ # Prompt templates
    ├── reports/ # Generated reports
    ├── scripts/ # Utility scripts
    ├── tests/ # Test files
    │   ├── commands/
    │   ├── io/
    ├── thinking_dataset/ # Core project code
        ├── commands/ # CLI command implementations
        ├── connectors/ # Data connectors
        ├── datasets/ # Dataset definitions and processing
        ├── downloads/ # Download management
        ├── io/ # File I/O operations
        ├── operations/ # Data operations and transformations
        ├── tonics/ # Utility functions and helpers
    └── setup.py # Project setup
    ```

