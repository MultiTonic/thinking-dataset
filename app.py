import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
from pydantic import Field, BaseModel
# from testcontainers.ollama import OllamaContainer
import requests

from distilabel.llms import OpenAILLM, AzureOpenAILLM, OllamaLLM, vLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, GeneratorStep
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput
from distilabel.distiset import Distiset

from datasets import Dataset, load_dataset

from dotenv import load_dotenv

from prompts import SITREPPROMPT

from scripts.utilities.tcollamad import OptimizedTestContainerOllamaLLM, ContainerConfig

# Load environment variables from .env file
load_dotenv()

# Redirect stdout to support UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    encoding='utf-8'
)

# Step Input/Output Schemas
class CableContent(BaseModel):
    cables: str

class PreparedContent(BaseModel):
    prepared_content: str

class Message(BaseModel):
    messages: List[Dict[str, str]]

class ComparisonPrompt(BaseModel):
    comparison_prompt: str

# Custom prompt templates
SUMMARY_PROMPT = """{cable_content}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

def clean_content(text: str) -> str:
    import re
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'[^ -~]', '', text)  # Remove non-ASCII characters
    return text.strip()

class LoadLocalDataset(GeneratorStep):
    file_path: str = Field(description="Path to the local parquet file")
    input_batch_size: int = Field(default=32, description="Number of items to process in each batch")

    @property
    def inputs(self) -> List[str]:
        return []  # No inputs, this step generates data from file

    @property
    def outputs(self) -> List[str]:
        return ["cables"]  # Outputs the loaded cables

    def process(self, offset: Optional[int] = None) -> StepOutput:
        dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
        start = offset or 0
        end = min(start + self.input_batch_size, len(dataset))

        while start < len(dataset):
            batch = []
            for i in range(start, end):
                cable_row = dataset[i]
                if "cleaned_content" in cable_row:
                    cable_content = clean_content(cable_row["cleaned_content"])
                    if cable_content:  # Ensure the cleaned content is not empty
                        batch.append({"cables": cable_content})
                    else:
                        logging.warning(f"Row {i} has empty 'cleaned_content', skipping.")
                else:
                    logging.warning(f"Row {i} missing 'cleaned_content', skipping.")

            if batch:
                yield batch
            else:
                logging.warning(f"No valid cables found in batch starting at index {start}.")

            start = end
            end = min(start + self.input_batch_size, len(dataset))

class PrepareContentStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["cables"]

    @property
    def outputs(self) -> List[str]:
        return ["prepared_content"]
    
    def process(self, inputs: StepInput) -> StepOutput:
        prepared_batch = [{"prepared_content": item["cables"]} for item in inputs if "cables" in item]
        if prepared_batch:
            yield prepared_batch
        else:
            logging.warning("No 'prepared_content' generated in PrepareContentStep.")

class PrepareMessagesStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["comparison_prompt"]  # Updated to match the output from RandomSampleForComparison

    @property
    def outputs(self) -> List[str]:
        return ["messages"]
    
    def process(self, inputs: StepInput) -> StepOutput:
        output_batch = []
        for item in inputs:
            if "comparison_prompt" in item:
                messages = [
                    {"role": "system", "content": SITREPPROMPT},
                    {"role": "user", "content": item["comparison_prompt"]}
                ]
                output_batch.append({"messages": messages})
        
        if output_batch:
            yield output_batch
        else:
            logging.error("No valid messages generated to yield in PrepareMessagesStep.")

class RandomSampleForComparison(Step):
    num_comparisons: int = Field(default=2000, description="Number of comparisons to generate")
    sample_size: int = Field(default=200, description="Size of the sample to draw from")

    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["comparison_prompt"]

    def process(self, inputs: StepInput) -> StepOutput:
        cable_sample = [item for item in inputs if "prepared_content" in item]
        available_comparisons = len(cable_sample) // 3
        total_comparisons = min(self.num_comparisons, available_comparisons)

        if total_comparisons == 0:
            logging.warning("Not enough prepared_content items to generate comparisons.")
            return

        for _ in range(total_comparisons):
            sampled = random.sample(cable_sample, 3)
            comparison_prompt = COMPARISON_PROMPT.format(
                cable_1=sampled[0]["prepared_content"],
                cable_2=sampled[1]["prepared_content"],
                cable_3=sampled[2]["prepared_content"]
            )
            yield [{"comparison_prompt": comparison_prompt}]

def create_pipeline():
    with Pipeline(
        name="openai-casestudy-pipeline",
        description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
    ) as pipeline:
        load_dataset_step = LoadLocalDataset(
            name="load_cablegate_dataset",
            file_path=os.path.join("scripts", "cables", "cleaned_data.parquet"),
            input_batch_size=32
        )

        prepare_content_step = PrepareContentStep(
            name="prepare_content"
        )

        sample_for_comparison_step = RandomSampleForComparison(
            name="sample_for_comparison",
            num_comparisons=2000,
            sample_size=200
        )

        prepare_messages_comparison_step = PrepareMessagesStep(
            name="prepare_messages_comparison"
        )

        # Initialize optimized LLM with multiple containers
        ollama_llm = OptimizedTestContainerOllamaLLM(
            model="yi:6b-q4_K_M",  # Using Q4_K_M quantization for all instances
            num_instances=4,  # Number of parallel instances
            base_port=11434  # Base port for the first instance
        )

        compare_cables_step = ChatGeneration(
            name="compare_cables",
            llm=ollama_llm,
            input_batch_size=32,
            input_mappings={"messages": "messages"}, 
            output_mappings={"generation": "generation"},  
            generation_kwargs={
                "temperature": 0.9,
                "max_new_tokens": 4095,
            }
        )

        # Define the pipeline flow
        load_dataset_step \
            >> prepare_content_step \
            >> sample_for_comparison_step \
            >> prepare_messages_comparison_step \
            >> compare_cables_step

    return pipeline

def process_dataset(pipeline: Pipeline, parameters: Dict[str, Any]) -> Distiset:
    try:
        return pipeline.run(parameters=parameters, use_cache=False)
    except Exception as e:
        logging.error(f"Error running the pipeline: {e}")
        raise

if __name__ == "__main__":
    # Ensure that environment variables are set for sensitive information
    required_env_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_BASE_URL"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    huggingface_token = os.getenv("HUGGINGFACE_TOKEN", "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")  # Consider moving this to env variables as well

    pipeline = create_pipeline()

    # Process comparisons
    comparison_distiset = process_dataset(pipeline, {
        "load_cablegate_dataset": {
            "file_path": os.path.join("scripts", "cables", "cleaned_data.parquet"),
        },
        "compare_cables": {
            "generation_kwargs": {  # Moved generation_kwargs here as part of ChatGeneration step
                "temperature": 0.9,
                "max_new_tokens": 4095,
            }
        },
        "sample_for_comparison": {
            "num_comparisons": 2000,
            "sample_size": 200,
        },
    })
    
    # Access the correct key from Distiset
    compare_cables_output = comparison_distiset.get("compare_cables", {})
    generation_data = compare_cables_output.get("generation", [])

    # Convert to Hugging Face Dataset format
    if isinstance(generation_data, list) and generation_data:
        # Assuming each generation has a 'generation' key
        # Convert list of dicts to dict of lists
        dataset_dict = {}
        for entry in generation_data:
            for key, value in entry.items():
                dataset_dict.setdefault(key, []).append(value)
        
        comparison_dataset = Dataset.from_dict(dataset_dict)
    else:
        comparison_dataset = Dataset.from_dict({})

    if len(comparison_dataset) > 0:
        try:
            comparison_dataset.push_to_hub(
                "DataTonic/BusinessCaseStudies",
                private=True,
                token=huggingface_token
            )
            logging.info("Comparison dataset successfully pushed to the Hugging Face Hub.")
        except Exception as e:
            logging.error(f"Failed to push dataset to the Hub: {e}")
    else:
        logging.warning("Comparison dataset is empty and will not be pushed to the Hub.")

    logging.info("Pipeline execution completed.")
