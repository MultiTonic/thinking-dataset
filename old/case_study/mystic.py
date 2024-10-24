import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

from pydantic import Field

from distilabel.llms import OneAI
from distilabel.pipeline import Pipeline
from distilabel.steps import LoadDataFromHub, Step, FormatChatGenerationSFT
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput
from distilabel.distiset import Distiset
from distilabel.mixins.runtime_parameters import RuntimeParameter

from datasets import Dataset, load_dataset, DatasetDict

from dotenv import load_dotenv

from globe import SITREPPROMPT
import logging

# Configure logging to use UTF-8 encoding with timestamps and step info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    encoding='utf-8'
)

# Load environment variables from .env file
if not load_dotenv():
    logging.error("Failed to load .env file. Ensure the file exists and is accessible.")

# Retrieve OneAI API key from environment variables
oneai_api_key = os.getenv("ONEAI_API_KEY", "sk-a2b5128e4b284dc682187c919a8dbadb")
if not oneai_api_key:
    logging.error("OneAI API key not found in environment variables. Ensure ONEAI_API_KEY is set.")
    sys.exit(1)

# Custom prompt templates
SUMMARY_PROMPT = """{cable_content}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""


class PrepareContentStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["cleaned_content"]

    @property
    def outputs(self) -> List[str]:
        return ["prepared_content"]

    def process(self, inputs: StepInput) -> StepOutput:
        for batch in inputs:
            logging.info(f"Processing batch with {len(batch)} items in PrepareContentStep.")
            prepared_batch = []
            for item in batch:
                try:
                    prepared_item = {
                        "prepared_content": item["cleaned_content"].strip()
                    }
                    prepared_batch.append(prepared_item)
                except KeyError:
                    logging.error("Key 'cleaned_content' not found in the item.")
                    continue
            yield prepared_batch
            logging.info("Batch processed successfully in PrepareContentStep.")


class RandomSampleForComparison(Step):
    num_comparisons: RuntimeParameter[int] = Field(default=200000, description="Number of comparisons to generate")
    sample_size: RuntimeParameter[int] = Field(default=500, description="Size of the sample to draw from")
    cable_sample: List[Dict[str, Any]] = Field(default_factory=list, description="Sample of cables")

    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["comparison_prompt"]

    def process(self, inputs: StepInput) -> StepOutput:
        total_comparisons_generated = 0
        for batch in inputs:
            batch_size = len(batch)
            logging.info(f"Processing {batch_size} items in RandomSampleForComparison.")

            # Adjust sample size if batch is smaller
            sample_needed = self.sample_size - len(self.cable_sample)
            if sample_needed > 0:
                self.cable_sample.extend(random.sample(batch, min(batch_size, sample_needed)))

            # Generate comparisons while we have enough samples
            while len(self.cable_sample) >= 3 and total_comparisons_generated < self.num_comparisons:
                try:
                    sampled_cables = random.sample(self.cable_sample, 3)
                    comparison_prompt = COMPARISON_PROMPT.format(
                        cable_1=sampled_cables[0]["prepared_content"],
                        cable_2=sampled_cables[1]["prepared_content"],
                        cable_3=sampled_cables[2]["prepared_content"]
                    )
                    yield [{"comparison_prompt": comparison_prompt}]
                    total_comparisons_generated += 1
                except Exception as e:
                    logging.error(f"Error generating comparison prompt: {str(e)}")
                    continue

            logging.info(f"Generated {total_comparisons_generated} comparison prompts so far.")
            # Keep cable_sample within manageable memory limits
            if len(self.cable_sample) > self.sample_size:
                self.cable_sample = self.cable_sample[:self.sample_size]  # Keep the sample manageable

        logging.info("RandomSampleForComparison processing completed.")

    def dump(self, **kwargs):
        dump = super().dump(**kwargs)
        dump['cable_sample'] = []  # Exclude cable_sample from serialization
        return dump

    @property
    def runtime_parameters_names(self):
        return {
            "resources": {
                "replicas": True,
                "cpus": True,
                "gpus": True,
                "memory": True,
                "resources": True
            },
            "input_batch_size": True,
            "num_comparisons": True,
            "sample_size": True
        }


class PrepareMessagesStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["messages"]

    def process(self, inputs: StepInput) -> StepOutput:
        for batch in inputs:
            logging.info(f"Preparing messages for a batch of {len(batch)} items.")
            output_batch = []
            for item in batch:
                try:
                    messages = [
                        {"role": "system", "content": SITREPPROMPT},
                        {"role": "user", "content": item["prepared_content"]}
                    ]
                    output_batch.append({"messages": messages})
                except KeyError:
                    logging.error("Key 'prepared_content' not found in the item.")
                    continue
            yield output_batch
            logging.info("Messages prepared successfully.")


def create_pipeline():
    try:
        logging.info("Initializing the cablegate-analysis pipeline.")
        with Pipeline(
            name="cablegate-analysis-pipeline",
            description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
        ) as pipeline:

            # Each step creation should be logged
            logging.info("Loading dataset.")
            load_dataset = LoadDataFromHub(
                name="load_cablegate_dataset",
                repo_id="DataTonic/cablegate-pdf-dataset",
                split="cables",
                batch_size=32,
                streaming=True,
                output_mappings={"cables": "cleaned_content"}
            )

            logging.info("Preparing content.")
            prepare_content = PrepareContentStep(name="prepare_content", input_batch_size=32)

            logging.info("Setting up message preparation for summary.")
            prepare_messages_summary = PrepareMessagesStep(name="prepare_messages_summary", input_batch_size=32)

            logging.info("Summarizing cables.")
            summarize_cable = ChatGeneration(name="summarize_cable", llm=OneAI(api_key=oneai_api_key), input_batch_size=32)

            format_summary_sft = FormatChatGenerationSFT(name="format_summary_sft", input_batch_size=32)

            logging.info("Sampling for comparison.")
            sample_for_comparison = RandomSampleForComparison(name="sample_for_comparison", input_batch_size=32)

            prepare_messages_comparison = PrepareMessagesStep(name="prepare_messages_comparison", input_batch_size=32)

            compare_cables = ChatGeneration(name="compare_cables", llm=OneAI(api_key=oneai_api_key), input_batch_size=32)

            format_comparison_sft = FormatChatGenerationSFT(name="format_comparison_sft", input_batch_size=32)

            # Define the pipeline flow
            load_dataset >> prepare_content
            prepare_content >> prepare_messages_summary >> summarize_cable >> format_summary_sft
            prepare_content >> sample_for_comparison >> prepare_messages_comparison >> compare_cables >> format_comparison_sft

        logging.info("Pipeline created successfully.")
        return pipeline
    except Exception as e:
        logging.error(f"Pipeline creation failed: {str(e)}")
        sys.exit(1)


def process_dataset(pipeline, parameters):
    try:
        logging.info("Running the pipeline with given parameters.")
        return pipeline.run(parameters=parameters)
    except Exception as e:
        logging.error(f"Pipeline run failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    huggingface_token = "hf_..."

    pipeline = create_pipeline()

    try:
        logging.info("Processing summaries.")
        summary_distiset = process_dataset(pipeline, {
            "load_cablegate_dataset": {
                "repo_id": "DataTonic/cablegate-pdf-dataset",
                "split": "cables",
            },
            "summarize_cable": {
                "llm": {
                    "generation_kwargs": {
                        "temperature": 0.9,
                        "max_new_tokens": 4095,
                    }
                }
            },
        })

        logging.info("Processing comparisons.")
        comparison_distiset = process_dataset(pipeline, {
            "load_cablegate_dataset": {
                "repo_id": "DataTonic/cablegate-pdf-dataset",
                "split": "cables",
            },
            "compare_cables": {
                "llm": {
                    "generation_kwargs": {
                        "temperature": 0.9,
                        "max_new_tokens": 4095,
                    }
                },
            },
            "sample_for_comparison": {
                "num_comparisons": 200000,
                "sample_size": 500,
            },
        })

        # Create datasets from Distiset objects
        summary_data = summary_distiset.get("format_summary_sft", {})
        comparison_data = comparison_distiset.get("format_comparison_sft", {})

        # Ensure the data dictionaries are not empty
        if not summary_data:
            logging.error("Summary data is empty.")
            summary_dataset = Dataset.from_dict({})
        else:
            summary_dataset = Dataset.from_dict(summary_data)

        if not comparison_data:
            logging.error("Comparison data is empty.")
            comparison_dataset = Dataset.from_dict({})
        else:
            comparison_dataset = Dataset.from_dict(comparison_data)

        # Check if datasets are empty
        if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
            logging.error("Error: Both summary and comparison datasets are empty. No data was generated.")
            sys.exit(1)

        # Create SFT dataset
        logging.info("Creating SFT dataset.")
        if len(summary_dataset) > 0 and len(comparison_dataset) > 0:
            sft_dataset = Dataset.from_dict({
                "prompt": summary_dataset["prompt"] + comparison_dataset["prompt"],
                "prompt_id": summary_dataset["prompt_id"] + comparison_dataset["prompt_id"],
                "messages": summary_dataset["messages"] + comparison_dataset["messages"]
            })
        elif len(summary_dataset) > 0:
            sft_dataset = Dataset.from_dict({
                "prompt": summary_dataset["prompt"],
                "prompt_id": summary_dataset["prompt_id"],
                "messages": summary_dataset["messages"]
            })
        elif len(comparison_dataset) > 0:
            sft_dataset = Dataset.from_dict({
                "prompt": comparison_dataset["prompt"],
                "prompt_id": comparison_dataset["prompt_id"],
                "messages": comparison_dataset["messages"]
            })
        else:
            sft_dataset = Dataset.from_dict({})
            logging.warning("SFT dataset is empty.")

        # Push datasets to Hub
        if len(summary_dataset) > 0:
            logging.info("Pushing summary dataset to Hub.")
            summary_dataset.push_to_hub("DataTonic/CaseStudies-en-small", private=True, token=huggingface_token)
        else:
            logging.warning("Summary dataset is empty and will not be pushed to the Hub.")

        if len(comparison_dataset) > 0:
            logging.info("Pushing comparison dataset to Hub.")
            comparison_dataset.push_to_hub("DataTonic/CaseStudies-en-multi", private=True, token=huggingface_token)
        else:
            logging.warning("Comparison dataset is empty and will not be pushed to the Hub.")

        if len(sft_dataset) > 0:
            logging.info("Pushing SFT dataset to Hub.")
            sft_dataset.push_to_hub("DataTonic/CaseStudies-en-sft", private=True, token=huggingface_token)
        else:
            logging.warning("SFT dataset is empty and will not be pushed to the Hub.")

        # Create and push combined dataset
        logging.info("Creating and pushing combined dataset.")
        combined_dataset = DatasetDict({
            "summaries": summary_dataset,
            "comparisons": comparison_dataset,
            "sft": sft_dataset
        })
        combined_dataset.push_to_hub("DataTonic/CaseStudies-en", private=True, token=huggingface_token)

        logging.info("Pipeline execution completed and results pushed to the Hub.")
    except Exception as e:
        logging.error(f"Error during dataset processing or pushing: {str(e)}")
        sys.exit(1)
