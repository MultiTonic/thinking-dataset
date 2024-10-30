import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
from pydantic import Field, SecretStr, BaseModel

from distilabel.llms import OpenAILLM, AzureOpenAILLM
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, GeneratorStep, step
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput, StepResources
from distilabel.distiset import Distiset
from distilabel.mixins.runtime_parameters import RuntimeParameter

from datasets import Dataset, load_dataset

from dotenv import load_dotenv

from prompts import SITREPPROMPT

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)], encoding='utf-8')

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

Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""

def clean_content(text: str) -> str:
    import re
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'[^ -~]', '', text)  # Remove non-ASCII characters
    return text.strip()

class LoadLocalDataset(GeneratorStep):
    file_path: str = Field(default= "", description="Path to the local parquet file")
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
                yield batch, end >= len(dataset)
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

class PrepareMessagesStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["messages"]
    
    def process(self, inputs: StepInput) -> StepOutput:
        output_batch = []
        for item in inputs:
            if "prepared_content" in item:
                messages = [
                    {"role": "system", "content": SITREPPROMPT},
                    {"role": "user", "content": item["prepared_content"]}
                ]
                output_batch.append({"messages": messages})
        
        if output_batch:
            yield output_batch

class RandomSampleForComparison(Step):
    num_comparisons: int = Field(default=200000, description="Number of comparisons to generate")
    sample_size: int = Field(default=500, description="Size of the sample to draw from")

    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["comparison_prompt"]

    def process(self, inputs: StepInput) -> StepOutput:
        cable_sample = [item for item in inputs if "prepared_content" in item]
        if len(cable_sample) >= 3:
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
        load_dataset = LoadLocalDataset(
            name="load_cablegate_dataset",
            file_path=os.path.join("scripts", "cables", "cleaned_data.parquet"),
            input_batch_size=32
        )

        prepare_content = PrepareContentStep(
            name="prepare_content",
            input_batch_size=32
        )

        sample_for_comparison = RandomSampleForComparison(
            name="sample_for_comparison",
            input_batch_size=32
        )

        prepare_messages_comparison = PrepareMessagesStep(
            name="prepare_messages_comparison",
            input_batch_size=32,
        )

        compare_cables = ChatGeneration(
            name="compare_cables",
            llm=AzureOpenAILLM(api_version="2024-02-15-preview", model="gptonic", api_key="f1f1c0ed4b8344be8de28d93c1a41a51", base_url="https://eastus2.api.cognitive.microsoft.com/"),
            input_batch_size=32,
            input_mappings={"messages": "messages"}, 
            output_mappings={"generation": "generation"},  
        )

        load_dataset >> prepare_content >> sample_for_comparison >> prepare_messages_comparison >> compare_cables

    return pipeline

def process_dataset(pipeline, parameters):
    return pipeline.run(parameters=parameters, use_cache=False)

if __name__ == "__main__":
    huggingface_token = "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"

    pipeline = create_pipeline()

    # Process comparisons
    comparison_distiset = process_dataset(pipeline, {
        "load_cablegate_dataset": {
            "input_batch_size": 32,
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
            "input_batch_size": 32,
        },
    })
    
    comparison_dataset = Dataset.from_dict(comparison_distiset.get("compare_cables", {}))
    
    if len(comparison_dataset) > 0:
        comparison_dataset.push_to_hub("DataTonic/BusinessCaseStudies", private=True, token=huggingface_token)
    else:
        print("Warning: Comparison dataset is empty and will not be pushed to the Hub.")

    print("Pipeline execution completed and results pushed to the Hub.")