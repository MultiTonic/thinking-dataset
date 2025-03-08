import asyncio
import os
import random
import time
import json

from datasets import Dataset
from tenacity import retry, stop_after_attempt, wait_random

from endpoints import get_next_endpoint
from generate import generate_thinking
from load import load_dataset_split
from hub import create_dataset_with_splits
from checkpoints import save_checkpoint
from constants import (
    MAX_WORKERS, MAX_RETRIES, REQUEST_TIMEOUT, ENDPOINT_COOLDOWN
)

async def save_processing_state(batch_index, total_processed, split_name, directories, source, destination, log_fn=None, processing_complete=False, pushed_to_hub=False):
    """
    Save the current processing state to a JSON file.
    
    Args:
        batch_index: Index of the last completed batch
        total_processed: Total records processed so far
        split_name: Current split being processed
        directories: Directory structure information
        source: Source dataset
        destination: Destination dataset
        log_fn: Optional logging function
        processing_complete: Whether all processing is complete
        pushed_to_hub: Whether the dataset has been pushed to the hub
    """
    try:
        state_file = os.path.join(directories["rd"], "processing_state.json")
        state = {
            "timestamp": time.time(),
            "batch_index": batch_index,
            "total_processed": total_processed,
            "split_name": split_name,
            "source": source,
            "destination": destination,
            "processing_complete": processing_complete,
            "pushed_to_hub": pushed_to_hub
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        if log_fn:
            if processing_complete:
                log_fn(f"Saved processing state: All processing complete, push status: {'complete' if pushed_to_hub else 'pending'}")
            else:
                log_fn(f"Saved processing state after batch {batch_index+1} ({total_processed} records processed)")
    except Exception as e:
        if log_fn:
            log_fn(f"Warning: Could not save processing state: {str(e)}")

async def proc_1sp(split_name, split_code, source, offset, max_records, directories, 
                  config, endpoints, telemetry_stats, arguments, 
                  batch_size_default, checkpoint_interval_default, max_workers_default, 
                  max_retries, request_timeout, endpoint_cooldown, logger, file_logger, test_mode):
    """
    Process a single split of the dataset, handling batching, checkpointing, and record processing.
    
    Args:
        split_name: Split name
        split_code: Split code
        source: Source dataset identifier
        offset: Record offset
        max_records: Maximum records to process
        directories: Directory structure information
        config: Configuration dictionary
        endpoints: List of available endpoints
        telemetry_stats: TelemetryStats instance for metrics
        arguments: Command line arguments
        batch_size_default, checkpoint_interval_default, max_workers_default: Various defaults
        max_retries: Maximum number of retry attempts
        request_timeout: API request timeout in seconds
        endpoint_cooldown: Cooldown period between endpoint usage
        logger: Logging function
        file_logger: File logger
        test_mode: Whether in test mode
    
    Returns:
        tuple: (dataset_dict, success_count)
    """
    telemetry_stats.reset_stats()
    
    logger(f"Processing split: {split_name} ({split_code})")
    
    logger(f"Column mappings: query={config['columns']['query']}, response={config['columns']['response']}, think={config['columns']['think']}")
    
    dataset = await load_dataset_split(source, split_name, offset, max_records, logger=logger)
    if not dataset:
        logger(f"Failed to load dataset for split {split_name}")
        return {}, 0
        
    query_column = config['columns']['query']
    response_column = config['columns']['response']
    think_column = config['columns']['think']
    
    if query_column not in dataset.column_names or response_column not in dataset.column_names:
        logger(f"Error: Required columns not found in dataset")
        return {}, 0
    
    categories = set(dataset["category"]) if "category" in dataset.column_names else set()
    if categories:
        logger(f"Found categories in dataset: {', '.join(categories)}")
        
        category_counts = {}
        for category in categories:
            category_counts[category] = sum(1 for c in dataset["category"] if c == category)
        for category, count in category_counts.items():
            logger(f"Category '{category}': {count} records")
    else:
        logger(f"Warning: No 'category' column found in dataset, will use default category")
    
    total_records = len(dataset)
    logger(f"Found {total_records} records with query and response columns for split {split_name}")
    
    # Adjust batch size based on total_records if needed
    batch_size = batch_size_default
    if total_records < batch_size:
        batch_size = total_records
        logger(f"Adjusted batch size to {batch_size} to match available records")
    
    # Adjust checkpoint interval if needed - ensure it's never larger than total records
    checkpoint_interval = checkpoint_interval_default
    if checkpoint_interval > total_records:
        checkpoint_interval = total_records
        logger(f"Adjusted checkpoint interval to {checkpoint_interval} to match available records")
    
    # Adjust worker count if needed
    worker_count = arguments.workers if arguments.workers is not None else max_workers_default
    if worker_count > total_records:
        worker_count = max(1, total_records)
        logger(f"Adjusted worker count to {worker_count} to match available records")
    
    # Update telemetry to reflect actual number of records being processed
    telemetry_stats.total_expected = total_records
    
    logger(f"Using {worker_count} workers, batches of {batch_size}, checkpoint every {checkpoint_interval}")
    
    semaphore = asyncio.Semaphore(worker_count)
    
    all_results = []
    success_results = []
    failed_results = []
    total_processed = 0
    
    total_needed = total_records
    telemetry_stats.last_log_time = time.time() - 30

    # Fix: Create a helper function to ensure consistent record structure
    def create_error_record(row, record_id, error_message):
        error_record = {}
        
        # Ensure all fields from successful records exist in error records too
        error_record["id"] = str(row["id"]) if row and "id" in row else f"error_{record_id}"
        error_record[think_column] = f"ERROR: {error_message}"
        error_record[response_column] = row[response_column] if row else ""
        error_record[query_column] = row[query_column] if row else ""
        error_record["category"] = row.get("category", "") if row else ""
        error_record["endpoint"] = f"error - {type(error_message).__name__}"
        error_record["source"] = config.get('src', 'unknown')
        error_record["source_data"] = ""
        
        # Add source_data if it exists in original
        source_data_col = config['columns'].get('source_data')
        if row and source_data_col and source_data_col in row:
            error_record["source_data"] = row[source_data_col]
        
        # Copy any other fields from original record
        if row:
            for c in row:
                if c not in error_record and c not in [response_column, think_column, query_column, "id"]:
                    error_record[c] = row[c]
                    
        return error_record

    # Determine if we're resuming and need to skip batches
    resuming = False
    resume_batch_index = -1
    resume_processed_count = 0
    
    if arguments.resume and "resume_state" in directories:
        resume_state = directories["resume_state"]
        if resume_state.get('split_name') == split_name:
            resuming = True
            resume_batch_index = resume_state.get('batch_index', -1)
            resume_processed_count = resume_state.get('total_processed', 0)
            
            if resuming and resume_processed_count > 0:
                logger(f"Resuming processing of split '{split_name}' from batch {resume_batch_index+2} ({resume_processed_count} records already processed)")
                # Update success_results and total_processed
                # We would need to load the checkpoint data here
                
                if "ck" in directories:
                    checkpoint_file = os.path.join(directories["ck"], f"checkpoint_{resume_processed_count}")
                    if os.path.exists(checkpoint_file):
                        logger(f"Loading data from checkpoint: {checkpoint_file}")
                        try:
                            # Load checkpoint data and update success_results, failed_results
                            from datasets import DatasetDict
                            checkpoint_ds = DatasetDict.load_from_disk(checkpoint_file)
                            if split_name in checkpoint_ds:
                                success_records = checkpoint_ds[split_name].to_list()
                                success_results.extend(success_records)
                                logger(f"Loaded {len(success_records)} successful records")
                            
                            failed_split = f"{split_name}_failed"
                            if failed_split in checkpoint_ds:
                                failed_records = checkpoint_ds[failed_split].to_list()
                                failed_results.extend(failed_records)
                                logger(f"Loaded {len(failed_records)} failed records")
                                
                            # Update telemetry stats
                            telemetry_stats.successful_generations = len(success_results)
                            telemetry_stats.failed_generations = len(failed_results)
                        except Exception as e:
                            logger(f"Warning: Could not load checkpoint data: {str(e)}")

    for start_idx in range(0, total_records, batch_size):
        batch_index = start_idx // batch_size
        
        # Skip batches we've already processed when resuming
        if resuming and batch_index <= resume_batch_index:
            logger(f"Skipping batch {batch_index+1} as it was already processed")
            continue
            
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, total_records)
        current_batch = dataset.select(range(start_idx, end_idx))
        current_batch_size = len(current_batch)
        
        logger(f"Processing batch {batch_index+1}: records {start_idx+1} to {end_idx} (batch size: {current_batch_size})")
        
        # Create all tasks at once, rather than waiting for some to complete first
        task_list = []
        for i, row in enumerate(current_batch):
            idx = start_idx + i
            record_id = str(row.get('id', idx))
            
            task = asyncio.create_task(process_record_with_full_retries(
                row, idx, query_column, response_column, think_column, split_name, semaphore, config, endpoints, 
                telemetry_stats, request_timeout, endpoint_cooldown, max_retries, directories, logger, file_logger, test_mode
            ))
            task.record_id = record_id
            task.row = row
            task.row_idx = idx
            task_list.append(task)
        
        # Process tasks as they complete
        batch_results = []
        while task_list:
            # Wait for any task to complete
            done, task_list = await asyncio.wait(
                task_list,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Process completed tasks
            for completed_task in done:
                try:
                    result = completed_task.result()
                    if "id" in result:
                        result["id"] = str(result["id"])
                    batch_results.append(result)
                    if result[think_column].startswith("ERROR:"):
                        failed_results.append(result)
                    else:
                        success_results.append(result)
                except Exception as e:
                    record_id = getattr(completed_task, 'record_id', 'unknown')
                    row_idx = getattr(completed_task, 'row_idx', -1)
                    row = getattr(completed_task, 'row', None)
                    
                    logger(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                    
                    # Use the helper function to create consistent error records
                    error_record = create_error_record(row, record_id, str(e))
                    
                    batch_results.append(error_record)
                    failed_results.append(error_record)
                
                # Update telemetry periodically
                if time.time() - telemetry_stats.last_log_time > 30:
                    for line in telemetry_stats.get_telemetry_lines(total_needed):
                        logger(line)
                    telemetry_stats.last_log_time = time.time()
        
        all_results.extend(batch_results)
        total_processed += len(batch_results)
        batch_duration = time.time() - batch_start_time
        
        success_count = len(success_results)
        error_count = len(failed_results)
        
        logger(f"Completed batch {batch_index+1} ({total_processed}/{total_records} records) in {batch_duration:.2f}s ({success_count} success, {error_count} errors)")
        
        # Log telemetry with separate lines
        for line in telemetry_stats.get_telemetry_lines(total_needed):
            logger(line)
        telemetry_stats.last_log_time = time.time()
        
        if checkpoint_interval > 0 and total_processed % checkpoint_interval == 0:
            checkpoint_dataset = create_dataset_with_splits(success_results, failed_results, split_name)
            await save_checkpoint(checkpoint_dataset, split_name, total_processed, directories["ck"], log_fn=logger)
        
        # Save processing state at the end of each batch
        await save_processing_state(
            batch_index, 
            total_processed, 
            split_name, 
            directories, 
            source,
            config.get('dst', ''),
            log_fn=logger
        )
    
    ds = create_dataset_with_splits(success_results, failed_results, split_name)
    success_count = telemetry_stats.successful_generations
    error_count = telemetry_stats.failed_generations
    logger(f"Processing complete: {total_processed} total records ({success_count} success, {error_count} errors) in split {split_name}")
    
    # Log final telemetry with separate lines
    for line in telemetry_stats.get_telemetry_lines(total_needed):
        logger(line)
    
    split_dir_path = os.path.join(directories["cs"], split_name)
    os.makedirs(split_dir_path, exist_ok=True)
    ds.save_to_disk(split_dir_path)
    logger(f"Saved dataset with {len(success_results)} successful and {len(failed_results)} failed records to {split_dir_path}")
    
    return {split_name: ds}, len(success_results)

async def proc_sp(split_name, split_code, source, offset, max_records, directories, all_datasets, 
                 total_records, config, arguments, batch_size_default, logger):
    """
    Alternative processor for dataset splits - simpler implementation.
    
    Args:
        split_name: Split name
        split_code: Split code
        source: Source dataset identifier
        offset: Record offset
        max_records: Maximum records to process
        directories: Directory structure information
        all_datasets: All processed datasets dictionary
        total_records: Total records processed so far
        config: Configuration dictionary
        arguments: Command line arguments
        batch_size_default: Default batch size
        logger: Logging function
        
    Returns:
        tuple: (updated_datasets_dict, updated_total_records)
    """
    logger(f"Processing split: {split_name} ({split_code})")
    logger(f"System prompt length: {len(config['systems'][split_code])}");logger(f"Metacog prompt length: {len(config['metacogs'][split_code])}")
    logger(f"Column mappings: query={config['columns']['query']}, response={config['columns']['response']}, think={config['columns']['think']}") 
    
    dataset = await load_dataset_split(source, split_name, offset, max_records, logger=logger)
    if not dataset:
        logger(f"Failed to load dataset for split {split_name}")
        return all_datasets, total_records
        
    query_column = config['columns']['query']
    response_column = config['columns']['response']
    think_column = config['columns']['think']
    
    if query_column not in dataset.column_names:
        logger(f"Error: Query column '{query_column}' not found in dataset")
        return all_datasets, total_records
        
    if response_column not in dataset.column_names:
        logger(f"Error: Response column '{response_column}' not found in dataset")
        return all_datasets, total_records
        
    logger(f"Found {len(dataset)} records with query and response columns for split {split_name}")
    
    all_results = []
    total_processed = 0
    batch_size = arguments.batch_size if arguments.batch_size is not None else batch_size_default
    
    for start_idx in range(0, len(dataset), batch_size):
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, len(dataset))
        current_batch = dataset.select(range(start_idx, end_idx))
        logger(f"Processing batch {start_idx//batch_size + 1}: records {start_idx+1} to {end_idx} (batch size: {len(current_batch)})")
        
        tasks = []
        for i, row in enumerate(current_batch):
            tasks.append(process_record(row, start_idx + i, query_column, response_column, think_column))
            
        batch_results = await asyncio.gather(*tasks)
        all_results.extend(batch_results)
        total_processed += len(batch_results)
        batch_duration = time.time() - batch_start_time
        logger(f"Completed batch {start_idx//batch_size + 1} ({total_processed}/{len(dataset)} records) in {batch_duration:.2f}s")
    
    logger(f"Prepared {len(all_results)} records with column order: id, prompt, think, response, query, [other fields]")
    ds = Dataset.from_list(all_results)
    split_dir_path = os.path.join(directories["cs"], split_name)
    os.makedirs(split_dir_path, exist_ok=True)
    ds.save_to_disk(split_dir_path)
    logger(f"Saved {len(all_results)} records to local directory: {split_dir_path}")
    
    all_datasets[split_name] = ds
    total_records += len(all_results)
    return all_datasets, total_records

@retry(
    stop=stop_after_attempt(3),  # Use lower retry count here as we have manual retries
    wait=wait_random(min=1, max=3),
    retry=lambda e: hasattr(e, 'should_retry') and e.should_retry,
    reraise=True
)
async def process_record(row, idx, query_column, response_column, think_column, split_name, semaphore,
                         config, endpoints, telemetry_stats, request_timeout, endpoint_cooldown, 
                         retry_limit, directories, logger, file_logger, test_mode):
    """
    Process a single record by generating the thinking process.
    
    Args:
        row: The record to process
        idx: Index of the record
        query_column, response_column, think_column: Column mappings
        split_name: Split name
        semaphore: Asyncio semaphore for concurrency control
        config: Configuration dictionary
        endpoints: Endpoints list
        telemetry_stats: Statistics tracking instance
        request_timeout: Timeout for API requests
        endpoint_cooldown: Cooldown period between endpoint usage
        retry_limit: Maximum number of retries
        directories: Directory structure
        logger: Logging function
        file_logger: File logger
        test_mode: Whether in test mode
        
    Returns:
        dict: Processed record with generated thinking
    """
    # Convert record_id to string for consistency
    record_id = str(row.get("id", idx))
    
    async with semaphore:
        try:
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Starting to process record")
            
            endpoint_idx = get_next_endpoint(endpoints, endpoint_cooldown, logger=logger)
            
            # Check if this is a retry attempt
            retry_state = getattr(process_record, 'retry', None)
            current_attempt = 1
            if retry_state and hasattr(retry_state, 'statistics'):
                stats = retry_state.statistics
                if isinstance(stats, dict):
                    current_attempt = stats.get('attempt_number', 1)
                
            if current_attempt > 1:  # If this is a retry
                logger(f"[{record_id}] Attempt {current_attempt}/{retry_limit}: Getting endpoint for retry")
                
            # Generate the thinking/reasoning for this record
            # Fix: Pass all arguments in the correct order
            reasoning, elapsed_time, metacog_prompt, endpoint_name = await generate_thinking(
                row, split_name, endpoint_idx, endpoints, config, telemetry_stats, 
                request_timeout, endpoint_cooldown, directories, logger, file_logger, test_mode
            )
            
            # Prepare the result record
            result_dict = {}
            if "id" in row:
                result_dict["id"] = str(row["id"])  # Convert to string
            else:
                result_dict["id"] = str(idx)  # Use string version of index
                
            # Add the generated thinking and existing fields
            result_dict[think_column] = reasoning
            result_dict[response_column] = row[response_column]
            result_dict[query_column] = row[query_column]
            
            # Add other metadata fields
            result_dict["category"] = row.get("category", "")
            result_dict["endpoint"] = endpoint_name
            
            # Use source dataset name
            source_dataset = config.get('src', 'unknown')
            result_dict["source"] = source_dataset
            
            # Source data could be from a specific column or a default
            result_dict["source_data"] = ""
            source_data_col = config['columns'].get('source_data')
            if source_data_col and source_data_col in row:
                result_dict["source_data"] = row[source_data_col]
            
            # Copy remaining fields from the original row
            for c in row:
                if c not in result_dict and c not in [response_column, think_column, query_column, "id"]:
                    result_dict[c] = row[c]
            
            # Enhanced logging with more details
            response_size = len(reasoning)
            retry_info = f" ({current_attempt-1} retries)" if current_attempt > 1 else ""
            logger(f"[{record_id}] Successfully completed processing in {elapsed_time:.2f}s - {response_size} chars{retry_info} - {endpoint_name}")
            
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Successfully processed in {elapsed_time:.2f}s - {response_size} chars{retry_info} - {endpoint_name}")
                
            return result_dict
                
        except Exception as e:
            # Check retry status
            retry_state = getattr(process_record, 'retry', None)
            current_attempt = 1
            if retry_state and hasattr(retry_state, 'statistics'):
                stats = retry_state.statistics
                if isinstance(stats, dict):
                    current_attempt = stats.get('attempt_number', 1)
                
            max_attempts = retry_limit
            
            if current_attempt < max_attempts:
                logger(f"[{record_id}] RETRY {current_attempt}/{max_attempts}: {type(e).__name__} - {str(e)[:100]}")
                # Attach a flag to make this exception retriable
                setattr(e, 'should_retry', True)
                # Re-raise to trigger the retry
                raise e
            else:
                logger(f"[{record_id}] ERROR after all {max_attempts} retries: {type(e).__name__} - {str(e)[:100]}")
                raise e

async def process_record_with_full_retries(row, idx, query_column, response_column, think_column, split_name, semaphore,
                                         config, endpoints, telemetry_stats, request_timeout, endpoint_cooldown, 
                                         retry_limit, directories, logger, file_logger, test_mode):
    """
    Wrapper around process_record that ensures all retry attempts are completed
    before giving up on a record.
    
    Args:
        see process_record
        
    Returns:
        dict: Processed record or error record
    """
    record_id = str(row.get("id", idx))
    retry_count = 0
    max_retries = retry_limit
    last_error = None
    consecutive_rate_limits = 0  # Track consecutive rate limit errors
    
    while retry_count < max_retries or is_rate_limit_error(last_error):
        try:
            # Try to process the record
            return await process_record(row, idx, query_column, response_column, think_column, split_name, semaphore,
                                 config, endpoints, telemetry_stats, request_timeout, endpoint_cooldown, 
                                 retry_limit, directories, logger, file_logger, test_mode)
        except Exception as e:
            last_error = e
            
            # Check if this is a rate limit error
            if is_rate_limit_error(e):
                consecutive_rate_limits += 1
                
                # Mark the endpoint as rate limited (just for tracking, no extra cooldown)
                endpoint_idx = getattr(e, 'endpoint_idx', None)
                if endpoint_idx is not None and endpoint_idx < len(endpoints):
                    endpoints[endpoint_idx]['rate_limited'] = True
                    logger(f"[{record_id}] Rate limit hit on {endpoints[endpoint_idx].get('p', '')}-{endpoints[endpoint_idx].get('n', '')}")
                
                # For rate limit errors, don't count toward retry limit
                backoff_time = min(5.0 * consecutive_rate_limits, 30.0)  # Gradually increase backoff time
                logger(f"[{record_id}] Rate limit error: {type(e).__name__} - {str(e)[:100]} (waiting {backoff_time:.2f}s)")
                await asyncio.sleep(backoff_time)  # Add a backoff delay
                continue  # Try again without incrementing retry_count
            elif is_length_error(e):
                # Length issues (too short or too long) should be retried but counted toward retry limit
                retry_count += 1
                
                if retry_count >= max_retries:
                    logger(f"[{record_id}] ERROR after exhausting all {max_retries} retries: {type(e).__name__} - {str(e)[:100]}")
                    raise
                else:
                    backoff_time = random.uniform(0.5, 1.5)  # Shorter backoff for length errors
                    is_too_long = "exceeds maximum allowed length" in str(e).lower()
                    error_type = "too long" if is_too_long else "too short"
                    logger(f"[{record_id}] Response {error_type}, RETRY {retry_count}/{max_retries}: {str(e)[:100]} (waiting {backoff_time:.2f}s)")
                    await asyncio.sleep(backoff_time)
            else:
                consecutive_rate_limits = 0  # Reset consecutive rate limits
                retry_count += 1
                
                if retry_count >= max_retries:
                    logger(f"[{record_id}] ERROR after exhausting all {max_retries} retries: {type(e).__name__} - {str(e)[:100]}")
                    raise
                else:
                    backoff_time = random.uniform(1, 3)
                    logger(f"[{record_id}] Manual RETRY {retry_count}/{max_retries}: {type(e).__name__} - {str(e)[:100]} (waiting {backoff_time:.2f}s)")
                    await asyncio.sleep(backoff_time)
                    # Let the loop continue to retry

def is_rate_limit_error(error):
    """Check if an error is a rate limit error"""
    if error is None:
        return False
        
    error_message = str(error).lower()
    return (
        "429" in error_message or 
        "too many tokens" in error_message or 
        "rate limit" in error_message or
        "quota" in error_message
    )

def is_length_error(error):
    """Check if an error is related to response length (too short or too long)"""
    if error is None:
        return False
        
    error_message = str(error).lower()
    return (
        "shorter than minimum required length" in error_message or
        "exceeds maximum allowed length" in error_message
    )

async def process_splits(splits, source, config, arguments, directories, endpoints, telemetry_stats, 
                        batch_size, checkpoint_interval, logger, file_logger, test_mode):
    """
    Process all dataset splits from the source dataset.
    
    Args:
        splits: List of split names to process
        source: Source dataset identifier
        config: Configuration dictionary
        arguments: Command line arguments
        directories: Directory structure information
        endpoints: List of available endpoints
        telemetry_stats: TelemetryStats instance for metrics
        batch_size: Batch size for processing
        checkpoint_interval: Interval for saving checkpoints
        logger: Logging function
        file_logger: File logger
        test_mode: Whether in test mode
        
    Returns:
        tuple: (all_datasets, total_records)
    """
    all_datasets = {}
    total_records = 0
    
    logger(f"Starting to process {len(splits)} splits from source: {source}")
    logger(f"Max records per split: {arguments.max_records if arguments.max_records > 0 else 'unlimited'}")
    
    # If we're resuming and have state, adjust the order of splits to continue from the right split
    if arguments.resume and "resume_state" in directories:
        resume_state = directories["resume_state"]
        last_split = resume_state.get('split_name')
        if last_split in splits:
            logger(f"Reordering splits to resume from '{last_split}'")
            # Move the last processed split to the beginning
            splits = [last_split] + [s for s in splits if s != last_split]
    
    for split_name in splits:
        split_code = config["splits"][split_name]
        logger(f"Processing split '{split_name}' with code '{split_code}'")
        
        dataset_dict, count = await proc_1sp(
            split_name, split_code, source, arguments.offset, arguments.max_records, 
            directories, config, endpoints, telemetry_stats, arguments, 
            batch_size, checkpoint_interval, MAX_WORKERS, MAX_RETRIES, 
            REQUEST_TIMEOUT, ENDPOINT_COOLDOWN, logger, file_logger, test_mode
        )
        
        if dataset_dict:
            all_datasets.update(dataset_dict)
            total_records += count
            logger(f"Split '{split_name}' processed successfully: {count} records")
        else:
            logger(f"Split '{split_name}' processing failed or returned no records")
    
    # After all splits are processed, mark processing as complete in state file
    if all_datasets and arguments and not test_mode:
        destination = arguments.dst or config.get('dst', '')
        # Mark processing as complete but not yet pushed to hub
        await save_processing_state(
            -1,  # batch_index not applicable for complete processing
            total_records,
            "all_complete",  # special value to indicate all splits are done
            directories,
            source,
            destination,
            log_fn=logger,
            processing_complete=True,
            pushed_to_hub=False
        )
    
    if total_records == 0:
        logger("WARNING: No records were processed successfully across all splits")
    else:
        logger(f"Successfully processed {total_records} records across {len(all_datasets)} splits")
    
    return all_datasets, total_records
