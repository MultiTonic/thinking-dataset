import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from datasets import Dataset, load_dataset
import openai
from openai import OpenAI
from dotenv import load_dotenv
from prompts import SITREPPROMPT

# Set the base URL for the OpenAI API
openai.api_base = "https://api.lingyiwanwu.com/v1"  # Replace with your actual base URL

# Configure logging to use UTF-8 encoding
logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("ONEAI_API_KEY", "e75810fc0c96453eb15c865e00edea24")

# Custom prompt templates
SUMMARY_PROMPT = """{cable_content}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

client = OpenAI(api_key=openai_api_key, base_url="https://api.lingyiwanwu.com/v1")

def load_local_dataset(file_path: str) -> Dataset:
    """Load a local parquet dataset."""
    return load_dataset("parquet", data_files={"train": file_path})["train"]

def prepare_content(dataset: Dataset) -> List[Dict[str, Any]]:
    """Prepare content for processing."""
    prepared_content = []
    for row in dataset:
        cleaned_content = row["cleaned_content"]
        prepared_content.append({"prepared_content": cleaned_content})
    return prepared_content

def append_to_file(filename: str, content: str) -> None:
    """Append a single line of content to a local file."""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{content}\n")

def generate_summaries(content: List[Dict[str, Any]], batch_size: int = 5, summary_file: str = "summaries.txt") -> List[str]:
    """Generate summaries using OpenAI API in batches and save to file after each response."""
    summaries = []
    for i in range(0, len(content), batch_size):
        batch = content[i:i + batch_size]
        messages = [
            {"role": "system", "content": SITREPPROMPT}
        ]
        for item in batch:
            messages.append({"role": "user", "content": SUMMARY_PROMPT.format(cable_content=item["prepared_content"])})
        
        try:
            response = client.chat.completions.create(
                model="yi-large",
                messages=messages,
                max_tokens=4095,
                temperature=0.9
            )
            for choice in response.choices:
                summary = choice.message.content.strip()
                summaries.append(summary)
                # Append each summary to file
                append_to_file(summary_file, summary)
        except Exception as e:
            logging.error(f"Error generating summaries for batch starting at index {i}: {e}")
    
    return summaries

def generate_comparisons(content: List[Dict[str, Any]], num_comparisons: int, batch_size: int = 5, comparison_file: str = "comparisons.txt") -> List[str]:
    """Generate comparisons using OpenAI API in batches and save to file after each response."""
    comparisons = []
    cable_sample = random.sample(content, min(len(content), num_comparisons))

    for _ in range(num_comparisons // 3):
        sampled_cables = random.sample(cable_sample, 3)
        messages = [
            {"role": "system", "content": SITREPPROMPT},
            {"role": "user", "content": COMPARISON_PROMPT.format(
                cable_1=sampled_cables[0]["prepared_content"],
                cable_2=sampled_cables[1]["prepared_content"],
                cable_3=sampled_cables[2]["prepared_content"]
            )}
        ]
        
        try:
            response = client.chat.completions.create(
                model="yi-large",
                messages=messages,
                max_tokens=2995,
                temperature=0.9
            )
            comparison = response.choices[0].message.content.strip()
            comparisons.append(comparison)
            # Append each comparison to file
            append_to_file(comparison_file, comparison)
        except Exception as e:
            logging.error(f"Error generating comparison: {e}")

    return comparisons

def push_to_hub(dataset: Dataset, repo_name: str, huggingface_token: str):
    """Push dataset to Hugging Face Hub."""
    if len(dataset) > 0:
        try:
            dataset.push_to_hub(repo_name, private=True, token=huggingface_token)
            logging.info(f"Pushed dataset to {repo_name}.")
        except Exception as e:
            logging.error(f"Error pushing dataset to {repo_name}: {e}")
    else:
        logging.warning(f"{repo_name} dataset is empty and will not be pushed to the Hub.")

if __name__ == "__main__":
    huggingface_token = os.getenv("HUGGINGFACE_TOKEN", "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")

    # Load dataset
    file_path = os.path.join( "scripts", "cables", "cleaned_data.parquet")  # Adjusted for relative path
    # file_path = "./cleaned_data.parquet"
    dataset = load_local_dataset(file_path)

    # Prepare content
    prepared_content = prepare_content(dataset)

    # Generate summaries and append each one to the file
    summaries = generate_summaries(prepared_content, summary_file="summaries.txt")
    summary_dataset = Dataset.from_dict({"text": summaries})

    # Generate comparisons and append each one to the file
    comparisons = generate_comparisons(prepared_content, num_comparisons=200000, comparison_file="comparisons.txt")
    comparison_dataset = Dataset.from_dict({"text": comparisons})

    # Push datasets to Hub
    push_to_hub(summary_dataset, "DataTonic/CaseStudies-cn-small", huggingface_token)
    push_to_hub(comparison_dataset, "DataTonic/CaseStudies-cn-multi", huggingface_token)

    if len(summary_dataset) == 0 and len(comparison_dataset) == 0:
        logging.error("Error: Both summary and comparison datasets are empty. No data was generated.")
        sys.exit(1)
