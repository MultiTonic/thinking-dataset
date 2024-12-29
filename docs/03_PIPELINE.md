# Pipeline

## Overview

This document outlines the data pipeline for the "Dark Thoughts" project, from data ingestion to model training and evaluation. The pipeline is designed to handle ethical dilemmas, cognitive biases, and decision-making processes, leveraging various serverless inference endpoints.

## Pipeline Phases

### Phase 1: Setup and Configuration
1. **Project Initialization**
   - Create and configure the project directory.
   - Set up version control using Git.

2. **Environment Setup**
   - Create a virtual environment and install dependencies using `venv` and `pip`.
   - Ensure all necessary packages are included in `setup.py`.

3. **Configuration Management**
   - Use `python-dotenv` to manage configuration files and environment variables securely.

### Phase 2: Data Pipeline Development
1. **Raw Data Ingestion**
   - Collect initial raw data from various sources (historical records, literature, user-generated content, and the WikiLeaks Cablegate dataset).
   - Store raw data in a structured format using SQLite.

2. **Data Cleaning and Preprocessing**
   - Implement methods to remove duplicates, handle missing values, and normalize data.
   - Use `pandas` for efficient data manipulation.

3. **Seed Generation**
   - Define and generate seed objects using predefined keywords.
   - Store seeds in the SQLite database.

### Phase 3: Data Enrichment and Case Study Creation
1. **Cable Creation**
   - Combine multiple seed objects to generate cables (detailed scenarios).

2. **Case Study Generation**
   - Use cables to create detailed case studies with injected data points.
   - Standardize case studies into a dataset format (e.g., `input_text`, `features`, `context`, `target`, etc.).

3. **Distillation to Standard Format**
   - Refine case studies into a consistent format for model training.

### Phase 4: Model Training and Evaluation
1. **Final Dataset Preparation**
   - Validate data integrity, balance classes, and split data into training and testing sets.

2. **Model Training**
   - Train baseline and fine-tuned models using the prepared dataset.
   - Use `scikit-learn` for implementing machine learning algorithms.

3. **Evaluation System Development**
   - Implement an evaluation system to score models and compare fine-tuned models against baseline models.

### Phase 5: Continuous Improvement
1. **Feedback Loop**
   - Gather user and system feedback, iteratively refine and update the dataset and models.

2. **Documentation**
   - Maintain comprehensive documentation of methods, changes, and updates.

3. **Community Engagement**
   - Engage with the community for contributions and collaboration.
   - Open issues and pull requests for enhancements.

## Inference Endpoint Adapters/Bridges
1. **Unified Interface**
   - Create a common interface or abstract class for consistency across adapters.

2. **Adapter Implementations**
   - Develop concrete implementations for various endpoints (LLama.cpp, Ollama, testcontainers, Runpod).

   Example Algorithm:
   - Define an abstract class `InferenceEndpointAdapter` with methods `initialize`, `predict`, and `cleanup`.
   - Implement the `LLamaCppAdapter` class:
     - Load environment variables.
     - Initialize the model using `LLama` with the provided model path.
     - Implement the `predict` method to generate predictions.
     - Implement the `cleanup` method to handle any cleanup tasks if necessary.

3. **Integration with Main Application**
   - Ensure seamless interaction between adapters and the main application.

   Example Algorithm:
   - Create an `InferenceManager` class to manage adapters.
     - Register adapters and initialize them.
     - Use a method to predict results from all registered adapters.
     - Implement a cleanup method to clean up all adapters.

## Tools and Technologies
- **Python**: Core programming language for the project.
- **SQLite**: Lightweight database for storing structured data.
- **pandas**: Data manipulation and preprocessing.
- **scikit-learn**: Machine learning library for model training and evaluation.
- **rich**: Enhanced console output and error handling.
- **python-dotenv**: Manage configuration and environment variables.
- **LLama.cpp**: For text-generation and NLP tasks.
- **testcontainers**: For integration testing with containers.
- **Runpod**: Serverless computing platform.

## Next Steps
- Implement and test various inference endpoint adapters/bridges.
- Develop unit tests to prototype basic LLama.cpp functionality.
- Verify chat completion and text generation using LLama.cpp.
- Configure Serilog for colorful logging output.
- Set up configuration management using `Microsoft.Extensions.Configuration`.
- Integrate MediatR for a robust event system.
- Document and refine the case study generation pipeline.
