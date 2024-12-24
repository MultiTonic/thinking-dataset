# Architecture

## Project Architecture

This document provides an overview of the architecture and key components of the "Dark Thoughts" thinking-dataset project. It describes how different parts of the system interact and the technologies used to build the project.

## Overview

The "Dark Thoughts" thinking-dataset project is designed to develop and analyze complex psychological scenarios, ethical dilemmas, and decision-making processes. The architecture is composed of several key components, including data ingestion, preprocessing, enrichment, model training, and evaluation. The system leverages various serverless endpoints and adapters to ensure flexibility and scalability.

## Key Components

### 1. Data Ingestion

- **Raw Data Sources**: The project collects data from multiple sources, including historical records, literature, and user-generated content.
- **Data Storage**: Raw data is stored in a structured format using SQLite, a lightweight database.

### 2. Data Preprocessing

- **Data Cleaning**: Methods are implemented to remove duplicates, handle missing values, and normalize data.
- **Data Transformation**: The raw data is transformed into a standardized format suitable for further processing and analysis.

### 3. Data Enrichment and Case Study Creation

- **Seed Generation**: Seed objects are defined and generated using predefined keywords.
- **Cable Creation**: Multiple seed objects are combined to generate detailed scenarios called cables.
- **Case Study Generation**: Cables are used to create detailed case studies with injected data points.
- **Standard Format Distillation**: Case studies are refined into a consistent format for model training.

### 4. Model Training and Evaluation

- **Dataset Preparation**: Data integrity is validated, classes are balanced, and data is split into training and testing sets.
- **Model Training**: Baseline and fine-tuned models are trained using the prepared dataset.
- **Evaluation System**: An evaluation system is implemented to score models and compare fine-tuned models against baseline models.

### 5. Inference Endpoint Adapters/Bridges

- **Unified Interface**: A common interface or abstract class is created to ensure consistency across different adapters.
- **Adapter Implementations**: Concrete implementations are developed for various serverless endpoints such as Ollama, testcontainers, Runpod, and Hugging Face API.
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

## Architectural Diagram

Below is a high-level architectural diagram of the "Dark Thoughts" thinking-dataset project:

```
+--------------------+            +--------------------+
|    Data Ingestion  |            |  Data Preprocessing|
| +----------------+ |            | +----------------+ |
| | Raw Data       | |            | | Data Cleaning  | |
| | Sources        | |            | | Data Transformation |
| +----------------+ |            | +----------------+ |
+--------|-----------+            +--------|-----------+
         |                              |
         v                              v
+--------------------+            +--------------------+
| Data Enrichment    |            |  Model Training    |
| +----------------+ |            | +----------------+ |
| | Seed Generation| |            | | Dataset        | |
| | Cable Creation | |            | | Preparation    | |
| | Case Studies   | |            | | Model Training | |
| +----------------+ |            | | Evaluation     | |
+--------|-----------+            +--------------------+
         |                              |
         v                              v
+--------------------+            +--------------------+
|  Inference Endpoint|            | Continuous         |
|  Adapters/Bridges  |            | Improvement        |
| +----------------+ |            | +----------------+ |
| | Unified Interface|            | | Feedback Loop  | |
| | Adapter Impl.  | |            | | Documentation  | |
| +----------------+ |            | | Community      | |
+--------------------+            | | Engagement     | |
                                  +--------------------+
```

## Conclusion

This `ARCHITECTURE.md` provides a detailed overview of the "Dark Thoughts" thinking-dataset project's architecture. It describes the key components and their interactions, providing a comprehensive understanding of how the system is designed and implemented.
