import asyncio
import os
import random
import time

from datasets import Dataset
from tenacity import retry, stop_after_attempt, wait_random

from endpoints import get_next_endpoint
from generate_thinking import generate_thinking
from load_dataset import load_dataset_split
from push_hub import create_dataset_with_splits
from save_checkpoints import save_checkpoint

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
    
    batch_size = arguments.batch_size if arguments.batch_size is not None else batch_size_default
    checkpoint_interval = arguments.checkpoint_interval if arguments.checkpoint_interval is not None else checkpoint_interval_default
    worker_count = arguments.workers if arguments.workers is not None else max_workers_default
    
    logger(f"Using {worker_count} workers, batches of {batch_size}, checkpoint every {checkpoint_interval}")
    
    semaphore = asyncio.Semaphore(worker_count)
    
    all_results = []
    success_results = []
    failed_results = []
    total_processed = 0
    
    total_needed = total_records
    telemetry_stats.last_log_time = time.time() - 30
    
    for start_idx in range(0, total_records, batch_size):
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, total_records)
        current_batch = dataset.select(range(start_idx, end_idx))
        current_batch_size = len(current_batch)
        
        logger(f"Processing batch {start_idx//batch_size + 1}: records {start_idx+1} to {end_idx} (batch size: {current_batch_size})")
        
        task_list = []
        batch_results = []
        
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
            
            if len(task_list) >= worker_count or i == len(current_batch) - 1:
                done, remaining_tasks = await asyncio.wait(
                    task_list, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                task_list = list(remaining_tasks)
                
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
                        
                        error_record = {}
                        if row and "id" in row:
                            error_record["id"] = str(row["id"])
                        else:
                            error_record["id"] = f"error_{record_id}"
                            
                        if row:
                            error_record["prompt"] = f"Thinking process for query: {row[query_column][:50]}..."
                            error_record[think_column] = f"ERROR: Failed to generate thinking process: {str(e)}"
                            error_record[response_column] = row[response_column]
                            error_record[query_column] = row[query_column]
                            for c in row:
                                if c not in error_record and c not in [response_column, think_column, query_column, "id", "prompt"]:
                                    error_record[c] = row[c]
                        else:
                            error_record["prompt"] = "Unknown due to exception"
                            error_record[think_column] = f"ERROR: Failed to generate thinking process: {str(e)}"
                            error_record[response_column] = ""
                            error_record[query_column] = ""
                        
                        batch_results.append(error_record)
                        failed_results.append(error_record)
                    
                    if time.time() - telemetry_stats.last_log_time > 30:
                        logger(telemetry_stats.get_telemetry_string(total_needed))
                        telemetry_stats.last_log_time = time.time()
        
        if task_list:
            done, _ = await asyncio.wait(task_list)
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
                    logger(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                    
                    error_record = {
                        "id": f"error_{record_id}",
                        "prompt": "Unknown due to exception",
                        think_column: f"ERROR: Failed to generate thinking process: {str(e)}",
                        response_column: "",
                        query_column: ""
                    }
                    batch_results.append(error_record)
                    failed_results.append(error_record)
        
        all_results.extend(batch_results)
        total_processed += len(batch_results)
        batch_duration = time.time() - batch_start_time
        
        success_count = len(success_results)
        error_count = len(failed_results)
        
        logger(f"Completed batch {start_idx//batch_size + 1} ({total_processed}/{total_records} records) in {batch_duration:.2f}s ({success_count} success, {error_count} errors)")
        
        logger(telemetry_stats.get_telemetry_string(total_needed))
        telemetry_stats.last_log_time = time.time()
        
        if checkpoint_interval > 0 and total_processed % checkpoint_interval == 0:
            checkpoint_dataset = create_dataset_with_splits(success_results, failed_results, split_name)
            await save_checkpoint(checkpoint_dataset, split_name, total_processed, directories["ck"], log_fn=logger)
    
    ds = create_dataset_with_splits(success_results, failed_results, split_name)
    success_count = telemetry_stats.successful_generations
    error_count = telemetry_stats.failed_generations
    logger(f"Processing complete: {total_processed} total records ({success_count} success, {error_count} errors) in split {split_name}")
    
    logger(telemetry_stats.get_telemetry_string(total_needed))
    
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
            
            logger(f"[{record_id}] Successfully completed processing in {elapsed_time:.2f}s")
            
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Successfully processed in {elapsed_time:.2f}s")
                
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
    
    while retry_count < max_retries:
        try:
            # Try to process the record
            return await process_record(row, idx, query_column, response_column, think_column, split_name, semaphore,
                                 config, endpoints, telemetry_stats, request_timeout, endpoint_cooldown, 
                                 retry_limit, directories, logger, file_logger, test_mode)
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger(f"[{record_id}] ERROR after exhausting all {max_retries} retries: {type(e).__name__} - {str(e)[:100]}")
                # Re-raise the exception after all retries are exhausted
                raise
            else:
                backoff_time = random.uniform(1, 3)
                logger(f"[{record_id}] Manual RETRY {retry_count}/{max_retries}: {type(e).__name__} - {str(e)[:100]} (waiting {backoff_time:.2f}s)")
                await asyncio.sleep(backoff_time)  # Add a backoff delay
                # Let the loop continue to retry
