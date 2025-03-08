import os
from datasets import Dataset, DatasetDict

def get_field_names():
    """Return standard field names used in our dataset in the correct order"""
    return [
        "id", 
        "think", 
        "response", 
        "query", 
        "category",
        "source_data",
        "endpoint",
        "source"
    ]

def create_dataset_with_splits(successful_records, failed_records, split_name):
    """Create a dataset with separate splits for successful and failed records."""
    field_names = get_field_names()
    empty_record = {field_name: "" for field_name in field_names}
    empty_record["id"] = "0"  # Set default ID
    
    for record in successful_records:
        if "id" in record:
            record["id"] = str(record["id"])
    
    for record in failed_records:
        if "id" in record:
            record["id"] = str(record["id"])
    
    dataset_splits = {}
    if successful_records:
        dataset_splits[split_name] = Dataset.from_list(successful_records)
    else:
        dataset_splits[split_name] = Dataset.from_list([empty_record]).select([])
        
    if failed_records:
        dataset_splits[f"{split_name}_failed"] = Dataset.from_list(failed_records)
    
    return DatasetDict(dataset_splits)

def prepare_splits_for_hub(dataset_dict):
    """
    Extract data from a potentially nested DatasetDict into a flat structure.
    Handles both direct Dataset objects and nested DatasetDict structures.
    
    Args:
        dataset_dict: DatasetDict with potentially nested structure
    
    Returns:
        DatasetDict: A flat structure with all splits extracted and organized
    """
    # Create our flat splits structure
    splits = {}
    
    # Define empty record template using the standard field names
    field_names = get_field_names()
    empty_record = {field_name: "" for field_name in field_names}
    empty_record["id"] = "0"  # Set default ID
    
    # Process all splits in the dataset_dict
    for split_name, dataset in dataset_dict.items():
        if isinstance(dataset, DatasetDict):
            # Handle nested structure (like split and split_failed)
            for nested_split, nested_dataset in dataset.items():
                # For nested splits, use the nested split name to avoid collisions
                splits[nested_split] = nested_dataset
        else:
            # This is directly a Dataset
            splits[split_name] = dataset
    
    # Create the DatasetDict with the flat split structure
    return DatasetDict(splits)

async def push_dataset_to_hub(dataset_dict, destination, config=None, log_fn=print):
    """
    Prepare and push a dataset to the Hugging Face Hub.
    
    Args:
        dataset_dict: A potentially nested DatasetDict with our processed records
        destination: The Hugging Face dataset ID to push to
        config: Configuration dictionary with optional hf_token and private settings
        log_fn: Logging function (defaults to print)
    
    Returns:
        bool: Success status
    """
    try:
        log_fn(f"Preparing dataset for upload to {destination}")
        
        # Prepare the dataset with the right split structure
        final_dataset = prepare_splits_for_hub(dataset_dict)
        
        # Log our structure
        log_fn(f"Prepared dataset for upload with splits:")
        for split_name, split_data in final_dataset.items():
            log_fn(f"- {split_name}: {len(split_data)} records")
            if len(split_data) > 0:
                log_fn(f"  - Columns: {', '.join(split_data.column_names)}")
        
        # Get Hub upload parameters
        huggingface_token = config.get('hf_token') if config else None
        is_private = config.get('private', False) if config else False
        
        # Push to Hub
        if huggingface_token:
            log_fn("Using HF_TOKEN from config")
            final_dataset.push_to_hub(destination, token=huggingface_token, private=is_private)
        else:
            log_fn("No HF_TOKEN in config, using default credentials")
            final_dataset.push_to_hub(destination, private=is_private)
            
        log_fn(f"Successfully pushed dataset to {destination}")
        return True
    except Exception as error:
        log_fn(f"Error pushing dataset to Hugging Face Hub: {str(error)}")
        return False
