import os
import json
import time

async def save_checkpoint(data, split, total_processed, checkpoint_dir, log_fn=None):
    """
    Save a checkpoint of the current dataset processing state to disk.
    
    Args:
        data: The dataset to save
        split: The split name being processed
        total_processed: Number of records processed so far
        checkpoint_dir: Directory to save the checkpoint
        log_fn: Optional logging function
    
    Returns:
        bool: Success status
    """
    try:
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_{split}_{total_processed}")
        data.save_to_disk(checkpoint_path)
        if log_fn:
            log_fn(f"Saved checkpoint at {checkpoint_path} after processing {total_processed} records")
        
        # Create metadata about this checkpoint
        metadata = {
            "split": split,
            "processed": total_processed,
            "timestamp": time.time(),
            "checkpoint_path": checkpoint_path
        }
        
        # Save metadata to a JSON file
        with open(os.path.join(checkpoint_dir, f"meta_{split}.json"), 'w') as f:
            json.dump(metadata, f)
        
        return True
    except Exception as e:
        error_msg = f"Error saving checkpoint: {str(e)}"
        if log_fn:
            log_fn(error_msg)
        return False
