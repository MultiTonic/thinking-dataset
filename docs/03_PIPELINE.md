# Pipeline

## Overview

This document provides an overview of the data pipeline for the "Dark Thoughts" project, covering all stages from data ingestion to model training and evaluation. The pipeline handles complex tasks involving ethical dilemmas, cognitive biases, and decision-making processes by leveraging various serverless inference endpoints to ensure flexibility, scalability, and efficiency.

## Pipeline Phases

### Phase 1: Setup and Configuration

- **Project Initialization**: Create and configure the project directory. Set up version control using Git.
- **Environment Setup**: Create a virtual environment and install necessary dependencies using `venv` and `pip`.
- **Configuration Management**: Use `python-dotenv` to manage configuration files and environment variables securely.

### Phase 2: Data Pipeline Development

- **Raw Data Ingestion**: Gather data from sources such as historical records, literature, user-generated content, and the WikiLeaks Cablegate dataset. Store data in SQLite.
- **Data Cleaning and Preprocessing**: Remove duplicates, handle missing values, and normalize data using `pandas` for data manipulation.
- **Seed Generation**: Define and generate seed objects using predefined keywords and store them in SQLite.

### Phase 3: Data Enrichment and Case Study Creation

- **Cable Creation**: Combine multiple seed objects to generate detailed scenarios known as cables.
- **Persona Database**: Generate and store stakeholder personas using the personas dataset on Hugging Face.
- **Synthetic SitRep Generation**: Generate synthetic Situation Reports (SitReps) inspired by random seed objects.
- **Case Study Generation**: Distribute SitReps to imaginary stakeholders, generate detailed case studies, and enrich them with a chain of thoughts for use in Self-Teaching with Reinforcement (STaR).

### Phase 4: Model Training and Evaluation

- **Dataset Preparation**: Validate data integrity, balance classes, and split data into training and testing sets.
- **Model Training**: Train baseline models using the prepared dataset, followed by fine-tuning models for improved performance using `scikit-learn`.
- **Evaluation System Development**: Implement an evaluation system to score models and compare fine-tuned models against baseline models.

### Phase 5: Continuous Improvement

- **Feedback Loop**: Gather user and system feedback to iteratively refine the dataset and models.
- **Documentation**: Maintain comprehensive documentation of methods, changes, and updates.
- **Community Engagement**: Engage with the community for contributions and collaboration.

## Inference Endpoint Adapters/Bridges

- **Unified Interface**: Establish a unified interface or abstract class for all adapters.
- **Adapter Implementations**: Develop concrete implementations for various endpoints (e.g., Hugging Face, Ollama, testcontainers, Runpod).
- **Integration**: Seamlessly integrate adapters into the main application.

## Tools and Technologies

- **Python**: Core programming language.
- **SQLite**: Structured data storage.
- **pandas**: Data manipulation and preprocessing.
- **scikit-learn**: Model training and evaluation.
- **rich**: Console output and error handling.
- **python-dotenv**: Configuration management.
- **Hugging Face Transformers**: NLP models.
- **Testcontainers**: Integration testing with containers.
- **Runpod**: Serverless computing.
- **LLama.cpp**: Text-generation and NLP tasks.
- **SQLAlchemy**: Database interactions.
- **DB Browser for SQLite**: Database administration.
- **datasets**: Accessing and sharing datasets.
- **PyPDF2**: PDF toolkit.
- **click**: Command line interface creation tool.
- **requests**: HTTP requests.
- **sqlite-utils**: Working with SQLite databases.
- **pytest**: Testing framework.
- **pytest-html**: HTML report generation for pytest.
- **pytest-cov**: Coverage reporting for pytest.
- **loguru**: Logging library.
- **numpy**: Scientific computing.
- **tqdm**: Progress bar library.
- **pydantic**: Data validation and settings management.

## Next Steps

- Implement and test various inference endpoint adapters/bridges.
- Develop unit tests to prototype basic LLama.cpp functionality.
- Verify chat completion and text generation using LLama.cpp.
- Document and refine the case study generation pipeline.
