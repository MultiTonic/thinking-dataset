# test_app.py

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
from distilabel.llms.base import LLM, AsyncLLM

import locale
import codecs

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

import numpy as np
import warnings
import asyncio

# Suppress numpy-related warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numpy')

# Version check
if np.__version__.startswith('2'):
    import subprocess
    import sys
    
    print("Detected NumPy 2.x. Downgrading to compatible version...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0", "--force-reinstall"])
    print("NumPy downgrade complete. Please restart the application.")
    sys.exit(0)

#logger
from scripts.utilities.easylog import EasyLogger
easy_logger = EasyLogger()
easy_logger.initialize()

# Load environment variables from .env file
load_dotenv()


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
    batch_size: int = Field(default=32, description="Number of items to process in each batch")

    @property
    def inputs(self) -> List[str]:
        return []

    @property
    def outputs(self) -> List[str]:
        return ["cables"]

    def process(self, offset: Optional[int] = None) -> StepOutput:
        dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
        start = offset or 0
        end = min(start + self.batch_size, len(dataset))

        while start < len(dataset):
            batch = []
            for i in range(start, end):
                cable_row = dataset[i]
                if "cleaned_content" in cable_row:
                    cable_content = clean_content(cable_row["cleaned_content"])
                    if cable_content:
                        batch.append({"cables": cable_content})

            # Yield batch with last_batch flag
            is_last_batch = end >= len(dataset)
            if batch:
                yield batch, is_last_batch

            start = end
            end = min(start + self.batch_size, len(dataset))

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
        description="A pipeline to summarize and compare diplomatic cables"
    ) as pipeline:
        load_dataset_step = LoadLocalDataset(
            name="load_cablegate_dataset",
            file_path=os.path.join("scripts", "cables", "cleaned_data.parquet"),
            batch_size=32  # Changed from input_batch_size to batch_size
        )

        prepare_content_step = PrepareContentStep(
            name="prepare_content"
        )

        sample_for_comparison_step = RandomSampleForComparison(
            name="sample_for_comparison",
            input_batch_size=32  # Added correct parameter name
        )

        prepare_messages_comparison_step = PrepareMessagesStep(
            name="prepare_messages_comparison"
        )

        ollama_llm = OptimizedTestContainerOllamaLLM(
            model="yi:6b-q4_K_M",
            num_instances=4,
            base_port=11434
        )
        
        # Ensure LLM is loaded properly
        asyncio.run(ollama_llm.load())

        compare_cables_step = ChatGeneration(
            name="compare_cables",
            llm=ollama_llm,
            input_batch_size=32,
            input_mappings={"messages": "messages"},
            output_mappings={"generation": "generation"}
        )

        # Define pipeline flow
        load_dataset_step >> prepare_content_step >> sample_for_comparison_step >> prepare_messages_comparison_step >> compare_cables_step

    return pipeline

def process_dataset(pipeline: Pipeline, parameters: Dict[str, Any]) -> Distiset:
    try:
        run_parameters = {
            "load_cablegate_dataset": {
                "batch_size": 32
            },
            "sample_for_comparison": {
                "input_batch_size": 32
            }
        }
        return pipeline.run(parameters=run_parameters, use_cache=False)
    except Exception as e:
        logging.error(f"Error running the pipeline: {e}")
        raise

def test_pipeline_dry_run():
    """
    Test the pipeline using distilabel's dry_run functionality
    """
    logging.info("Starting pipeline dry run test...")

    try:
        # Create the pipeline
        pipeline = create_pipeline()

        # Execute dry run with sample parameters
        dry_run_params = {
            "load_cablegate_dataset": {
                "file_path": os.path.join("scripts", "cables", "cleaned_data.parquet"),
            },
            "sample_for_comparison": {
                "num_comparisons": 3,  # Small number for testing
                "sample_size": 3,
            }
        }

        # Run the dry run with parameters instead of data
        pipeline.dry_run(parameters=dry_run_params)

        logging.info("Dry run completed successfully")
        return True

    except Exception as e:
        logging.error(f"Pipeline dry run failed: {e}")
        return False

if __name__ == "__main__":
    try:
        # Run the dry run test
        success = test_pipeline_dry_run()
        
        if success:
            pipeline = create_pipeline()
            comparison_distiset = process_dataset(pipeline, {
                "load_cablegate_dataset": {
                    "batch_size": 32
                },
                "sample_for_comparison": {
                    "input_batch_size": 32
                }
            })
            
            # Process results
            compare_cables_output = comparison_distiset.get("compare_cables", {})
            generation_data = compare_cables_output.get("generation", [])

            if isinstance(generation_data, list) and generation_data:
                dataset_dict = {}
                for entry in generation_data:
                    for key, value in entry.items():
                        dataset_dict.setdefault(key, []).append(value)
                
                comparison_dataset = Dataset.from_dict(dataset_dict)
                
                if len(comparison_dataset) > 0:
                    try:
                        comparison_dataset.push_to_hub(
                            "DataTonic/BusinessCaseStudies",
                            private=True,
                            token=os.getenv("HUGGINGFACE_TOKEN")
                        )
                        logging.info("Dataset successfully pushed to the Hub")
                    except Exception as e:
                        logging.error(f"Failed to push dataset to the Hub: {e}")
                else:
                    logging.warning("Comparison dataset is empty")
        else:
            logging.error("Pipeline dry run validation failed")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure proper cleanup
        logging.shutdown()