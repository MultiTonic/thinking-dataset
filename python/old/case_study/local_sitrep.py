import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic import Field

from distilabel.llms import OneAI
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, FormatChatGenerationSFT, GeneratorStep
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput
from distilabel.distiset import Distiset
from distilabel.mixins.runtime_parameters import RuntimeParameter

from datasets import Dataset, load_dataset, DatasetDict

from dotenv import load_dotenv

# Configure logging to use UTF-8 encoding
logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Retrieve OneAI API key from environment variables
oneai_api_key = os.getenv("ONEAI_API_KEY", "e75810fc0c96453eb15c865e00edea24")

# Custom prompt templates
SUMMARY_PROMPT = """{cable_content}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

SITREPPROMPT = """You are an expert in creating fictional case studies based on diplomatic cables. Your task is to generate a detailed, long-form case study that captures the essence of the provided content while transforming it into a completely fictional scenario. Ensure that your case study is creative, engaging, and maintains the tone and style of a diplomatic communication without directly referencing any real people, places, or events from the original content."""

class LoadLocalDataset(GeneratorStep):
    file_path: str = Field(..., description="Path to the local parquet file")
    input_batch_size: int = Field(default=32, description="Number of items to process in each batch")
    
    @property
    def outputs(self) -> List[str]:
        return ["cables"]

    def process(self, offset: Optional[int] = None) -> StepOutput:
        dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
        start = offset or 0
        for i in range(start, len(dataset), self.input_batch_size):
            batch = dataset[i:i+self.input_batch_size]
            yield [{"cables": item["cleaned_content"]} for item in batch]

class PrepareContentStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["cables"]

    @property
    def outputs(self) -> List[str]:
        return ["prepared_content"]

    def process(self, inputs: StepInput) -> StepOutput:
        for batch in inputs:
            prepared_batch = []
            for item in batch:
                prepared_item = {
                    "prepared_content": item["cables"].strip()
                }
                prepared_batch.append(prepared_item)
            yield prepared_batch

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
        for batch in inputs:
            self.cable_sample.extend(random.sample(batch, min(len(batch), self.sample_size - len(self.cable_sample))))
            
            while len(self.cable_sample) >= 3 and len(self.cable_sample) < self.num_comparisons:
                sampled_cables = random.sample(self.cable_sample, 3)
                comparison_prompt = COMPARISON_PROMPT.format(
                    cable_1=sampled_cables[0]["prepared_content"],
                    cable_2=sampled_cables[1]["prepared_content"],
                    cable_3=sampled_cables[2]["prepared_content"]
                )
                yield [{"comparison_prompt": comparison_prompt}]

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
            output_batch = []
            for item in batch:
                messages = [
                    {"role": "system", "content": SITREPPROMPT},
                    {"role": "user", "content": item["prepared_content"]}
                ]
                output_batch.append({"messages": messages})
            yield output_batch

def create_pipeline():
    with Pipeline(
        name="cablegate-analysis-pipeline",
        description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
    ) as pipeline:
        load_dataset = LoadLocalDataset(
            name="load_cablegate_dataset",
            file_path=r"scripts\cables\cleaned_data.parquet"
        )

        prepare_content = PrepareContentStep(
            name="prepare_content",
            input_batch_size=32
        )

        prepare_messages_summary = PrepareMessagesStep(
            name="prepare_messages_summary",
            input_batch_size=32
        )

        summarize_cable = ChatGeneration(
            name="summarize_cable",
            llm=OneAI(api_key=oneai_api_key),
            input_batch_size=32
        )

        format_summary_sft = FormatChatGenerationSFT(
            name="format_summary_sft",
            input_batch_size=32
        )

        sample_for_comparison = RandomSampleForComparison(
            name="sample_for_comparison",
            input_batch_size=32
        )

        prepare_messages_comparison = PrepareMessagesStep(
            name="prepare_messages_comparison",
            input_batch_size=32
        )

        compare_cables = ChatGeneration(
            name="compare_cables",
            llm=OneAI(api_key=oneai_api_key),
            input_batch_size=32
        )

        format_comparison_sft = FormatChatGenerationSFT(
            name="format_comparison_sft",
            input_batch_size=32
        )

        # Define the pipeline flow
        load_dataset >> prepare_content
        prepare_content >> prepare_messages_summary >> summarize_cable >> format_summary_sft
        prepare_content >> sample_for_comparison >> prepare_messages_comparison >> compare_cables >> format_comparison_sft

    return pipeline

def process_dataset(pipeline, parameters):
    return pipeline.run(parameters=parameters)

if __name__ == "__main__":
    huggingface_token = "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"

    pipeline = create_pipeline()
    
    # Process summaries
    summary_distiset = process_dataset(pipeline, {
        "summarize_cable": {
            "llm": {
                "generation_kwargs": {
                    "temperature": 0.9,
                    "max_new_tokens": 4095,
                }
            }
        },
    })
    
    # Process comparisons
    comparison_distiset = process_dataset(pipeline, {
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
    summary_dataset = Dataset.from_dict(summary_distiset.get("format_summary_sft", {}))
    comparison_dataset = Dataset.from_dict(comparison_distiset.get("format_comparison_sft", {}))
    
    # Check if datasets are empty
    if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
        print("Error: Both summary and comparison datasets are empty. No data was generated.")
        sys.exit(1)
    
    # Create SFT dataset
    sft_dataset = Dataset.from_dict({
        "prompt": summary_dataset["prompt"] + comparison_dataset["prompt"],
        "prompt_id": summary_dataset["prompt_id"] + comparison_dataset["prompt_id"],
        "messages": summary_dataset["messages"] + comparison_dataset["messages"]
    })
    
    # Push datasets to Hub
    if len(summary_dataset) > 0:
        summary_dataset.push_to_hub("DataTonic/CaseStudies-en-small", private=True, token=huggingface_token)
    else:
        print("Warning: Summary dataset is empty and will not be pushed to the Hub.")

    if len(comparison_dataset) > 0:
        comparison_dataset.push_to_hub("DataTonic/CaseStudies-en-multi", private=True, token=huggingface_token)
    else:
        print("Warning: Comparison dataset is empty and will not be pushed to the Hub.")

    if len(sft_dataset) > 0:
        sft_dataset.push_to_hub("DataTonic/CaseStudies-en-sft", private=True, token=huggingface_token)
    else:
        print("Warning: SFT dataset is empty and will not be pushed to the Hub.")
    
    # Create and push combined dataset
    combined_dataset = DatasetDict({
        "summaries": summary_dataset,
        "comparisons": comparison_dataset,
        "sft": sft_dataset
    })
    combined_dataset.push_to_hub("DataTonic/CaseStudies-en", private=True, token=huggingface_token)
    
    print("Pipeline execution completed and results pushed to the Hub.")