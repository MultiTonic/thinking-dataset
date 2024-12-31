# Pipeline

## Overview

This document provides a comprehensive overview of the data pipeline for the "Dark Thoughts" project. The pipeline covers all stages from data ingestion to model training and evaluation, tailored to handle complex tasks involving ethical dilemmas, cognitive biases, and decision-making processes. By leveraging various serverless inference endpoints, the pipeline ensures flexibility, scalability, and efficiency. This guide details each phase of the pipeline, the key components involved, and the tools and technologies used to build and maintain the system.

## Pipeline Phases

### Phase 1: Setup and Configuration

The first phase involves project initialization, which includes creating and configuring the project directory and setting up version control using Git. Following that, the environment setup is established by creating a virtual environment and installing necessary dependencies using `venv` and `pip`. Configuration management is handled using `python-dotenv` to securely manage configuration files and environment variables, ensuring that sensitive information is protected.

### Phase 2: Data Pipeline Development

In the data pipeline development phase, raw data ingestion is carried out by gathering data from multiple sources such as historical records, literature, user-generated content, and the WikiLeaks Cablegate dataset. This raw data is stored in a structured format using SQLite. The data cleaning and preprocessing steps involve implementing methods to remove duplicates, handle missing values, and normalize data, with `pandas` being used for efficient data manipulation. Seed generation is the final step in this phase, where seed objects are defined and generated using predefined keywords, and then stored in the SQLite database.

### Phase 3: Data Enrichment and Case Study Creation

During the data enrichment and case study creation phase, multiple seed objects are combined to generate detailed scenarios known as cables. These cables are then used to create detailed case studies with injected data points. The case studies are standardized into a consistent format for model training. This phase ensures that all case studies are refined into a format that is suitable for training the models, maintaining consistency and quality throughout the process.

### Phase 4: Model Training and Evaluation

The model training and evaluation phase starts with final dataset preparation, where the integrity of the data is validated, class distributions are balanced, and the data is split into training and testing sets. Model training involves training both baseline and fine-tuned models using the prepared dataset, with `scikit-learn` being used for implementing machine learning algorithms. An evaluation system is developed to score the models and compare the performance of fine-tuned models against baseline models, ensuring that the best models are selected based on their performance.

### Phase 5: Continuous Improvement

In the continuous improvement phase, user and system feedback is gathered and analyzed to iteratively refine and update the dataset and models. Comprehensive documentation of methods, changes, and updates is maintained to ensure transparency and reproducibility. The project engages with the community for contributions and collaboration, opening issues and pull requests for enhancements. This phase ensures that the project remains up-to-date and benefits from community input and feedback.

## Inference Endpoint Adapters/Bridges

The inference endpoint adapters/bridges section focuses on establishing a unified interface or abstract class to ensure consistency across all adapters. Concrete implementations for various endpoints such as Hugging Face, Ollama, testcontainers, and Runpod are developed. Seamless integration of these adapters into the main application is ensured to facilitate smooth operation and data flow.

## Tools and Technologies

The project leverages a robust technology stack including Python as the core programming language, SQLite for structured data storage, and libraries like pandas for data manipulation and preprocessing. scikit-learn is used for model training and evaluation, and rich enhances console output and error handling. python-dotenv manages configuration and environment variables, while Hugging Face Transformers provide advanced NLP models. Testcontainers and Runpod are used for integration testing and serverless computing, respectively, and LLama.cpp is employed for text-generation and NLP tasks.

## Next Steps

The next steps involve implementing and testing various inference endpoint adapters/bridges, developing unit tests to prototype basic LLama.cpp functionality, verifying chat completion and text generation using LLama.cpp, and documenting and refining the case study generation pipeline.
