# Roadmap

## Project Roadmap

This document outlines the future plans, features, and milestones for the "Dark Thoughts" thinking-dataset project. The roadmap is designed to guide the project's development and ensure continuous improvement.

## Milestones

### Phase 1: Initial Setup and Configuration
- **Project Initialization**
  - [x] Create and configure the project directory.
  - [x] Set up version control using Git.
- **Environment Setup**
  - [x] Create a virtual environment and install dependencies.
  - [x] Configure environment variables using `.env` file.
- **Initial Documentation**
  - [x] Create essential documentation files: README.md, CONTRIBUTING.md, LICENSE.md.

### Phase 2: Data Pipeline Development
- **Raw Data Ingestion**
  - [ ] Collect initial raw data from various sources.
  - [ ] Store raw data in a structured format using SQLite.
- **Data Preprocessing**
  - [ ] Implement data cleaning methods to remove duplicates and handle missing values.
  - [ ] Normalize and transform data into a standardized format.
- **Seed Generation**
  - [ ] Define and generate seed objects using predefined keywords.

### Phase 3: Data Enrichment and Case Study Creation
- **Cable Creation**
  - [ ] Combine multiple seed objects to generate cables (detailed scenarios).
- **Case Study Generation**
  - [ ] Use cables to create detailed case studies with injected data points.
- **Standard Format Distillation**
  - [ ] Refine case studies into a consistent format for model training.

### Phase 4: Model Training and Evaluation
- **Dataset Preparation**
  - [ ] Validate data integrity and balance classes.
  - [ ] Split data into training and testing sets.
- **Model Training**
  - [ ] Train baseline models using the prepared dataset.
  - [ ] Fine-tune models for improved performance.
- **Evaluation System Development**
  - [ ] Implement an evaluation system to score models.
  - [ ] Compare fine-tuned models against baseline models.

### Phase 5: Inference Endpoint Adapters/Bridges
- **Unified Interface**
  - [ ] Create a common interface or abstract class for adapters.
- **Adapter Implementations**
  - [ ] Develop concrete implementations for various endpoints (Ollama, testcontainers, Runpod, Hugging Face API).
- **Integration**
  - [ ] Seamlessly integrate adapters into the main application.

### Phase 6: Continuous Improvement
- **Feedback Loop**
  - [ ] Gather user and system feedback to iteratively refine the dataset and models.
- **Documentation**
  - [ ] Maintain comprehensive documentation of methods, changes, and updates.
- **Community Engagement**
  - [ ] Engage with the community for contributions and collaboration.
  - [ ] Open issues and pull requests for enhancements.

### Future Features and Enhancements
- **Enhanced Scenario Development**
  - [ ] Develop more complex and diverse hypothetical scenarios.
  - [ ] Include multi-layered ethical dilemmas and cognitive biases.
- **Advanced Model Evaluation**
  - [ ] Implement advanced metrics for model evaluation.
  - [ ] Develop benchmarking tools for comparing different models.
- **User Interaction Tools**
  - [ ] Create interactive tools for users to engage with scenarios and provide feedback.
  - [ ] Develop visualization tools for better understanding of decision-making processes.

## Timeline

### Q1 2025
- Complete data enrichment and case study creation.
- Begin model training and evaluation.
- Develop and test initial inference endpoint adapters.

### Q2 2025
- Refine and optimize model training processes.
- Implement advanced model evaluation metrics.
- Launch interactive user tools for scenario engagement.

### Q3 2025
- Gather and integrate user feedback for continuous improvement.
- Expand scenario database with more complex and diverse cases.
- Enhance community engagement and contributions.

### Q4 2025
- Finalize and document all project components.
- Prepare for a major version release.
- Plan for future research and development initiatives.
