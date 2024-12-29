# Architecture

## Overview

The "Dark Thoughts" thinking-dataset project is designed to develop and analyze complex psychological scenarios, ethical dilemmas, and decision-making processes. The architecture includes key components like data ingestion, preprocessing, enrichment, model training, and evaluation. The system leverages various serverless endpoints and adapters to ensure flexibility and scalability.

## Key Components

This project relies on several core elements: Data Ingestion for collecting and storing raw data; Data Preprocessing for cleaning, transforming, and validating data; Data Enrichment and Case Study Creation for generating scenarios and case studies; Model Training and Evaluation for training and assessing AI models; Inference Endpoint Adapters for integrating various serverless endpoints; and Continuous Improvement for refining the dataset and models based on feedback. Each component plays a vital role in achieving the project's goal of analyzing complex psychological scenarios, ethical dilemmas, and decision-making processes.

### 1. Data Ingestion

- **Raw Data Sources**: Data is collected from multiple sources, including historical records, literature, user-generated content, and the WikiLeaks Cablegate dataset.
- **Data Storage**: Raw data is stored in a structured format using SQLite, a lightweight database.

### 2. Data Preprocessing

- **Data Cleaning**: Methods are implemented to remove duplicates, handle missing values, and normalize data.
- **Data Transformation**: Raw data is transformed into a standardized format suitable for further processing and analysis.
- **Data Validation**: Ensures the integrity and quality of the data before further processing.

### 3. Data Enrichment and Case Study Creation

- **Seed Generation**: Seed objects are defined and generated using predefined keywords and cables.
- **Cable Creation**: Multiple seed objects are combined to generate detailed scenarios called cables.
- **Case Study Generation**: Cables are used to create detailed case studies with injected data points.
- **Standard Format Distillation**: Case studies are refined into a consistent format for model training.

### 4. Model Training and Evaluation

- **Dataset Preparation**: Validates data integrity, balances classes, and splits data into training and testing sets.
- **Model Training**: Baseline and fine-tuned models are trained using the prepared dataset.
- **Evaluation System**: Scores models and compares fine-tuned models against baseline models.

### 5. Inference Endpoint Adapters/Bridges

- **Unified Interface**: A common interface or abstract class ensures consistency across different adapters.
- **Adapter Implementations**: Developed for various serverless endpoints such as Hugging Face, Ollama, testcontainers, and Runpod.
- **Integration**: Adapters are seamlessly integrated into the main application to leverage the best tools for various tasks.

### 6. Continuous Improvement

- **Feedback Loop**: User and system feedback is gathered to iteratively refine and update the dataset and models.
- **Documentation**: Comprehensive documentation of methods, changes, and updates is maintained.
- **Community Engagement**: The project engages with the community for contributions and collaboration, opening issues and pull requests for enhancements.

## Technology Stack

- **Python**: Core programming language for the project.
- **SQLite**: Lightweight database for storing structured data.
- **pandas**: Data manipulation and preprocessing.
- **scikit-learn**: Machine learning library for model training and evaluation.
- **rich**: Enhanced console output and error handling.
- **python-dotenv**: Manage configuration and environment variables.
- **Hugging Face Transformers**: Library for state-of-the-art NLP models.
- **Testcontainers**: Library for integration testing with containers.
- **Runpod**: Serverless computing platform.
- **python-statemachine**: Library for managing state machines within the project.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for database interactions.

## Architectural Diagram

Below is a high-level architectural diagram of the "Dark Thoughts" thinking-dataset project:

```
+------------------------------+------------------------------+
|       Data Ingestion         |      Data Preprocessing      |
| +-------------------------+  | +-------------------------+  |
| |     Raw Data Sources    |  | |     Data Cleaning       |  |
| +-------------------------+  | |     Data Transformation |  |
|                              | |     Data Validation     |  |
+-------------|----------------+ +------------|---------------+
              |                                   |
              v                                   v
+------------------------------+ +----------------------------+
|       Data Enrichment        | |       Model Training       |
| +----------------------------+ | +------------------------+ |
| |     Seed Generation        | | |    Dataset Preparation | |
| |     Cable Creation         | | |    Model Training      | |
| |     Case Studies           | | |    Evaluation System   | |
| +----------------------------+ | +------------------------+ |
+-------------|----------------+ +----------------|-----------+
              |                                   |
              v                                   v
+------------------------------+ +----------------------------+
|    Inference Endpoint        | |    Continuous Improvement  |
|        Adapters and Bridges  | |                            |
| +--------------------------+ | +--------------------------+ |
| |    Unified Interface     | | |     Feedback Loop        | |
| |    Adapter Implementation| | |     Documentation        | |
| +--------------------------+ | |     Community Engagement | |
+-------------|----------------+ +------------|---------------+
              |                                   |
              v                                   v
+-------------------------------------------------------------+
|                          Foundation                         |
| +---------------------------------------------------------+ |
| |               Core Technologies & Infrastructure        | |
| +---------------------------------------------------------+ |
+-------------|------------------^----------------------------+
              |                  |                            |
              +------------------+                            |
                       Feedback Loop                          |
                       (Generation to Input)                  |
+-------------------------------------------------------------+
|     Synthetic SitReps and Case Studies Creation Cycle       |
| +---------------------------------------------------------+ |
| |  Synthetic SitReps Creation -> Case Study Generation -> | |
| |  Feeding Back into Data Ingestion for Continuous Loop   | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
```

## Conclusion

The "Dark Thoughts" thinking-dataset robust and scalable architecture is designed to handle complex psychological scenarios, ethical dilemmas, and decision-making processes. The integration of various serverless endpoints and adapters ensures flexibility and scalability, while the continuous feedback loop facilitates iterative improvement. This meticulous design not only supports the current needs of the project but also lays a solid foundation for future enhancements, pushing the boundaries of AI and cognitive science research. Through strategic implementation, we aim to significantly advance our understanding and replication of human thought patterns, contributing to the fields of artificial intelligence and machine learning.
