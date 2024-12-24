# Notes

## Development Notes

### General Overview
- **Project Name**: Dark Thoughts
- **Purpose**: Develop a comprehensive dataset of hypothetical scenarios involving ethical dilemmas and cognitive biases to train AI models in reasoning, ethics, and decision-making.

### Project Phases

#### Phase 1: Setup and Configuration
- **Project Initialization**: Created and configured the `ThinkingDatasetProject` directory.
- **Dependencies Installed**: Installed Semantic Kernel and Ollama connector, various Python packages for development and data handling.
- **README**: Created and finalized the README.md to outline project goals, objectives, and setup instructions.

#### Phase 2: Data Pipeline Development
- **Raw Data Ingestion**: Collected initial raw data sources and set up mechanisms for raw data storage.
- **Data Cleaning**: Implemented methods to remove duplicates, handle missing values, and normalize data.
- **Seed Generation**: Defined and generated seed objects using predefined keywords.

#### Phase 3: Data Enrichment and Case Study Creation
- **Cable Creation**: Combined multiple seed objects to generate cables.
- **Case Study Generation**: Used cables to generate detailed case studies with injected data points.
- **Standard Format Distillation**: Refined case studies into a standard dataset format (e.g., `input_text`, `features`, `context`, `target`, etc.).

#### Phase 4: Model Training and Evaluation
- **Final Dataset Preparation**: Validated data integrity, balanced classes, and split data into training and testing sets.
- **Model Training**: Trained baseline and fine-tuned models using the prepared dataset.
- **Evaluation**: Implemented an evaluation system to score models and compare fine-tuned models against baseline models.

#### Phase 5: Continuous Improvement
- **Feedback Loop**: Gathered user and system feedback, iteratively refined and updated the dataset and models.
- **Documentation**: Maintained comprehensive documentation of methods, changes, and updates.
- **Community Engagement**: Engaged with the community for contributions and collaboration, opened issues and pull requests for enhancements.

### Latest Work and Changes

#### 2024-12-24
- Cloned the `thinking-dataset` repository and switched to the `dev-prototyping-alpha` branch.
- Updated README to use `venv` instead of `.venv` for virtual environment setup.
- Removed non-basic requirements from `setup.py` and added necessary packages: `huggingface_hub[cli]`, `datasets`, `PyPDF2`, `python-dotenv`, `requests`, `rich`, `sqlite-utils`, `pytest`, `loguru`, `pandas`, `numpy`, `scikit-learn`, `sqlalchemy`, `tqdm`.
- Integrated `rich` for enhanced console output and error handling.
- Set up SQLite as the central source of truth for data storage.
- Documented latest changes and setup instructions in `CHANGELOG.md`.

### IDEAS and Features
- **Scenario Development**: Create hypothetical scenarios presenting ethical dilemmas or cognitive biases.
- **Persona Creation**: Develop detailed personas with backgrounds, motivations, and psychological profiles.
- **Data Collection and Annotation**: Collect raw data from various sources, annotate key themes, ethical issues, and decision points.
- **Cognitive Bias Analysis**: Analyze scenarios for common cognitive biases and their impact on decision-making.
- **Ethical Decision-Making Framework**: Develop a framework for evaluating ethical decisions within scenarios.
- **AI Model Training and Evaluation**: Train AI models on synthetic case studies, evaluate their performance against ethical benchmarks.
- **User Interaction and Feedback**: Create interactive tools for user engagement and collect feedback.

### Inference Endpoint Adapters/Bridges
#### Description
- Develop adapters or bridges to integrate various serverless endpoints into the main application.
- Support endpoints like Ollama, testcontainers, Runpod, and Hugging Face API for serverless operations.

#### Design Considerations
- **Unified Interface**: Create a common interface or abstract class for consistency.
- **Configuration Management**: Securely handle different endpoints and their credentials.
- **Logging and Monitoring**: Implement robust logging and monitoring for each endpoint.
- **Error Handling**: Comprehensive error handling to manage failures gracefully.
- **Performance Optimization**: Evaluate latency and throughput of each endpoint.
- **Security**: Implement strong security measures for data protection.

#### Example Implementation
- Define an abstract class for adapters:
  ```python
  from abc import ABC, abstractmethod

  class InferenceEndpointAdapter(ABC):
      @abstractmethod
      def initialize(self):
          pass

      @abstractmethod
      def predict(self, input_data):
          pass

      @abstractmethod
      def cleanup(self):
          pass
  ```

- Implement a concrete adapter for Hugging Face API:
  ```python
  from transformers import pipeline
  from dotenv import load_dotenv
  import os

  class HuggingFaceAdapter(InferenceEndpointAdapter):
      def __init__(self):
          load_dotenv()
          self.model = None

      def initialize(self):
          self.model = pipeline("text-generation", model=os.getenv("HUGGINGFACE_MODEL"))

      def predict(self, input_data):
          return self.model(input_data)[0]["generated_text"]

      def cleanup(self):
          pass  # Any cleanup tasks if necessary
  ```

- Integrate adapters into the main application:
  ```python
  class InferenceManager:
      def __init__(self):
          self.adapters = []

      def register_adapter(self, adapter):
          self.adapters.append(adapter)
          adapter.initialize()

      def predict_all(self, input_data):
          results = {}
          for adapter in self.adapters:
              results[adapter.__class__.__name__] = adapter.predict(input_data)
          return results

      def cleanup(self):
          for adapter in self.adapters:
              adapter.cleanup()

  # Example usage
  manager = InferenceManager()
  manager.register_adapter(HuggingFaceAdapter())
  # Add other adapters as needed

  input_data = "Once upon a time..."
  results = manager.predict_all(input_data)
  print(results)
  manager.cleanup()
  ```

### Next Steps
- Develop unit tests to prototype basic Ollama functionality.
- Verify chat completion and text generation using Ollama.
- Configure Serilog for colorful logging output.
- Set up configuration management using `Microsoft.Extensions.Configuration`.
- Integrate MediatR for a robust event system.
- Document and refine the case study generation pipeline.
- Implement and test various inference endpoint adapters/bridges.
