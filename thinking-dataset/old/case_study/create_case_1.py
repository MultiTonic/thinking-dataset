import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
from pydantic import Field, SecretStr, BaseModel

from distilabel.llms import  OpenAILLM
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, FormatChatGenerationSFT,  LoadDataFromFileSystem,  GeneratorStep, KeepColumns, step
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput,StepResources, _STEP_INPUT_ANNOTATION
from distilabel.distiset import Distiset
from distilabel.mixins.runtime_parameters import RuntimeParameter

from datasets import Dataset, load_dataset, DatasetDict

from dotenv import load_dotenv

from prompts import SITREPPROMPT

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

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
    file_path: RuntimeParameter[str] = Field(
        default=None,
        description="Path to the local parquet file"
    )
    input_batch_size: RuntimeParameter[int] = Field(
        default=32,
        description="Number of items to process in each batch"
    )

    @property
    def inputs(self) -> List[str]:
        return []  # No inputs, this step generates data from file

    @property
    def outputs(self) -> List[str]:
        return ["cables"]  # Outputs the loaded cables
    
    # def process(self) -> StepOutput:
    #     dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
    #     for i in range(0, len(dataset), self.input_batch_size):
    #         batch = dataset[i:i + self.input_batch_size]
    #         output_batch = [{"cables": clean_content(row["cleaned_content"])} for row in batch if "cleaned_content" in row]
    #         yield output_batch

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
                        batch.append({"cables": cable_content}) # batch.append(CableContent(cables=cable_content).model_dump())
                    else:
                        logging.warning(f"Row {i} has empty 'cleaned_content', skipping.")
                else:
                    logging.warning(f"Row {i} missing 'cleaned_content', skipping.")
            
            # if batch:
            #     yield batch, end >= len(dataset)
            # else:
            #     logging.error(f"No valid items found in batch from {start} to {end}")
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
        yield prepared_batch

    # def process(self, inputs: StepInput) -> StepOutput:
    #     prepared_batch = []

        # for item in inputs:
        #     cable_content = item.get("cables", None)
        #     if cable_content:
        #         prepared_batch.append({"prepared_content": cable_content})
        #     else:
        #         logging.warning(f"Invalid or missing 'cables' in item: {item}")

        # if prepared_batch:
        #     yield prepared_batch
        # else:
        #     logging.error("No valid 'prepared_content' found to yield.")
        # for item in inputs:
        #     try:
        #         content = CableContent(**item)
        #         prepared_batch.append(PreparedContent(prepared_content=content.cables).model_dump())
        #     except Exception as e:
        #         logging.warning(f"Skipping invalid item due to error: {e}")

        # if prepared_batch:
        #     yield prepared_batch
        # else:
        #     logging.error("No valid 'prepared_content' found to yield.")

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
        yield output_batch
    # def process(self, inputs: StepInput) -> StepOutput:
    #     output_batch = []

    #     for item in inputs:
    #         prepared_content = item.get("prepared_content", None)
    #         if prepared_content:
    #             messages = [
    #                 {"role": "system", "content": SITREPPROMPT},
    #                 {"role": "user", "content": prepared_content}
    #             ]
    #             output_batch.append({"messages": messages})
    #         else:
    #             logging.warning(f"Invalid 'prepared_content' format in item: {item}")
    # def process(self, inputs: StepInput) -> StepOutput:
    #     for batch in inputs:
    #         output_batch = []

    #         for item in batch:
    #             try:
    #                 content = PreparedContent(**item)
    #                 messages = [
    #                     {"role": "system", "content": SITREPPROMPT},
    #                     {"role": "user", "content": content.prepared_content}
    #                 ]
    #                 output_batch.append(Message(messages=messages).model_dump())
    #             except Exception as e:
    #                 logging.warning(f"Invalid 'prepared_content' format: {item}, error: {e}")

    #         if output_batch:
    #             yield output_batch
    #         else:
    #             logging.error("No valid messages generated to yield.")
        if output_batch:
            yield output_batch
        else:
            logging.error("No valid messages generated to yield.")


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
        while len(cable_sample) >= 3 and len(cable_sample) < self.num_comparisons:
            sampled = random.sample(cable_sample, 3)
            comparison_prompt = COMPARISON_PROMPT.format(
                cable_1=sampled[0]["prepared_content"],
                cable_2=sampled[1]["prepared_content"],
                cable_3=sampled[2]["prepared_content"]
            )
            yield [{"comparison_prompt": comparison_prompt}]

# class RandomSampleForComparison(Step):
#     num_comparisons: RuntimeParameter[int] = Field(default=200000, description="Number of comparisons to generate")
#     sample_size: RuntimeParameter[int] = Field(default=500, description="Size of the sample to draw from")
#     cable_sample: List[Dict[str, Any]] = Field(default_factory=list, description="Sample of cables")

#     @property
#     def inputs(self) -> List[str]:
#         return ["prepared_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["comparison_prompt"]

#     def process(self, inputs: StepInput) -> StepOutput:
#         for batch in inputs:
#             self.cable_sample.extend(random.sample(batch, min(len(batch), self.sample_size - len(self.cable_sample))))
            
#             while len(self.cable_sample) >= 3 and len(self.cable_sample) < self.num_comparisons:
#                 sampled_cables = random.sample(self.cable_sample, 3)
#                 comparison_prompt = COMPARISON_PROMPT.format(
#                     cable_1=sampled_cables[0]["prepared_content"],
#                     cable_2=sampled_cables[1]["prepared_content"],
#                     cable_3=sampled_cables[2]["prepared_content"]
#                 )
#                 yield [ComparisonPrompt(comparison_prompt=comparison_prompt).model_dump()]


#     @property
#     def runtime_parameters_names(self):
#         return {
#             "resources": {
#                 "replicas": True,
#                 "cpus": True,
#                 "gpus": True,
#                 "memory": True,
#                 "resources": True
#             },
#             "input_batch_size": True,
#             "num_comparisons": True,
#             "sample_size": True
#         }

def create_pipeline():
    with Pipeline(
        name="cablegate-analysis-pipeline",
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

        prepare_messages_summary = PrepareMessagesStep(
            name="prepare_messages_summary",
            input_batch_size=32
        )

        summarize_cable = ChatGeneration(
            name="summarize_cable",
            llm=OpenAILLM(api_key="secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb", base_url="https://api.lambdalabs.com/v1", model="/models/LiquidCloud"),
            input_batch_size=32,
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
            llm=OpenAILLM(api_key="""secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb""", base_url="https://api.lambdalabs.com/v1", model="/models/LiquidCloud"),
            input_batch_size=32
        )


        load_dataset >> prepare_content
        prepare_content >> prepare_messages_summary >> summarize_cable #>> format_summary_sft
        prepare_content >> sample_for_comparison >> prepare_messages_comparison >> compare_cables #>> format_comparison_sft

    return pipeline

def process_dataset(pipeline, parameters):
    return pipeline.run(parameters=parameters, use_cache=False)



# def merge_summaries_and_comparisons(summary_dataset, comparison_dataset):
#     merged_data = {"text": []}

#     # Add summaries to the merged dataset
#     for summary_row in summary_dataset:
#         merged_data["text"].append(summary_row.get('train', ''))

#     # Add comparisons to the merged dataset
#     for comparison_row in comparison_dataset:
#         comparison_text = comparison_row.get('comparison_prompt', None)
#         if comparison_text:
#             merged_data["text"].append(comparison_text)
#         else:
#             logging.warning("Missing comparison_prompt in comparison_row")

#     return Dataset.from_dict(merged_data)

if __name__ == "__main__":
    huggingface_token = "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"

    pipeline = create_pipeline()
    
    # Process summaries
    summary_distiset = process_dataset(pipeline, {
        "load_cablegate_dataset": {
            "file_path": os.path.join("scripts", "cables", "cleaned_data.parquet"),
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
    
    # Process comparisons
    comparison_distiset = process_dataset(pipeline, {
        "load_cablegate_dataset": {
            "file_path": os.path.join("scripts", "cables", "cleaned_data.parquet"),
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
            "num_comparisons": 100000,
            "sample_size": 200,
        },
    })
    
    # Create datasets from Distiset objects
    summary_dataset = Dataset.from_dict(summary_distiset.get("summarize_cable", {}))
    comparison_dataset = Dataset.from_dict(comparison_distiset.get("compare_cables", {}))
    
    # # Check if datasets are empty
    # if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
    #     print("Error: Both summary and comparison datasets are empty. No data was generated.")
    #     sys.exit(1)
    
    # # Merge summaries and comparisons into a single dataset with one 'text' column
    # final_dataset = merge_summaries_and_comparisons(summary_dataset, comparison_dataset)

    
    # Push datasets to Hub
    if len(summary_dataset) > 0:
        summary_dataset.push_to_hub("DataTonic/CaseStudies-en-small", private=True, token=huggingface_token)
    else:
        print("Warning: Summary dataset is empty and will not be pushed to the Hub.")

    if len(comparison_dataset) > 0:
        comparison_dataset.push_to_hub("DataTonic/CaseStudies-en-multi", private=True, token=huggingface_token)
    else:
        print("Warning: Comparison dataset is empty and will not be pushed to the Hub.")

    # if len(final_dataset) > 0:
    #     final_dataset.push_to_hub("DataTonic/CaseStudies-en-sft", private=True, token=huggingface_token)
    # else:
    #     print("Warning: Final dataset is empty and will not be pushed to the Hub.")
    
    print("Pipeline execution completed and results pushed to the Hub.")
