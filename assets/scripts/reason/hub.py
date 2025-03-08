import os
import asyncio
import time
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

def ensure_consistent_columns(records, field_names=None):
    """
    Make sure all records have the same set of columns.
    
    Args:
        records: List of record dictionaries
        field_names: Optional list of field names to ensure exist
        
    Returns:
        list: Records with consistent columns
    """
    if not records:
        return records
        
    if field_names is None:
        field_names = get_field_names()
    
    # Make a copy of the records to avoid modifying originals
    updated_records = []
    
    for record in records:
        new_record = dict(record)  # Clone the record
        
        # Make sure every standard field exists
        for field in field_names:
            if field not in new_record:
                new_record[field] = ""
                
        updated_records.append(new_record)
    
    return updated_records

def create_dataset_with_splits(successful_records, failed_records, split_name):
    """Create a dataset with separate splits for successful and failed records."""
    field_names = get_field_names()
    empty_record = {field_name: "" for field_name in field_names}
    empty_record["id"] = "0"  # Set default ID
    
    # Ensure consistent columns in both successful and failed records
    successful_records = ensure_consistent_columns(successful_records, field_names)
    failed_records = ensure_consistent_columns(failed_records, field_names)
    
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

def normalize_column_structure(dataset_dict, log_fn=print):
    """
    Ensure consistent column structure between main splits and failed splits.
    
    Args:
        dataset_dict: DatasetDict with splits to normalize
        log_fn: Logging function (defaults to print)
        
    Returns:
        DatasetDict: Updated dataset dictionary with normalized columns
    """
    for split_name, split_data in list(dataset_dict.items()):
        log_fn(f"- Split '{split_name}': {len(split_data)} records, columns: {', '.join(split_data.column_names)}")
        
        # Check if this is a failed split
        if split_name.endswith('_failed'):
            base_split = split_name.replace('_failed', '')
            if base_split in dataset_dict:
                # Get the columns from the base split
                base_columns = dataset_dict[base_split].column_names
                
                # Check if column sets don't match
                if set(base_columns) != set(split_data.column_names):
                    log_fn(f"  - Normalizing columns in '{split_name}' to match '{base_split}'")
                    
                    # Convert to list of dicts, ensure consistent columns, and convert back
                    records = split_data.to_list()
                    consistent_records = ensure_consistent_columns(records)
                    dataset_dict[split_name] = Dataset.from_list(consistent_records)
                    log_fn(f"  - Updated columns: {', '.join(dataset_dict[split_name].column_names)}")
    
    return dataset_dict

async def prepare_final_dataset(all_datasets, total_records, directories, destination, config=None, log_fn=print):
    """
    Prepare the final dataset and upload to Hugging Face Hub.
    
    Args:
        all_datasets: Dictionary of processed datasets by split name or DatasetDict
        total_records: Total number of records processed
        directories: Dictionary with directory paths
        destination: Hugging Face destination dataset ID
        config: Optional configuration dictionary
        log_fn: Logging function (default: print)
        
    Returns:
        bool: Success status
    """
    if not all_datasets:
        return False
        
    log_fn(f"=== Final Dataset Preparation ===")
    
    # Convert to DatasetDict if it's not already
    if isinstance(all_datasets, dict) and not isinstance(all_datasets, DatasetDict):
        dataset_dict = DatasetDict(all_datasets)
        log_fn(f"- Created dataset with {total_records} total records across {len(all_datasets)} splits")
    else:
        dataset_dict = all_datasets  # Already a DatasetDict
        log_fn(f"- Using existing dataset with {sum(len(ds) for ds in dataset_dict.values())} total records")
    
    # Check for consistent column structure across splits
    # and normalize failed splits to match successful ones
    dataset_dict = normalize_column_structure(dataset_dict, log_fn=log_fn)
    
    # Save locally
    if directories and "cs" in directories:
        cs_path = directories["cs"]
        dataset_dict.save_to_disk(cs_path)
        log_fn(f"- Saved unified dataset to {cs_path}")
    
    # Push to HuggingFace Hub
    if destination:
        log_fn(f"- Pushing dataset to Hugging Face Hub: {destination}")
        success = await push_dataset_to_hub(dataset_dict, destination, config=config, log_fn=log_fn)
        if not success:
            log_fn(f"- Failed to push dataset to Hugging Face Hub")
            return False
        else:
            # Successfully pushed to hub
            log_fn(f"- Successfully pushed dataset to Hugging Face Hub: {destination}")
            
            # Update state file to mark as pushed (this will be a no-op if the processor doesn't update state)
            try:
                from processor import save_processing_state
                if directories and "rd" in directories:
                    # This is a defensive update - the main function will also update the state
                    await save_processing_state(
                        -1, total_records, "all_complete", directories, 
                        source=config.get('src', ''), 
                        destination=destination, 
                        log_fn=log_fn,
                        processing_complete=True,
                        pushed_to_hub=True
                    )
            except ImportError:
                pass  # Ignore if save_processing_state can't be imported
    
    # Don't clear processing state here - leave that to the main function
    
    return True

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
