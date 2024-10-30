import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic import Field, SecretStr

from distilabel.llms import TogetherLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, FormatChatGenerationSFT,  LoadDataFromFileSystem,  GeneratorStep
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput,StepResources
from distilabel.distiset import Distiset
from distilabel.mixins.runtime_parameters import RuntimeParameter

from datasets import Dataset, load_dataset, DatasetDict

from dotenv import load_dotenv

from prompts import SITREPPROMPT

# Configure logging to use UTF-8 encoding
logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding='utf-8')

# Load environment variables from .env file
# load_dotenv()

# # Retrieve OneAI API key from environment variables
# oneai_api_key = os.getenv("ONEAI_API_KEY", "e75810fc0c96453eb15c865e00edea24")

# Custom prompt templates
SUMMARY_PROMPT = """{cable_content}

Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""


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

    def process(self, offset: Optional[int] = None) -> StepOutput:
        dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
        start = offset or 0
        end = min(start + self.input_batch_size, len(dataset))

        while start < len(dataset):
            batch = []
            for i in range(start, end):
                cable_row = dataset[i]
                cable_content = cable_row["cleaned_content"] 
                batch.append({"cables": cable_content})

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
        for batch in inputs:
            prepared_batch = []
            logging.info(f"Processing batch: {batch}")
            for item in batch:
                if isinstance(item, dict) and "prepared_content" in item:
                    prepared_item = {"role": "user", "content": item["prepared_content"]}
                    logging.info(f"Generated messages: {prepared_item}")
                else:
                    logging.warning(f"Invalid item format: {item}")
                    continue  # Skip invalid items
                
            

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
            logging.info(f"Processing batch: {batch}")
            logging.info(f"Generated messages: {messages}")

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
            llm=TogetherLLM(api_key="secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb", base_url="https://api.lambdalabs.com/v1", ),
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
            input_batch_size=32,
            
        )

        compare_cables = ChatGeneration(
            name="compare_cables",
            llm=TogetherLLM(api_key="secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb", base_url="https://api.lambdalabs.com/v1"),
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

# def create_pipeline():
#     with Pipeline(
#         name="cablegate-analysis-pipeline",
#         description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
#     ) as pipeline:
#         load_dataset = LoadLocalDataset(
#             name='load_cablegate_dataset',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             batch_size=50,
#             file_path='scripts\\cables\\cleaned_data.parquet',
#             input_batch_size=32
#         )

#         # Prepare content step
#         prepare_content = PrepareContentStep(
#             name='prepare_content',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32
#         )

#         # Prepare messages for comparison
#         prepare_messages_comparison = PrepareMessagesStep(
#             name='prepare_messages_comparison',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32
#         )

#         # Prepare messages for summary
#         prepare_messages_summary = PrepareMessagesStep(
#             name='prepare_messages_summary',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32
#         )

#         # Random sample for comparison
#         sample_for_comparison = RandomSampleForComparison(
#             name='sample_for_comparison',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32,
#             num_comparisons=200000,
#             sample_size=500,
#             cable_sample=[]
#         )

#         # Chat generation step for comparison
#         compare_cables = ChatGeneration(
#             name='compare_cables',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32,
#             llm=OpenAILLM(
#                 generation_kwargs={},
#                 model='LiquidCloud',
#                 base_url='https://api.lambdalabs.com/v1',
#                 api_key='secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb',
#                 max_retries=6,
#                 timeout=120,
#                 structured_output=None
#             ),
#             group_generations=False,
#             add_raw_output=True,
#             num_generations=1
#         )

#         # Chat generation step for summarizing cables
#         summarize_cable = ChatGeneration(
#             name='summarize_cable',
#             resources=StepResources(
#                 replicas=1,
#                 cpus=None,
#                 gpus=None,
#                 memory=None,
#                 resources=None
#             ),
#             input_mappings={},
#             output_mappings={},
#             input_batch_size=32,
#             llm=OpenAILLM(
#                 generation_kwargs={},
#                 model='LiquidCloud',
#                 base_url='https://api.lingyiwanwu.com/v1',
#                 api_key='secret_dark-thoughts-casestudy_6fbfb20de4e640be87d6df2068a9927b.cF1MivYQbPelGCDcarKMIs5EudCFC8jb',
#                 max_retries=6,
#                 timeout=120,
#                 structured_output=None
#             ),
#             group_generations=False,
#             add_raw_output=True,
#             num_generations=1
#         )

#     # Define the pipeline flow with input and output mappings
#     # Connect load_dataset outputs
#     load_outputs = load_dataset.outputs
#     if isinstance(load_outputs, list):
#         for output in load_outputs:
#             prepare_content.inputs.append(output)  # Use append to handle list outputs
#     else:
#         prepare_content.inputs.append(load_outputs)  # Handle single output

#     # Connect outputs to their respective next steps
#     prepare_content.outputs[0] >> prepare_messages_summary.inputs  # Assuming it returns a single output
#     prepare_messages_summary.outputs[0] >> summarize_cable.inputs  # Assuming it returns a single output
#     sample_for_comparison.outputs[0] >> compare_cables.inputs  # Assuming it returns a single output

#     # Return the constructed pipeline
#     return Pipeline(steps=[
#         load_dataset,
#         prepare_content,
#         prepare_messages_comparison,
#         prepare_messages_summary,
#         sample_for_comparison,
#         compare_cables,
#         summarize_cable
#     ])

def process_dataset(pipeline, parameters):
    return pipeline.run(parameters=parameters, use_cache=True)

# def merge_summaries_and_comparisons(summary_dataset, comparison_dataset):
#     merged_data = {"text": []}

#     # Add summaries to the merged dataset
#     for summary_row in summary_dataset:
#         # Add the generation column from summaries as text
#         merged_data["text"].append(summary_row['messages'])

#     # Add comparisons to the merged dataset
#     for comparison_row in comparison_dataset:
#         # Add the comparison_prompt column from comparisons as text
#         merged_data["text"].append(comparison_row['comparison_prompt'])

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
            "sample_size": 500,
        },
    })
    
    # Create datasets from Distiset objects
    summary_dataset = Dataset.from_dict(summary_distiset.get("summarize_cable", {}))
    comparison_dataset = Dataset.from_dict(comparison_distiset.get("compare_cables", {}))
    
    # Check if datasets are empty
    if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
        print("Error: Both summary and comparison datasets are empty. No data was generated.")
        sys.exit(1)
    
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

# import os
# import random
# import sys
# import logging
# from pathlib import Path
# from typing import List, Dict, Any

# from pydantic import Field

# from distilabel.llms import OneAI
# from distilabel.pipeline import Pipeline
# from distilabel.steps import LoadDataFromHub, Step, FormatChatGenerationSFT
# from distilabel.steps.tasks import ChatGeneration
# from distilabel.steps.typing import StepOutput
# from distilabel.steps.base import StepInput
# from distilabel.distiset import Distiset
# from distilabel.mixins.runtime_parameters import RuntimeParameter

# from datasets import Dataset, load_dataset, DatasetDict

# from dotenv import load_dotenv

# from globe import SITREPPROMPT

# # Configure logging to use UTF-8 encoding
# logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding='utf-8')

# # Load environment variables from .env file
# load_dotenv()

# # Retrieve OneAI API key from environment variables
# oneai_api_key = os.getenv("ONEAI_API_KEY", "e75810fc0c96453eb15c865e00edea24")

# # Custom prompt templates
# SUMMARY_PROMPT = """{cable_content}

# Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""

# COMPARISON_PROMPT = """{cable_1}

# {cable_2}

# {cable_3}

# Use the inspiration above to create a fictional case study using free text , detailed, long descriptive form:"""


# class PrepareContentStep(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["cleaned_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["prepared_content"]

#     def process(self, inputs: StepInput) -> StepOutput:
#         for batch in inputs:
#             prepared_batch = []
#             for item in batch:
#                 prepared_item = {
#                     "prepared_content": item["cleaned_content"].strip()
#                 }
#                 prepared_batch.append(prepared_item)
#             yield prepared_batch


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
#                 yield [{"comparison_prompt": comparison_prompt}]

#     def dump(self, **kwargs):
#         dump = super().dump(**kwargs)
#         dump['cable_sample'] = []  # Exclude cable_sample from serialization
#         return dump

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


# class PrepareMessagesStep(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["prepared_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["messages"]

#     def process(self, inputs: StepInput) -> StepOutput:
#         for batch in inputs:
#             output_batch = []
#             for item in batch:
#                 messages = [
#                     {"role": "system", "content": SITREPPROMPT},
#                     {"role": "user", "content": item["prepared_content"]}
#                 ]
#                 output_batch.append({"messages": messages})
#             yield output_batch


# def create_pipeline():
#     with Pipeline(
#         name="cablegate-analysis-pipeline",
#         description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
#     ) as pipeline:
#         load_dataset = LoadDataFromHub(
#             name="load_cablegate_dataset",
#             repo_id="DataTonic/cablegate-pdf-dataset",
#             split="cables",
#             batch_size=32,
#             streaming=True,
#             output_mappings={"cables": "cleaned_content"}  # Map 'cleaned_content' to 'cables'
#         )

#         prepare_content = PrepareContentStep(
#             name="prepare_content",
#             input_batch_size=32
#         )

#         prepare_messages_summary = PrepareMessagesStep(
#             name="prepare_messages_summary",
#             input_batch_size=32
#         )

#         summarize_cable = ChatGeneration(
#             name="summarize_cable",
#             llm=OneAI(api_key=oneai_api_key),
#             input_batch_size=32
#         )

#         format_summary_sft = FormatChatGenerationSFT(
#             name="format_summary_sft",
#             input_batch_size=32
#         )

#         sample_for_comparison = RandomSampleForComparison(
#             name="sample_for_comparison",
#             input_batch_size=32
#         )

#         prepare_messages_comparison = PrepareMessagesStep(
#             name="prepare_messages_comparison",
#             input_batch_size=32
#         )

#         compare_cables = ChatGeneration(
#             name="compare_cables",
#             llm=OneAI(api_key=oneai_api_key),
#             input_batch_size=32
#         )

#         format_comparison_sft = FormatChatGenerationSFT(
#             name="format_comparison_sft",
#             input_batch_size=32
#         )

#         # Define the pipeline flow
#         load_dataset >> prepare_content
#         prepare_content >> prepare_messages_summary >> summarize_cable >> format_summary_sft
#         prepare_content >> sample_for_comparison >> prepare_messages_comparison >> compare_cables >> format_comparison_sft

#     return pipeline


# def process_dataset(pipeline, parameters):
#     return pipeline.run(parameters=parameters)


# if __name__ == "__main__":
#     huggingface_token = "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"

#     pipeline = create_pipeline()
    
#     # Process summaries
#     summary_distiset = process_dataset(pipeline, {
#         "load_cablegate_dataset": {
#             "repo_id": "DataTonic/cablegate-pdf-dataset",
#             "split": "cables",
#         },
#         "summarize_cable": {
#             "llm": {
#                 "generation_kwargs": {
#                     "temperature": 0.9,
#                     "max_new_tokens": 4095,
#                 }
#             }
#         },
#     })
    
#     # Process comparisons
#     comparison_distiset = process_dataset(pipeline, {
#         "load_cablegate_dataset": {
#             "repo_id": "DataTonic/cablegate-pdf-dataset",
#             "split": "cables",
#         },
#         "compare_cables": {
#             "llm": {
#                 "generation_kwargs": {
#                     "temperature": 0.9,
#                     "max_new_tokens": 4095,
#                 }
#             },
#         },
#         "sample_for_comparison": {
#             "num_comparisons": 200000,
#             "sample_size": 500,
#         },
#     })
    
#     # Create datasets from Distiset objects
#     summary_dataset = Dataset.from_dict(summary_distiset.get("format_summary_sft", {}))
#     comparison_dataset = Dataset.from_dict(comparison_distiset.get("format_comparison_sft", {}))
    
#     # Check if datasets are empty
#     if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
#         print("Error: Both summary and comparison datasets are empty. No data was generated.")
#         sys.exit(1)
    
#     # Create SFT dataset
#     sft_dataset = Dataset.from_dict({
#         "prompt": summary_dataset["prompt"] + comparison_dataset["prompt"],
#         "prompt_id": summary_dataset["prompt_id"] + comparison_dataset["prompt_id"],
#         "messages": summary_dataset["messages"] + comparison_dataset["messages"]
#     })
    
#     # Push datasets to Hub
#     if len(summary_dataset) > 0:
#         summary_dataset.push_to_hub("DataTonic/CaseStudies-en-small", private=True, token=huggingface_token)
#     else:
#         print("Warning: Summary dataset is empty and will not be pushed to the Hub.")

#     if len(comparison_dataset) > 0:
#         comparison_dataset.push_to_hub("DataTonic/CaseStudies-en-multi", private=True, token=huggingface_token)
#     else:
#         print("Warning: Comparison dataset is empty and will not be pushed to the Hub.")

#     if len(sft_dataset) > 0:
#         sft_dataset.push_to_hub("DataTonic/CaseStudies-en-sft", private=True, token=huggingface_token)
#     else:
#         print("Warning: SFT dataset is empty and will not be pushed to the Hub.")
    
#     # Create and push combined dataset
#     combined_dataset = DatasetDict({
#         "summaries": summary_dataset,
#         "comparisons": comparison_dataset,
#         "sft": sft_dataset
#     })
#     combined_dataset.push_to_hub("DataTonic/CaseStudies-en", private=True, token=huggingface_token)
    
#     print("Pipeline execution completed and results pushed to the Hub.")

# if __name__ == "__main__":
#     # Dry run for the summarization pipeline
#     summary_dry_run = pipeline.dry_run(
#         parameters={
#             "load_cablegate_dataset": {
#                 "batch_size": 1,
#             },
#             "summarize_cable": {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 150,
#                     }
#                 },
#             },
#         },
#     )
#     print("Summarization pipeline dry run completed successfully.")
    
#     # Dry run for the comparison pipeline
#     comparison_dry_run = pipeline.dry_run(
#         parameters={
#             "load_cablegate_dataset": {
#                 "batch_size": 1,
#             },
#             "compare_cables": {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 300,
#                     }
#                 },
#             },
#         },
#     )
#     print("Comparison pipeline dry run completed successfully.")

#     print("Dry runs completed. Pipeline structure is valid.")

    # Uncomment the following lines to run the full pipeline
    # distiset = pipeline.run(
    #     parameters={
    #         "load_cablegate_dataset": {
    #             "batch_size": 10,  # Adjust batch size for full run
    #         },
    #         "summarize_cable": {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 150,
    #                 }
    #             },
    #         },
    #         "compare_cables": {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 300,
    #                 }
    #             },
    #         },
    #     },
    # )
    # distiset.push_to_hub("your-huggingface-username/cablegate-analysis-dataset")

# import os
# import random
# from typing import List, Dict
# from distilabel.llms import OneAI
# from distilabel.pipeline import Pipeline
# from distilabel.steps import LoadDataFromHub, Step, FormatChatGenerationSFT
# from distilabel.steps.tasks import ChatGeneration
# from distilabel.steps.typing import StepOutput
# from datasets import Dataset, DatasetDict

# # Ensure you have set your OneAI API key in the environment variables
# # os.environ["01AI_API_KEY"] = "your-oneai-api-key-here"

# # Custom prompt templates
# SUMMARY_PROMPT = """
# Analyze the following diplomatic cable content and provide a concise summary:

# {pdf_content}

# Summary:
# """

# COMPARISON_PROMPT = """
# Compare and contrast the following three diplomatic cables:

# Cable 1:
# {cable_1}

# Cable 2:
# {cable_2}

# Cable 3:
# {cable_3}

# Provide a comprehensive analysis highlighting similarities, differences, and potential implications:
# """

# class CleanTextStep(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["pdf_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["cleaned_content"]

#     def process(self, inputs) -> StepOutput:
#         for batch in inputs:
#             cleaned_batch = []
#             for item in batch:
#                 cleaned_item = {
#                     "cleaned_content": item["pdf_content"].replace("\n", " ").replace("\r", " ")
#                 }
#                 cleaned_batch.append(cleaned_item)
#             yield cleaned_batch

# class RandomSampleForComparison(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["cleaned_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["comparison_prompt"]

#     def process(self, inputs) -> StepOutput:
#         all_cables = [item for batch in inputs for item in batch]
#         for _ in range(200000):  # Generate 200000 comparisons
#             if len(all_cables) >= 3:
#                 sampled_cables = random.sample(all_cables, 3)
#                 comparison_prompt = COMPARISON_PROMPT.format(
#                     cable_1=sampled_cables[0]["cleaned_content"],
#                     cable_2=sampled_cables[1]["cleaned_content"],
#                     cable_3=sampled_cables[2]["cleaned_content"]
#                 )
#                 yield [{"comparison_prompt": comparison_prompt}]
#             else:
#                 break  # Stop if not enough cables

# class PrepareMessagesStep(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["cleaned_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["messages"]

#     def process(self, inputs) -> StepOutput:
#         for batch in inputs:
#             output_batch = []
#             for item in batch:
#                 messages = [
#                     {"role": "system", "content": "You are an expert in analyzing diplomatic communications. Provide clear and concise summaries of the given content."},
#                     {"role": "user", "content": item["cleaned_content"]}
#                 ]
#                 output_batch.append({"messages": messages})
#             yield output_batch

# with Pipeline(
#     name="cablegate-analysis-pipeline",
#     description="A pipeline to summarize and compare diplomatic cables from the Cablegate dataset"
# ) as pipeline:
#     load_dataset = LoadDataFromHub(
#         name="load_cablegate_dataset",
#         output_mappings={"cleaned_content": "cable_content"},  # Change this line
#         repo_id="DataTonic/cablegate-pdf-dataset",  # Set the repo_id here
#         split="cables",
#         batch_size=1
#     )

#     clean_text = CleanTextStep(
#         name="clean_text",
#         input_mappings={"cable_content": "pdf_content"} 
#     )

#     prepare_messages_summary = PrepareMessagesStep(
#         name="prepare_messages_summary"
#     )

#     summarize_cable = ChatGeneration(
#         name="summarize_cable",
#         llm=OneAI()
#     )

#     format_summary_sft = FormatChatGenerationSFT(
#         name="format_summary_sft"
#     )

#     sample_for_comparison = RandomSampleForComparison(
#         name="sample_for_comparison"
#     )

#     prepare_messages_comparison = PrepareMessagesStep(
#         name="prepare_messages_comparison"
#     )

#     compare_cables = ChatGeneration(
#         name="compare_cables",
#         llm=OneAI()
#     )

#     format_comparison_sft = FormatChatGenerationSFT(
#         name="format_comparison_sft"
#     )

#     # Define the pipeline flow
#     load_dataset >> clean_text
#     clean_text >> prepare_messages_summary >> summarize_cable >> format_summary_sft
#     clean_text >> sample_for_comparison >> prepare_messages_comparison >> compare_cables >> format_comparison_sft

# if __name__ == "__main__":
#     # Dry run for the summarization pipeline
#     summary_dry_run = pipeline.dry_run(
#         parameters={
#             "load_cablegate_dataset": {
#                 "batch_size": 1,
#             },
#             "summarize_cable": {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 150,
#                     }
#                 },
#             },
#         },
#     )
#     print("Summarization pipeline dry run completed successfully.")
    
#     # Dry run for the comparison pipeline
#     comparison_dry_run = pipeline.dry_run(
#         parameters={
#             "load_cablegate_dataset": {
#                 "batch_size": 1,
#             },
#             "compare_cables": {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 300,
#                     }
#                 },
#             },
#         },
#     )
#     print("Comparison pipeline dry run completed successfully.")

#     print("Dry runs completed. Pipeline structure is valid.")

    # Uncomment the following lines to run the full pipeline
    # distiset = pipeline.run(
    #     parameters={
    #         "load_cablegate_dataset": {
    #             "repo_id": "DataTonic/cablegate-pdf-dataset",
    #             "split": "train",
    #         },
    #         "summarize_cable": {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 150,
    #                 }
    #             },
    #         },
    #         "compare_cables": {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 300,
    #                 }
    #             },
    #         },
    #     },
    # )
    # distiset.push_to_hub("your-huggingface-username/cablegate-analysis-dataset")


    # # Run the full pipeline
    # distiset = pipeline.run(
    #     parameters={
    #         load_dataset.name: {
    #             "repo_id": "DataTonic/cablegate-pdf-dataset",
    #             "split": "train",
    #         },
    #         summarize_cable.name: {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 150,
    #                 }
    #             },
    #         },
    #         compare_cables.name: {
    #             "llm": {
    #                 "generation_kwargs": {
    #                     "temperature": 0.7,
    #                     "max_new_tokens": 300,
    #                 }
    #             },
    #         },
    #     }
    # )

    # # Push the generated dataset to the Hugging Face Hub
    # distiset.push_to_hub("your-username/cablegate-analysis-dataset")
    
#     # Dry run for the comparison pipeline
#     comparison_dry_run = pipeline.dry_run(
#         parameters={
#             load_dataset.name: {
#                 "repo_id": "DataTonic/cablegate-pdf-dataset",
#                 "split": "train",
#             },
#             compare_cables.name: {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 300,
#                     }
#                 },
#             },
#         },
#         batch_size=1
#     )
#     print("Comparison pipeline dry run completed successfully.")

#     """
#     # Run the summarization pipeline
#     summary_distiset = pipeline.run(
#         parameters={
#             load_dataset.name: {
#                 "repo_id": "DataTonic/cablegate-pdf-dataset",
#                 "split": "train",
#             },
#             summarize_cable.name: {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 150,
#                     }
#                 },
#                 "prompt_template": SUMMARY_PROMPT,
#             },
#         },
#     )
    
#     # Run the comparison pipeline
#     comparison_distiset = pipeline.run(
#         parameters={
#             load_dataset.name: {
#                 "repo_id": "DataTonic/cablegate-pdf-dataset",
#                 "split": "train",
#             },
#             compare_cables.name: {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 300,
#                     }
#                 },
#             },
#         },
#     )
    
#     # Create datasets
#     summary_dataset = Dataset.from_dict({
#         "summary": summary_distiset.to_pandas()["generation"].tolist(),
#         "prompt": summary_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": summary_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": summary_distiset.to_pandas()["messages"].tolist()
#     })
    
#     comparison_dataset = Dataset.from_dict({
#         "comparison": comparison_distiset.to_pandas()["generation"].tolist(),
#         "prompt": comparison_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": comparison_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": comparison_distiset.to_pandas()["messages"].tolist()
#     })
    
#     sft_dataset = Dataset.from_dict({
#         "prompt": summary_distiset.to_pandas()["prompt"].tolist() + comparison_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": summary_distiset.to_pandas()["prompt_id"].tolist() + comparison_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": summary_distiset.to_pandas()["messages"].tolist() + comparison_distiset.to_pandas()["messages"].tolist()
#     })
    
#     # Combine datasets into a single dataset with three splits
#     combined_dataset = DatasetDict({
#         "summaries": summary_dataset,
#         "comparisons": comparison_dataset,
#         "sft": sft_dataset
#     })
    
#     # Push the results to the Hugging Face Hub
#     combined_dataset.push_to_hub("your-username/cablegate-analysis")
#     print("Pipeline execution completed and results pushed to the Hub.")
#     """

#     print("Dry runs completed. Pipeline structure is valid.")

# if __name__ == "__main__":
#     # Run the summarization pipeline
#     summary_distiset = pipeline.run(
#         parameters={
#             load_dataset.name: {
#                 "repo_id": "DataTonic/cablegate-pdf-dataset",
#                 "split": "train",
#             },
#             summarize_cable.name: {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 150,
#                     }
#                 },
#                 "prompt_template": SUMMARY_PROMPT,
#             },
#         },
#     )
    
#     # Run the comparison pipeline
#     comparison_distiset = pipeline.run(
#         parameters={
#             load_dataset.name: {
#                 "repo_id": "DataTonic/cablegate-pdf-dataset",
#                 "split": "train",
#             },
#             compare_cables.name: {
#                 "llm": {
#                     "generation_kwargs": {
#                         "temperature": 0.7,
#                         "max_new_tokens": 300,
#                     }
#                 },
#             },
#         },
#     )
    
#     # Create datasets
#     summary_dataset = Dataset.from_dict({
#         "summary": summary_distiset.to_pandas()["generation"].tolist(),
#         "prompt": summary_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": summary_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": summary_distiset.to_pandas()["messages"].tolist()
#     })
    
#     comparison_dataset = Dataset.from_dict({
#         "comparison": comparison_distiset.to_pandas()["generation"].tolist(),
#         "prompt": comparison_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": comparison_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": comparison_distiset.to_pandas()["messages"].tolist()
#     })
    
#     sft_dataset = Dataset.from_dict({
#         "prompt": summary_distiset.to_pandas()["prompt"].tolist() + comparison_distiset.to_pandas()["prompt"].tolist(),
#         "prompt_id": summary_distiset.to_pandas()["prompt_id"].tolist() + comparison_distiset.to_pandas()["prompt_id"].tolist(),
#         "messages": summary_distiset.to_pandas()["messages"].tolist() + comparison_distiset.to_pandas()["messages"].tolist()
#     })
    
#     # Combine datasets into a single dataset with three splits
#     combined_dataset = DatasetDict({
#         "summaries": summary_dataset,
#         "comparisons": comparison_dataset,
#         "sft": sft_dataset
#     })
    
#     # Push the results to the Hugging Face Hub
#     combined_dataset.push_to_hub("your-username/cablegate-analysis")
#     print("Pipeline execution completed and results pushed to the Hub.")