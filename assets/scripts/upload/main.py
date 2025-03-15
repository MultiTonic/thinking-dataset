import argparse
import os
import glob
import logging
from typing import Dict, List
from datasets import Dataset, DatasetDict, load_from_disk
from huggingface_hub import login

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%X"
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Load arrow files and upload them as a dataset to HuggingFace Hub. "
                    "This script finds all arrow datasets in the specified directory, "
                    "combines them into a single dataset with multiple splits, and uploads "
                    "to the HuggingFace Hub.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--hf-token", required=True, 
                      help="HuggingFace authentication token for uploading datasets")
    parser.add_argument("--input", default="./data", 
                      help="Directory containing arrow datasets (default: ./data)")
    parser.add_argument("--output", required=True, 
                      help="Output dataset name on HuggingFace (e.g. DataTonic/dark_thoughts_case_study_reason)")
    parser.add_argument("--private", action="store_true", 
                      help="Set dataset as private on HuggingFace Hub (default: public)")
    return parser.parse_args()

def find_arrow_datasets(directory: str) -> List[str]:
    """Find all arrow dataset directories in the given directory."""
    dataset_paths = []
    # Look for directories containing dataset metadata files
    for path in glob.glob(os.path.join(directory, "**", "dataset_info.json"), recursive=True):
        dataset_dir = os.path.dirname(path)
        dataset_paths.append(dataset_dir)
    
    # If no datasets found, check if the directory itself is a dataset
    if not dataset_paths and os.path.exists(os.path.join(directory, "dataset_info.json")):
        dataset_paths.append(directory)
        
    return dataset_paths

def get_split_name(dataset_path: str) -> str:
    """Extract a readable split name from the dataset path."""
    # Use the directory name as the split name
    split_name = os.path.basename(dataset_path)
    
    # Clean up common prefixes/suffixes to get a cleaner name
    for prefix in ["interim_batch_", "batch_", "split_", "dataset_"]:
        if split_name.startswith(prefix):
            split_name = split_name[len(prefix):]
    
    return split_name

def load_datasets(dataset_paths: List[str]) -> DatasetDict:
    """Load all datasets and combine them into a DatasetDict."""
    dataset_dict = {}
    
    for dataset_path in dataset_paths:
        try:
            # Try to load the dataset
            dataset = load_from_disk(dataset_path)
            
            # If it's already a DatasetDict, extract its splits
            if isinstance(dataset, DatasetDict):
                for split_name, split_dataset in dataset.items():
                    split_key = f"{get_split_name(dataset_path)}_{split_name}"
                    dataset_dict[split_key] = split_dataset
                    logger.info(f"Loaded split {split_key} with {len(split_dataset)} records")
            else:
                # It's a single Dataset
                split_name = get_split_name(dataset_path)
                dataset_dict[split_name] = dataset
                logger.info(f"Loaded split {split_name} with {len(dataset)} records")
                
        except Exception as e:
            logger.error(f"Failed to load dataset from {dataset_path}: {e}")
    
    return DatasetDict(dataset_dict)

def upload_dataset(dataset_dict: DatasetDict, output_name: str, hf_token: str, private: bool = True) -> None:
    """Upload the dataset to HuggingFace Hub."""
    try:
        # Log what we're uploading
        logger.info(f"Uploading dataset {output_name} with the following splits:")
        for split_name, dataset in dataset_dict.items():
            logger.info(f"  - {split_name}: {len(dataset)} records")
            if len(dataset.column_names) > 0:
                logger.info(f"    Columns: {', '.join(dataset.column_names)}")
        
        # Upload to HuggingFace Hub
        dataset_dict.push_to_hub(
            output_name,
            token=hf_token,
            private=private
        )
        logger.info(f"Successfully uploaded dataset to {output_name}")
    except Exception as e:
        logger.error(f"Failed to upload dataset: {e}")
        raise

def main() -> None:
    """Main function to load and upload datasets."""
    args = parse_args()
    
    # Log into HuggingFace
    logger.info(f"Logging into HuggingFace with provided token")
    login(token=args.hf_token)
    
    # Find all datasets in the input directory
    logger.info(f"Searching for arrow datasets in {args.input}")
    dataset_paths = find_arrow_datasets(args.input)
    
    if not dataset_paths:
        logger.error(f"No datasets found in {args.input}")
        return
    
    logger.info(f"Found {len(dataset_paths)} datasets")
    for path in dataset_paths:
        logger.info(f"  - {path}")
    
    # Load all datasets
    logger.info("Loading datasets...")
    dataset_dict = load_datasets(dataset_paths)
    
    if not dataset_dict:
        logger.error("No valid datasets were loaded")
        return
    
    # Upload the combined dataset
    logger.info(f"Uploading dataset to {args.output}")
    upload_dataset(dataset_dict, args.output, args.hf_token, args.private)
    
    logger.info("All done!")

if __name__ == "__main__":
    main()
