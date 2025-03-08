import os
from datasets import DatasetDict

async def check_and_handle_resumption(arguments, directories, source, destination, log_fn, config=None):
    """
    Check if we're resuming a previous run and handle appropriate actions.
    
    This function specifically handles the case where processing was completed
    but pushing to the hub failed, allowing direct resumption from the push step.
    
    Args:
        arguments: Command line arguments
        directories: Dictionary of directories
        source: Source dataset name
        destination: Destination dataset name
        log_fn: Logging function
        config: Configuration dictionary
        
    Returns:
        bool: True if resumption was handled (should skip normal processing), 
              False if normal processing should continue
    """
    # Check if we're resuming a completed processing that just needs to be pushed
    if not arguments.resume or "resume_state" not in directories:
        return False
        
    resume_state = directories["resume_state"]
    if not resume_state.get('processing_complete', False) or resume_state.get('pushed_to_hub', False):
        # Either processing is not complete or already pushed to hub
        return False
        
    log_fn(f"Resuming: All processing is complete but dataset was not pushed to hub")
    
    # Check if we have a consolidated dataset ready to push
    cs_dir = directories.get('cs')
    if not cs_dir or not os.path.exists(cs_dir):
        log_fn(f"Cannot find processed dataset directory at {cs_dir}")
        return False
        
    # Load the dataset
    try:
        dataset_dict = DatasetDict.load_from_disk(cs_dir)
        if not dataset_dict:
            log_fn(f"Could not load dataset from {cs_dir}")
            return False
            
        total_records = sum(len(ds) for ds in dataset_dict.values())
        log_fn(f"Loaded processed dataset with {total_records} total records")
        
        # Import here to avoid circular import issues
        from hub import prepare_final_dataset
        from processor import save_processing_state
        
        # Skip to push step
        log_fn(f"Skipping processing and proceeding directly to push operation...")
        success = await prepare_final_dataset(dataset_dict, total_records, directories, destination, config=config, log_fn=log_fn)
        
        if success:
            log_fn("Dataset successfully pushed to hub")
            
            # Update state file to mark as pushed
            await save_processing_state(
                -1, total_records, "all_complete", directories, 
                source=resume_state.get('source', ''),
                destination=destination, 
                log_fn=log_fn, 
                processing_complete=True, 
                pushed_to_hub=True
            )
            return True
        else:
            log_fn("Failed to push dataset to hub")
            return True  # Still return True to skip normal processing
    except Exception as e:
        log_fn(f"Error during resumption: {str(e)}")
        log_fn("Will proceed with normal processing instead")
        return False
