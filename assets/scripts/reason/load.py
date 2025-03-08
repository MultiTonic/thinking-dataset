from datasets import load_dataset

async def load_dataset_split(source, split, offset=0, max_records=0, logger=None):
    """
    Load a specific split from a Hugging Face dataset with optional slicing.
    
    Args:
        source: Dataset source identifier (repo name or path)
        split: The split name to load
        offset: Start position for slicing (default: 0)
        max_records: Maximum number of records to load (default: 0 = all)
        logger: Optional logging function
        
    Returns:
        Dataset: The loaded dataset or None if failed
    """
    try:
        if logger: logger(f"Loading dataset from {source}")
        dataset_dict = load_dataset(source)
        
        if split in dataset_dict:
            full_dataset = dataset_dict[split]
            total_records = len(full_dataset)
            
            if offset > 0 or max_records > 0:
                if offset >= total_records:
                    if logger: logger(f"Error: Offset {offset} exceeds dataset size {total_records}")
                    return None
                    
                end_idx = total_records if max_records == 0 else min(offset + max_records, total_records)
                dataset = full_dataset.select(range(offset, end_idx))
                
                if logger: logger(f"Using dataset slice: records {offset} to {end_idx-1} (out of {total_records} total)")
            else:
                dataset = full_dataset
                if logger: logger(f"Using complete dataset: {total_records} records")
                
            if logger: logger(f"Dataset loaded: {len(dataset)} records in '{split}' split")
            if logger: logger(f"Dataset columns: {', '.join(dataset.column_names)}")
            
            return dataset
        else:
            available_splits = ", ".join(dataset_dict.keys())
            if logger: logger(f"Dataset loaded but split '{split}' not found. Available splits: {available_splits}")
            return None
            
    except Exception as e:
        if logger: logger(f"Error loading dataset: {e}")
        return None

async def load_all_splits(source, splits, offset=0, max_records=0, logger=None):
    """
    Load multiple splits from a Hugging Face dataset.
    
    Args:
        source: Dataset source identifier (repo name or path)
        splits: List of split names to load
        offset: Start position for slicing (default: 0)
        max_records: Maximum number of records to load (default: 0 = all)
        logger: Optional logging function
        
    Returns:
        dict: Dictionary of loaded datasets by split name
    """
    result = {}
    for split in splits:
        result[split] = await load_dataset_split(source, split, offset, max_records, logger)
    return result
