import os
import json
import time
from datasets import DatasetDict

async def save_checkpoint(dataset_dict, split_name, record_count, checkpoint_dir, log_fn=print):
    """
    Save a checkpoint dataset to disk.
    
    Args:
        dataset_dict: DatasetDict to save as a checkpoint
        split_name: Name of the split being processed
        record_count: Number of records processed so far
        checkpoint_dir: Directory to save checkpoints in
        log_fn: Logging function
        
    Returns:
        bool: Success status
    """
    try:
        start_time = time.time()
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_{record_count}")
        dataset_dict.save_to_disk(checkpoint_path)
        
        # Save metadata about the checkpoint
        metadata = {
            "timestamp": time.time(),
            "split_name": split_name,
            "record_count": record_count,
            "checkpoint_path": checkpoint_path
        }
        
        metadata_path = os.path.join(checkpoint_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        duration = time.time() - start_time
        log_fn(f"Saved checkpoint for {split_name} at {record_count} records in {duration:.2f}s")
        return True
    except Exception as e:
        log_fn(f"Error saving checkpoint: {str(e)}")
        return False

async def find_latest_checkpoint(checkpoint_dir, split_name, log_fn=print):
    """
    Find the latest checkpoint for a specific split.
    
    Args:
        checkpoint_dir: Directory containing checkpoints
        split_name: Name of the split
        log_fn: Logging function
        
    Returns:
        tuple: (checkpoint_path, record_count) or (None, 0) if not found
    """
    try:
        if not os.path.exists(checkpoint_dir):
            return None, 0
            
        checkpoints = []
        for item in os.listdir(checkpoint_dir):
            item_path = os.path.join(checkpoint_dir, item)
            if os.path.isdir(item_path) and item.startswith("checkpoint_"):
                try:
                    count = int(item.replace("checkpoint_", ""))
                    metadata_path = os.path.join(item_path, "metadata.json")
                    
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        
                        if metadata.get("split_name") == split_name:
                            checkpoints.append((count, item_path, metadata.get("timestamp", 0)))
                except (ValueError, IOError) as e:
                    log_fn(f"Warning: Skipping invalid checkpoint {item}: {str(e)}")
        
        if not checkpoints:
            return None, 0
            
        # Sort by record count (descending)
        checkpoints.sort(key=lambda x: x[0], reverse=True)
        latest_count, latest_path, latest_time = checkpoints[0]
        
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_time))
        log_fn(f"Found latest checkpoint for {split_name} with {latest_count} records from {time_str}")
        
        return latest_path, latest_count
    except Exception as e:
        log_fn(f"Error finding latest checkpoint: {str(e)}")
        return None, 0

async def load_checkpoint(checkpoint_path, log_fn=print):
    """
    Load a checkpoint from disk.
    
    Args:
        checkpoint_path: Path to the checkpoint directory
        log_fn: Logging function
        
    Returns:
        DatasetDict: The loaded dataset or None if failed
    """
    try:
        if not os.path.exists(checkpoint_path):
            log_fn(f"Checkpoint path does not exist: {checkpoint_path}")
            return None
            
        start_time = time.time()
        dataset_dict = DatasetDict.load_from_disk(checkpoint_path)
        duration = time.time() - start_time
        
        log_fn(f"Loaded checkpoint with {sum(len(ds) for ds in dataset_dict.values())} total records in {duration:.2f}s")
        
        # Log the splits that were loaded
        for split_name, dataset in dataset_dict.items():
            log_fn(f"- Split '{split_name}': {len(dataset)} records")
            
        return dataset_dict
    except Exception as e:
        log_fn(f"Error loading checkpoint: {str(e)}")
        return None
