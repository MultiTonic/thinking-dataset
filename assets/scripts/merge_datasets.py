import argparse, os, logging, time, requests, asyncio
import pandas as pd
from datasets import load_dataset, Dataset, DatasetDict
import concurrent.futures
from tenacity import retry, stop_after_attempt, wait_random_exponential

DEFAULT_CONFIG_URL = "https://gist.githubusercontent.com/p3nGu1nZz/299d55b7d55df72af83f71a507f1d126/raw"
LOG_DIR = "logs"
MAX_WORKERS = 4

def log(message, console_output=True):
    try:
        file_logger.info(message)
        if console_output:
            try: console_logger.info(message)
            except UnicodeEncodeError: console_logger.info(message.encode('ascii', errors='replace').decode('ascii'))
    except Exception as e: print(f"[LOGGING ERROR] Failed to log message: {str(e)}")

def validate_config(config):
    """Validate configuration and provide defaults where needed"""
    if not config:
        raise ValueError("No configuration provided")
        
    # Check required keys
    required_keys = ['src_datasets', 'dest_dataset']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
        
    # Set defaults for optional values
    if 'private' not in config:
        config['private'] = False
        log("Dataset visibility set to Public (default)")
    
    # Set splits configuration
    if 'src_splits' not in config:
        config['src_splits'] = ['english', 'chinese', 'english_failed', 'chinese_failed']
        log(f"Using default source splits: {', '.join(config['src_splits'])}")
    
    if 'dest_splits' not in config:
        config['dest_splits'] = config['src_splits']
        log(f"Using source splits as destination splits")
    
    log(f"Config validated successfully")
    return config

def setup_loggers(log_path):
    os.makedirs(log_path, exist_ok=True)
    console_logger, file_logger = logging.getLogger("console"), logging.getLogger("file")
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    console_logger.addHandler(console_handler)
    console_logger.setLevel(logging.INFO)
    console_logger.propagate = False
    
    log_file = os.path.join(log_path, f"merge_{int(time.time())}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    file_logger.addHandler(file_handler)
    file_logger.setLevel(logging.INFO)
    file_logger.propagate = False
    
    return console_logger, file_logger

async def fetch_config():
    try:
        log(f"Fetching config from: {DEFAULT_CONFIG_URL}")
        response = requests.get(DEFAULT_CONFIG_URL)
        if response.status_code == 200:
            config_json = response.json()
            log("Config fetched successfully")
            return config_json
        log(f"Failed to fetch config: {response.status_code}", False)
        return None
    except Exception as e:
        log(f"Error fetching config: {e}", False)
        return None

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=10))
async def load_dataset_async(src, split, semaphore):
    async with semaphore:
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                dataset = await asyncio.get_event_loop().run_in_executor(
                    pool, lambda: load_dataset(src, split=split)
                )
            log(f"Loaded {len(dataset)} records from {src}/{split}")
            return dataset
        except Exception as e:
            log(f"Warning: Could not load split {split} from {src}: {e}")
            raise  # Let tenacity handle the retry

async def load_datasets(src_datasets, splits):
    datasets_dict = {}
    telemetry = {"loaded_splits": 0, "failed_splits": 0, "total_records": 0}
    
    # Adjust worker count based on source datasets
    worker_count = min(MAX_WORKERS, len(src_datasets) * 2)
    semaphore = asyncio.Semaphore(worker_count)
    
    log(f"Loading datasets with up to {worker_count} concurrent downloads...")
    
    tasks = []
    for src_idx, src in enumerate(src_datasets):
        datasets_dict[src] = {}
        log(f"Preparing to load dataset from source {src_idx + 1}: {src}")
        
        for split in splits:
            tasks.append((src, split, load_dataset_async(src, split, semaphore)))
    
    start_time = time.time()
    for src, split, task in [(s, sp, asyncio.create_task(t)) for s, sp, t in tasks]:
        try:
            dataset = await task
            if dataset is not None:
                datasets_dict[src][split] = dataset
                telemetry["loaded_splits"] += 1
                telemetry["total_records"] += len(dataset)
            else:
                telemetry["failed_splits"] += 1
        except Exception as e:
            log(f"Error loading {split} split from {src} after retries: {e}")
            datasets_dict[src][split] = None
            telemetry["failed_splits"] += 1
    
    elapsed = time.time() - start_time
    log(f"Finished loading {telemetry['loaded_splits']} dataset splits in {elapsed:.2f} seconds")
    log(f"Total records loaded: {telemetry['total_records']}")
    if telemetry["failed_splits"] > 0:
        log(f"Failed to load {telemetry['failed_splits']} splits")
    
    return datasets_dict, telemetry

def merge_datasets(datasets_dict, src_splits):
    merged = {}
    telemetry = {"merged_records": 0, "source_records": 0}
    
    for split in src_splits:
        split_dfs = []
        for src, splits_dict in datasets_dict.items():
            if split in splits_dict and splits_dict[split]:
                try:
                    df = splits_dict[split].to_pandas()
                    telemetry["source_records"] += len(df)
                    df['source'] = src
                    split_dfs.append(df)
                    log(f"Added {len(df)} records from {src}/{split}")
                except Exception as e:
                    log(f"Error processing {src}/{split}: {e}")
        
        if split_dfs:
            merged_df = pd.concat(split_dfs, ignore_index=True)
            merged[split] = Dataset.from_pandas(merged_df)
            telemetry["merged_records"] += len(merged_df)
            log(f"Created merged {split} split with {len(merged[split])} total records")
        else:
            log(f"No data found for {split} split in any source dataset")
            merged[split] = Dataset.from_dict({})
    
    return DatasetDict(merged), telemetry

def apply_column_operations(dataset_dict, column_config):
    try:
        if not column_config: return dataset_dict, {}
        
        telemetry = {"processed_splits": 0, "total_records_processed": 0}
        log("Applying column operations...")
        result_dict = {}
        
        include_columns = column_config.get('include')
        exclude_columns = column_config.get('exclude', [])
        rename_mapping = column_config.get('rename', {})
        add_columns = column_config.get('add', {})
        column_order = column_config.get('order', [])
        id_config = column_config.get('id', {})
        
        generate_ids = id_config.get('generate', False)
        id_field = id_config.get('field', 'id')
        id_start = id_config.get('start', 1)
        id_increment = id_config.get('increment', 1)
        next_id = id_start
        
        log(f"Column operations configuration:")
        if include_columns: log(f"- Including only: {include_columns}")
        if exclude_columns: log(f"- Excluding: {exclude_columns}")
        if rename_mapping: log(f"- Renaming: {rename_mapping}")
        if add_columns: log(f"- Adding: {add_columns}")
        if column_order: log(f"- Ordering: {column_order}")
        if generate_ids: log(f"- Generating IDs starting at {id_start}")
        
        for split_name, split_dataset in dataset_dict.items():
            if len(split_dataset) == 0:
                result_dict[split_name] = split_dataset
                continue
            
            df = split_dataset.to_pandas()
            
            if generate_ids:
                if id_field in df.columns: df = df.drop(columns=[id_field])
                df[id_field] = range(next_id, next_id + len(df) * id_increment, id_increment)
                next_id = next_id + len(df) * id_increment
            
            if include_columns:
                columns_to_keep = include_columns.copy()
                if generate_ids and id_field not in columns_to_keep: columns_to_keep.append(id_field)
                existing_columns = [col for col in columns_to_keep if col in df.columns]
                df = df[existing_columns]
            elif exclude_columns:
                columns_to_drop = [col for col in exclude_columns if col in df.columns]
                if columns_to_drop: df = df.drop(columns=columns_to_drop)
            
            if add_columns:
                for col_name, default_value in add_columns.items():
                    if col_name not in df.columns:
                        log(f"Adding column '{col_name}' to {split_name}")
                        df[col_name] = default_value
            
            if rename_mapping:
                renames_to_apply = {old: new for old, new in rename_mapping.items() if old in df.columns}
                if renames_to_apply: df = df.rename(columns=renames_to_apply)
            
            if column_order:
                existing_ordered_columns = [col for col in column_order if col in df.columns]
                remaining_columns = [col for col in df.columns if col not in existing_ordered_columns]
                df = df[existing_ordered_columns + remaining_columns]
            
            result_dict[split_name] = Dataset.from_pandas(df)
            telemetry["processed_splits"] += 1
            telemetry["total_records_processed"] += len(df)
            log(f"Processed {split_name} split: {len(df)} records, {len(df.columns)} columns")
        
        if generate_ids: log(f"Generated {next_id - id_start} unique IDs")
        return DatasetDict(result_dict), telemetry
    except Exception as e:
        log(f"Error applying column operations: {e}")
        return dataset_dict, {}

def standardize_schema(dataset_dict):
    try:
        log("Standardizing schema across all splits...")
        all_columns = set()
        for split_name, dataset in dataset_dict.items():
            all_columns.update(dataset.column_names)
        
        standardized_dict = {}
        for split_name, dataset in dataset_dict.items():
            df = dataset.to_pandas()
            if '__index_level_0__' in df.columns: df = df.drop(columns=['__index_level_0__'])
            
            for col in all_columns:
                if col not in df.columns:
                    if col == 'id': df[col] = range(1, len(df) + 1)
                    elif col == 'elapsed_time': df[col] = 0.0
                    else: df[col] = ""
            
            for col, dtype in {'id': 'int64', 'elapsed_time': 'float64', 'model': 'string'}.items():
                if col in df.columns:
                    try:
                        if dtype == 'string': df[col] = df[col].fillna("").astype(str)
                        elif dtype == 'int64': df[col] = df[col].fillna(0).astype(int)
                        elif dtype == 'float64': df[col] = df[col].fillna(0.0).astype(float)
                    except Exception: pass
            
            standardized_dict[split_name] = Dataset.from_pandas(df)
        return DatasetDict(standardized_dict)
    except Exception as e:
        log(f"Error standardizing schema: {e}")
        return dataset_dict

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=10))
def push_to_hub(merged_dataset, destination, hf_token=None):
    try:
        log(f"Preparing to push merged dataset to {destination}")
        
        is_private = config.get('private', False)
        log(f"Dataset visibility: {'Private' if is_private else 'Public'}")
        
        # Push to hub directly without trying to delete first
        start_time = time.time()
        push_kwargs = {
            'repo_id': destination,
            'private': is_private,
        }
        
        # Add token if provided
        if hf_token:
            push_kwargs['token'] = hf_token
            
        merged_dataset.push_to_hub(**push_kwargs)
        
        upload_time = time.time() - start_time    
        log(f"Successfully pushed merged dataset to {destination} in {upload_time:.2f}s")
        
        for split, dataset in merged_dataset.items():
            log(f"- {split}: {len(dataset)} records")
        return True
    except Exception as e:
        log(f"Error pushing to hub: {e}")
        raise

def setup_directories(log_dir, output_dir=None):
    run_id = str(int(time.time()))
    log_dir = os.path.abspath(log_dir)
    
    if output_dir:
        data_dir = os.path.join(output_dir, "data")
    else:
        data_dir = os.path.join(os.getcwd(), "data")
        
    run_dir = os.path.join(data_dir, run_id)
    merged_dir = os.path.join(run_dir, "merged")
    
    for directory in [log_dir, data_dir, run_dir, merged_dir]:
        os.makedirs(directory, exist_ok=True)
    
    return {
        "run_id": run_id,
        "log_dir": log_dir,
        "data_dir": data_dir,
        "run_dir": run_dir,
        "merged_dir": merged_dir,
    }

def report_telemetry(start_time, telemetry):
    """Generate telemetry report"""
    elapsed_time = time.time() - start_time
    
    log("=== Telemetry Report ===")
    log(f"- Total runtime: {elapsed_time:.2f}s ({elapsed_time/60:.2f} min)")
    
    if "loaded_splits" in telemetry:
        log(f"- Loaded splits: {telemetry['loaded_splits']} successful, {telemetry.get('failed_splits', 0)} failed")
    
    if "total_records" in telemetry:
        log(f"- Total source records loaded: {telemetry['total_records']}")
    
    if "merged_records" in telemetry:
        log(f"- Records after merging: {telemetry['merged_records']}")
    
    if "total_records_processed" in telemetry:
        log(f"- Records processed through column operations: {telemetry['total_records_processed']}")
    
    if "filtered_records" in telemetry:
        log(f"- Records after filtering to destination splits: {telemetry['filtered_records']}")
    
    log("=======================\n")

async def main(args):
    try:
        global dirs, config, MAX_WORKERS
        
        start_time = time.time()
        telemetry = {}
        
        # Validate config
        config = validate_config(config)
        
        if args.workers:
            MAX_WORKERS = args.workers
        
        # Adjust MAX_WORKERS based on number of source datasets
        MAX_WORKERS = min(MAX_WORKERS, len(config['src_datasets']) * 2)
        log(f"Using {MAX_WORKERS} workers for concurrent operations")
        
        dirs = setup_directories(args.log_dir or LOG_DIR, args.output)
        
        log(f"Configuration: src={', '.join(config['src_datasets'])}, dest={config['dest_dataset']}")
        
        # Load datasets - with retries handled by tenacity
        src_splits = config.get('src_splits')
        datasets_dict, load_telemetry = await load_datasets(config['src_datasets'], src_splits)
        telemetry.update(load_telemetry)
        
        # Merge datasets
        merged_dataset, merge_telemetry = merge_datasets(datasets_dict, src_splits)
        telemetry.update(merge_telemetry)
        
        # Apply column operations
        if 'columns' in config:
            processed_dataset, process_telemetry = apply_column_operations(merged_dataset, config['columns'])
            telemetry.update(process_telemetry)
            
            # Create empty splits with proper schema if needed
            sample_record = {}
            if 'id' in config['columns'].get('order', []): sample_record['id'] = 0
            for column in config['columns'].get('order', []):
                if column not in sample_record: sample_record[column] = ""
            for col, value in config['columns'].get('add', {}).items():
                sample_record[col] = value
            
            for split in src_splits:
                if split not in processed_dataset or len(processed_dataset[split]) == 0:
                    log(f"Creating empty dataset for {split} split")
                    processed_dataset[split] = Dataset.from_pandas(pd.DataFrame([sample_record])).select([])
            
            standardized_dataset = standardize_schema(processed_dataset)
        else:
            standardized_dataset = standardize_schema(merged_dataset)
        
        # Filter to destination splits
        dest_splits = config.get('dest_splits')
        log(f"Filtering output to include only these splits: {', '.join(dest_splits)}")
        
        filtered_dataset = DatasetDict({
            split_name: standardized_dataset[split_name]
            for split_name in dest_splits
            if split_name in standardized_dataset
        })
        
        # Count records in filtered dataset
        filtered_records = sum(len(dataset) for dataset in filtered_dataset.values())
        telemetry["filtered_records"] = filtered_records
        
        # Log missing splits
        missing_splits = [s for s in dest_splits if s not in standardized_dataset]
        if missing_splits:
            log(f"Warning: Requested destination splits not found in dataset: {', '.join(missing_splits)}")
        
        log(f"Uploading {len(filtered_dataset)} splits to destination:")
        for split_name, dataset in filtered_dataset.items():
            log(f"- {split_name}: {len(dataset)} records")
        
        # Save all splits locally
        standardized_dataset.save_to_disk(os.path.join(dirs["merged_dir"], "all_splits"))
        log(f"Saved all splits locally to {os.path.join(dirs['merged_dir'], 'all_splits')}")
        
        # Push to HF with retries
        success = push_to_hub(filtered_dataset, config['dest_dataset'], config.get('hf_token'))
        telemetry["upload_success"] = success
        
        # Generate telemetry report
        report_telemetry(start_time, telemetry)
        
        if success:
            log("Dataset merge and upload completed successfully!")
        else:
            log("Dataset merge completed but upload failed.")
            filtered_dataset.save_to_disk(dirs["merged_dir"])
            log(f"Filtered data saved locally to {dirs['merged_dir']}")
            
    except Exception as e:
        log(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge datasets and push to HF")
    parser.add_argument("--config", default=DEFAULT_CONFIG_URL, help="Config URL")
    parser.add_argument("--log-dir", help="Log directory")
    parser.add_argument("--workers", type=int, help="Number of parallel workers for downloads")
    parser.add_argument("--output", default=os.getcwd(), help="Output directory for merged data")
    args = parser.parse_args()
    
    try:
        global console_logger, file_logger, config
        console_logger, file_logger = setup_loggers(args.log_dir or LOG_DIR)
        config = asyncio.run(fetch_config())
        if not config:
            log("Error: Failed to fetch or parse configuration")
            exit(1)
        config = validate_config(config)
        asyncio.run(main(args))
    except Exception as e:
        if 'console_logger' in globals():
            console_logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}")
        exit(1)