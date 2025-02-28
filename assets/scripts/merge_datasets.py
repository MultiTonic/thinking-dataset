import argparse, os, logging, time, requests, asyncio, json, hashlib, sys
import pandas as pd
from datasets import load_dataset, Dataset, DatasetDict
from datasets import config as datasets_config
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_random_exponential

LOG_DIR = "logs"
MAX_WORKERS = 4
CHUNK_SIZE = 50000

def log(message, console_output=True):
    try:
        file_logger.info(message)
        if console_output:
            try: console_logger.info(message)
            except UnicodeEncodeError: console_logger.info(message.encode('ascii', errors='replace').decode('ascii'))
    except Exception as e: print(f"[LOGGING ERROR] Failed to log message: {str(e)}")

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

def setup_directories(log_dir, output_dir=None):
    run_id = str(int(time.time()))
    log_dir = os.path.abspath(log_dir)
    
    if output_dir:
        data_dir = os.path.join(output_dir, "data")
    else:
        data_dir = os.path.join(os.getcwd(), "data")
        
    run_dir = os.path.join(data_dir, run_id)
    merged_dir = os.path.join(run_dir, "merged")
    cache_dir = os.path.join(run_dir, "cache")
    
    for directory in [log_dir, data_dir, run_dir, merged_dir, cache_dir]:
        os.makedirs(directory, exist_ok=True)
        
    datasets_config.HF_DATASETS_CACHE = cache_dir
    
    return {
        "run_id": run_id,
        "log_dir": log_dir,
        "data_dir": data_dir,
        "run_dir": run_dir,
        "merged_dir": merged_dir,
        "cache_dir": cache_dir
    }

def validate_config(config):
    if not config:
        raise ValueError("No configuration provided")
        
    required_keys = ['src_datasets', 'dest_dataset']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
        
    if 'private' not in config:
        config['private'] = False
        log("Dataset visibility set to Public (default)")
    
    if 'src_splits' not in config:
        config['src_splits'] = ['english', 'chinese']
        log(f"Using default source splits: {', '.join(config['src_splits'])}")
    else:
        log(f"Using specified source splits: {', '.join(config['src_splits'])}")
    
    if 'dest_splits' not in config:
        config['dest_splits'] = config['src_splits'].copy()
        log(f"Using source splits as destination splits")
    
    log(f"Config validated successfully")
    return config

def get_config_hash(config_data):
    config_str = json.dumps(config_data, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()

def report_telemetry(start_time, telemetry):
    elapsed_time = time.time() - start_time
    
    log("=== Telemetry Report ===")
    log(f"- Total runtime: {elapsed_time:.2f}s ({elapsed_time/60:.2f} min)")
    
    if "loaded_splits" in telemetry:
        log(f"- Loaded splits: {telemetry['loaded_splits']} successful, {telemetry.get('failed_splits', 0)} failed")
    
    if "total_records" in telemetry:
        log(f"- Total source records loaded: {telemetry['total_records']}")
    
    if "merged_records" in telemetry:
        log(f"- Records after merging: {telemetry['merged_records']}")
        
    if "deduped_records" in telemetry:
        log(f"- Records after deduplication: {telemetry['deduped_records']} ({telemetry.get('duplicates_removed', 0)} duplicates removed)")
    
    if "total_records_processed" in telemetry:
        log(f"- Records processed through column operations: {telemetry['total_records_processed']}")
    
    if "filtered_records" in telemetry:
        log(f"- Records after filtering to destination splits: {telemetry['filtered_records']}")

class ProcessingState:
    def __init__(self, config_hash, run_dir):
        self.config_hash = config_hash
        self.state_file = os.path.join(run_dir, "processing_state.json")
        self.state = {
            "config_hash": config_hash,
            "started_at": time.time(),
            "updated_at": time.time(),
            "downloads": {},
            "merges": {},
            "deduped": {},
            "processed_splits": {},
            "completed": False
        }
        self.load()
        
    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    loaded_state = json.load(f)
                    if loaded_state.get("config_hash") == self.config_hash:
                        self.state = loaded_state
                        log(f"Loaded processing state from {self.state_file}")
                        return True
                    else:
                        log(f"Config hash mismatch. Starting fresh processing state.")
            except Exception as e:
                log(f"Error loading processing state: {e}", False)
        return False
    
    def save(self):
        self.state["updated_at"] = time.time()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            return True
        except Exception as e:
            log(f"Error saving processing state: {e}", False)
            return False
            
    def mark_download_complete(self, source, split):
        if source not in self.state["downloads"]:
            self.state["downloads"][source] = {}
        self.state["downloads"][source][split] = {
            "completed_at": time.time(),
            "record_count": -1
        }
        self.save()
        
    def mark_download_records(self, source, split, record_count):
        if source not in self.state["downloads"]:
            self.state["downloads"][source] = {}
        if split in self.state["downloads"][source]:
            self.state["downloads"][source][split]["record_count"] = record_count
            self.save()
            
    def is_download_complete(self, source, split):
        return (source in self.state["downloads"] and 
                split in self.state["downloads"][source])
                
    def mark_merge_complete(self, split, record_count):
        self.state["merges"][split] = {
            "completed_at": time.time(),
            "record_count": record_count
        }
        self.save()
        
    def is_merge_complete(self, split):
        return split in self.state["merges"]
        
    def mark_dedup_complete(self, split, original_count, new_count):
        self.state["deduped"][split] = {
            "completed_at": time.time(),
            "original_count": original_count,
            "new_count": new_count,
            "duplicates_removed": original_count - new_count
        }
        self.save()
        
    def is_dedup_complete(self, split):
        return split in self.state["deduped"]
        
    def mark_processing_complete(self, split, record_count):
        self.state["processed_splits"][split] = {
            "completed_at": time.time(),
            "record_count": record_count
        }
        self.save()
        
    def is_processing_complete(self, split):
        return split in self.state["processed_splits"]
        
    def mark_all_complete(self):
        self.state["completed"] = True
        self.state["completed_at"] = time.time()
        self.save()
        
    def is_all_complete(self):
        return self.state.get("completed", False)

def clean_dataframe(df):
    index_cols = [col for col in df.columns if col.startswith('__index_level_')]
    if index_cols:
        df = df.drop(columns=index_cols)
    return df

def deduplicate_dataset_shard(dataset, dedup_columns, source, split):
    if not dedup_columns or len(dataset) == 0:
        return dataset, 0
    
    df = dataset.to_pandas()
    original_count = len(df)
    df = clean_dataframe(df)
    
    valid_dedup_cols = [col for col in dedup_columns if col in df.columns]
    
    if not valid_dedup_cols:
        log(f"No deduplication columns found in {source}/{split}, skipping deduplication")
        return dataset, 0
    
    log(f"Deduplicating {source}/{split} based on columns: {', '.join(valid_dedup_cols)}")
    deduped_df = df.drop_duplicates(subset=valid_dedup_cols)
    new_count = len(deduped_df)
    duplicates_removed = original_count - new_count
    
    if duplicates_removed > 0:
        percentage = (duplicates_removed / original_count) * 100
        log(f"Removed {duplicates_removed} duplicates ({percentage:.1f}%) from {source}/{split}")
        
        deduped_dataset = Dataset.from_pandas(deduped_df)
        return deduped_dataset, duplicates_removed
    
    return dataset, 0

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=0.1, max=3))
async def load_dataset_async(src, split, semaphore, state, dedup_columns=None):
    async with semaphore:
        try:
            if state.is_download_complete(src, split):
                log(f"Using cached download for {src}/{split}")
                with ThreadPoolExecutor() as pool:
                    dataset = await asyncio.get_event_loop().run_in_executor(
                        pool, lambda: load_dataset(src, split=split)
                    )
                state.mark_download_records(src, split, len(dataset))
                log(f"Loaded {len(dataset)} records from cached {src}/{split}")
                
                if dedup_columns:
                    original_count = len(dataset)
                    dataset, duplicates_removed = deduplicate_dataset_shard(dataset, dedup_columns, src, split)
                    if duplicates_removed > 0:
                        log(f"Deduplication complete for cached {src}/{split}: {len(dataset)} records remaining")
                        
                return dataset
            
            try:
                with ThreadPoolExecutor() as pool:
                    try:
                        dataset_info = await asyncio.get_event_loop().run_in_executor(
                            pool, lambda: load_dataset(src, split=None)
                        )
                        available_splits = dataset_info.keys() if dataset_info else []
                        if split not in available_splits:
                            log(f"Warning: Split '{split}' not found in dataset {src}. Available splits: {', '.join(available_splits)}")
                            return None
                    except Exception:
                        pass
                        
                    dataset = await asyncio.get_event_loop().run_in_executor(
                        pool, lambda: load_dataset(src, split=split, verification_mode="no_checks")
                    )
            except Exception as e:
                log(f"First download attempt for {src}/{split} failed, trying alternative method: {str(e)}")
                with ThreadPoolExecutor() as pool:
                    try:
                        dataset = await asyncio.get_event_loop().run_in_executor(
                            pool, lambda: load_dataset(src, split=split)
                        )
                    except Exception as e2:
                        log(f"Second download attempt failed: {str(e2)}, trying direct download")
                        try:
                            dataset = load_dataset(src, split=split)
                        except Exception as e3:
                            if "Split not found" in str(e3) or "Invalid split" in str(e3):
                                log(f"Split '{split}' not found in dataset {src}")
                                return None
                            raise
            
            duplicates_removed = 0
            original_count = len(dataset)
            if dedup_columns:
                dataset, duplicates_removed = deduplicate_dataset_shard(dataset, dedup_columns, src, split)
            
            log(f"Loaded {original_count} records from {src}/{split}" +
                (f" (removed {duplicates_removed} duplicates)" if duplicates_removed > 0 else ""))
            
            state.mark_download_complete(src, split)
            state.mark_download_records(src, split, len(dataset))
            
            return dataset
        except Exception as e:
            if "Split not found" in str(e) or "Invalid split" in str(e):
                log(f"Split '{split}' not found in dataset {src}")
                return None
            log(f"Warning: Could not load split {split} from {src}: {e}")
            raise

async def load_datasets(src_datasets, state, dedup_columns=None):
    datasets_dict = {}
    telemetry = {"loaded_splits": 0, "failed_splits": 0, "total_records": 0, "duplicates_removed": 0}
    
    worker_count = min(MAX_WORKERS, len(src_datasets) * 2)
    semaphore = asyncio.Semaphore(worker_count)
    
    log(f"Loading datasets with up to {worker_count} concurrent downloads...")
    
    available_splits_by_source = {}
    for src_idx, src in enumerate(src_datasets):
        try:
            with ThreadPoolExecutor() as pool:
                dataset_info = await asyncio.get_event_loop().run_in_executor(
                    pool, lambda: load_dataset(src, split=None)
                )
            available_splits = list(dataset_info.keys()) if dataset_info else []
            if available_splits:
                log(f"Found splits for {src}: {', '.join(available_splits)}")
                available_splits_by_source[src] = available_splits
            else:
                log(f"No splits found for {src}")
                available_splits_by_source[src] = []
        except Exception as e:
            log(f"Error discovering splits for {src}: {e}")
            available_splits_by_source[src] = []
    
    tasks = []
    for src_idx, src in enumerate(src_datasets):
        datasets_dict[src] = {}
        log(f"Preparing to load dataset from source {src_idx + 1}: {src}")
        
        splits_to_load = available_splits_by_source.get(src, [])
        
        if not splits_to_load:
            log(f"Warning: No splits found for source {src}")
            continue
            
        for split in splits_to_load:
            tasks.append((src, split, load_dataset_async(src, split, semaphore, state, dedup_columns)))
    
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
    
    if telemetry["failed_splits"] == len(src_datasets) * len(splits_to_load):
        error_msg = "All dataset splits failed to load. Cannot continue processing."
        log(f"CRITICAL ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    sources_with_data = []
    for src, splits_dict in datasets_dict.items():
        has_data = any(split_data is not None for split_data in splits_dict.values())
        if has_data:
            sources_with_data.append(src)
    
    if not sources_with_data:
        error_msg = "No data could be loaded from any source dataset. Cannot continue processing."
        log(f"CRITICAL ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    return datasets_dict, telemetry

def merge_datasets_chunked(datasets_dict, src_splits, state):
    merged = {}
    telemetry = {"merged_records": 0, "source_records": 0}
    
    for split in src_splits:
        if state.is_merge_complete(split):
            log(f"Skipping merge for {split} - already completed in previous run")
            
            try:
                merged_df = None
                record_count = 0
                
                for src, splits_dict in datasets_dict.items():
                    if split in splits_dict and splits_dict[split]:
                        try:
                            df = splits_dict[split].to_pandas()
                            source_records = len(df)
                            telemetry["source_records"] += source_records
                            df['source'] = src
                            
                            if merged_df is None:
                                merged_df = df
                            else:
                                merged_df = pd.concat([merged_df, df], ignore_index=True)
                                
                            record_count += source_records
                            log(f"Added {source_records} records from {src}/{split}, running total: {record_count}")
                            
                            del df
                            import gc
                            gc.collect()
                            
                        except Exception as e:
                            log(f"Error processing {src}/{split}: {e}")
                
                if merged_df is not None and record_count > 0:
                    merged[split] = Dataset.from_pandas(merged_df)
                    telemetry["merged_records"] += record_count
                    log(f"Created merged {split} split with {record_count} total records")
                    
                    del merged_df
                    import gc
                    gc.collect()
                else:
                    log(f"No data found for {split} split in any source dataset")
                    merged[split] = Dataset.from_dict({})
            except Exception as e:
                log(f"Error loading merged split {split} from cache: {e}")
                state.state["merges"].pop(split, None)
                state.save()
        
        if split not in merged:
            total_records = 0
            merged_df = None
            
            split_sizes = []
            for src, splits_dict in datasets_dict.items():
                if split in splits_dict and splits_dict[split]:
                    split_sizes.append((src, len(splits_dict[split])))
            
            log(f"Preparing to merge {split} split in chunks of {CHUNK_SIZE}")
            for src, size in split_sizes:
                log(f"  - {src}/{split}: {size} records")
            
            for src_idx, (src, splits_dict) in enumerate(datasets_dict.items()):
                if split in splits_dict and splits_dict[split]:
                    try:
                        dataset = splits_dict[split]
                        total_size = len(dataset)
                        telemetry["source_records"] += total_size
                        log(f"Processing source {src_idx+1}/{len(datasets_dict)}: {src}/{split} with {total_size} records")
                        
                        for start_idx in range(0, total_size, CHUNK_SIZE):
                            end_idx = min(start_idx + CHUNK_SIZE, total_size)
                            chunk = dataset.select(range(start_idx, end_idx))
                            df_chunk = chunk.to_pandas()
                            df_chunk['source'] = src
                            
                            if merged_df is None:
                                merged_df = df_chunk
                            else:
                                merged_df = pd.concat([merged_df, df_chunk], ignore_index=True)
                            
                            chunk_records = len(df_chunk)
                            total_records += chunk_records
                            log(f"Processed chunk from {src}/{split}: {chunk_records} records ({start_idx}-{end_idx}), running total: {total_records}")
                            
                            del chunk
                            del df_chunk
                            import gc
                            gc.collect()
                            
                            if total_records > 0 and total_records % (CHUNK_SIZE * 10) == 0:
                                log(f"Converting intermediate result to Dataset to optimize memory (records: {total_records})")
                                temp_dataset = Dataset.from_pandas(merged_df)
                                del merged_df
                                gc.collect()
                                merged_df = temp_dataset.to_pandas()
                                del temp_dataset
                                gc.collect()
                                
                    except Exception as e:
                        log(f"Error processing {src}/{split}: {e}")
            
            if merged_df is not None and total_records > 0:
                log(f"Creating dataset from merged dataframe with {total_records} records")
                merged_df = clean_dataframe(merged_df)
                merged[split] = Dataset.from_pandas(merged_df)
                telemetry["merged_records"] += total_records
                log(f"Created merged {split} split with {total_records} total records")
                
                state.mark_merge_complete(split, total_records)
                
                del merged_df
                import gc
                gc.collect()
            else:
                log(f"No data found for {split} split in any source dataset")
                merged[split] = Dataset.from_dict({})
                state.mark_merge_complete(split, 0)
    
    return DatasetDict(merged), telemetry

def apply_column_operations_chunked(dataset_dict, column_config, state):
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
        dataset_specific = column_config.get('dataset_specific', [])

        dataset_specific_ops = {}
        for ds_config in dataset_specific:
            if 'dataset' in ds_config:
                dataset_specific_ops[ds_config['dataset']] = ds_config

        generate_ids = id_config.get('generate', False)
        id_field = id_config.get('field', 'id')
        id_start = id_config.get('start', 1)
        id_increment = id_config.get('increment', 1)
        
        # Move the next_id counter outside the split processing loop to
        # ensure IDs are sequential across all splits
        next_id = id_start

        log(f"Column operations configuration:")
        if include_columns: log(f"- Including only: {include_columns}")
        if exclude_columns: log(f"- Excluding: {exclude_columns}")
        if rename_mapping: log(f"- Renaming: {rename_mapping}")
        if add_columns: log(f"- Adding: {add_columns}")
        if column_order: log(f"- Ordering: {column_order}")
        if generate_ids: log(f"- Generating IDs starting at {id_start} (unique across all splits)")
        if dataset_specific: log(f"- Dataset-specific operations for {len(dataset_specific)} datasets")
        
        # Get total record count for all splits to show in logging
        total_records = sum(len(dataset) for dataset in dataset_dict.values())
        log(f"Generating IDs for {total_records} records across {len(dataset_dict)} splits")

        # Process each split
        for split_name, split_dataset in dataset_dict.items():
            if state.is_processing_complete(split_name):
                log(f"Skipping processing for {split_name} - already completed in previous run")
                continue
 
            if len(split_dataset) == 0:
                result_dict[split_name] = split_dataset
                state.mark_processing_complete(split_name, 0)
                continue

            total_size = len(split_dataset)
            processed_chunks = []

            log(f"Processing {split_name} split in chunks of {CHUNK_SIZE}")
            for start_idx in range(0, total_size, CHUNK_SIZE):
                end_idx = min(start_idx + CHUNK_SIZE, total_size)
                chunk = split_dataset.select(range(start_idx, end_idx))

                df = chunk.to_pandas()

                if 'source' in df.columns and not df.empty:
                    log(f"Applying dataset-specific operations for {split_name} chunk {start_idx//CHUNK_SIZE + 1}")

                    unique_sources = df['source'].unique()
                    split_dfs = []

                    for source in unique_sources:
                        source_df = df[df['source'] == source].copy()
                        source_records = len(source_df)

                        if source in dataset_specific_ops:
                            ds_config = dataset_specific_ops[source]
                            log(f"- Processing {source_records} records from {source}")

                            ds_add_columns = ds_config.get('add', {})
                            if ds_add_columns:
                                for col_name, default_value in ds_add_columns.items():
                                    source_df[col_name] = default_value

                        split_dfs.append(source_df)

                    if split_dfs:
                        df = pd.concat(split_dfs, ignore_index=True)

                if generate_ids:
                    if id_field in df.columns: df = df.drop(columns=[id_field])
                    # Generate sequential IDs that continue from previous chunks and splits
                    df[id_field] = range(next_id, next_id + len(df) * id_increment, id_increment)
                    next_id = next_id + len(df) * id_increment

                # ...remaining code inside the chunk processing loop...
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
                            df[col_name] = default_value

                if rename_mapping:
                    renames_to_apply = {old: new for old, new in rename_mapping.items() if old in df.columns}
                    if renames_to_apply: df = df.rename(columns=renames_to_apply)

                if column_order:
                    existing_ordered_columns = [col for col in column_order if col in df.columns]
                    remaining_columns = [col for col in df.columns if col not in existing_ordered_columns]
                    df = df[existing_ordered_columns + remaining_columns]

                processed_chunks.append(df)
                log(f"Processed {split_name} chunk {start_idx//CHUNK_SIZE + 1}/{(total_size + CHUNK_SIZE - 1)//CHUNK_SIZE}: {len(df)} records")

                del df

            if processed_chunks:
                log(f"Combining {len(processed_chunks)} processed chunks for {split_name}")
                combined_df = pd.concat(processed_chunks, ignore_index=True)
                combined_df = clean_dataframe(combined_df)
                result_dict[split_name] = Dataset.from_pandas(combined_df)
                telemetry["processed_splits"] += 1
                telemetry["total_records_processed"] += len(combined_df)
                log(f"Processed {split_name} split: {len(combined_df)} records, {len(combined_df.columns)} columns")
                state.mark_processing_complete(split_name, len(combined_df))
                del combined_df
                del processed_chunks

        total_generated_ids = next_id - id_start
        if generate_ids: 
            log(f"Generated {total_generated_ids} unique IDs across all splits (range: {id_start}-{next_id-1})")
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
            df = clean_dataframe(df)

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
def push_to_hub(merged_dataset, destination, hf_token=None, config_data=None):
    try:
        log(f"Preparing to push merged dataset to {destination}")

        is_private = config_data.get('private', False) if config_data else False
        log(f"Dataset visibility: {'Private' if is_private else 'Public'}")

        start_time = time.time()
        push_kwargs = {
            'repo_id': destination,
            'private': is_private,
        }

        if hf_token:
            push_kwargs['token'] = hf_token
            
        merged_dataset.push_to_hub(**push_kwargs)
        
        upload_time = time.time() - start_time    
        log(f"Successfully pushed merged dataset to {destination} in {upload_time:.2f}s")
        
        for split, dataset in merged_dataset.items():
            log(f"- {split}: {len(dataset)} records")
        return True
    except Exception as e:
        error_str = str(e).lower()
        if "403 forbidden" in error_str or "don't have the rights" in error_str or "permissions" in error_str:
            log(f"CRITICAL ERROR: Authentication or permission error when pushing to hub:")
            log(f"- Error details: {str(e)}")
            log(f"- Destination: {destination}")
            log(f"- Using token: {'Yes' if hf_token else 'No'}")
            log(f"- Make sure your token has write access to '{destination.split('/')[0]}' organization")
            raise ValueError(f"Authentication error when pushing to {destination}. Check your permissions and token.")
        
        log(f"Error pushing to hub: {e}")
        raise

def deduplicate_dataset(dataset_dict, dedup_columns, state):
    if not dedup_columns:
        return dataset_dict, {}
        
    log(f"Deduplicating data based on columns: {', '.join(dedup_columns)}")
    result_dict = {}
    telemetry = {
        "original_records": 0,
        "deduped_records": 0,
        "duplicates_removed": 0
    }

    for split_name, dataset in dataset_dict.items():
        if state.is_dedup_complete(split_name):
            log(f"Skipping deduplication for {split_name} - already completed in previous run")
            result_dict[split_name] = dataset
            continue
            
        if len(dataset) == 0:
            log(f"Skipping deduplication for empty split: {split_name}")
            result_dict[split_name] = dataset
            state.mark_dedup_complete(split_name, 0, 0)
            continue
            
        try:
            log(f"Converting {split_name} to pandas for deduplication ({len(dataset)} records)")
            df = dataset.to_pandas()
            
            df = clean_dataframe(df)
            original_count = len(df)
            telemetry["original_records"] += original_count
            
            valid_dedup_cols = [col for col in dedup_columns if col in df.columns]
            if not valid_dedup_cols:
                log(f"Warning: None of the specified dedup columns {dedup_columns} found in {split_name}, skipping deduplication")
                result_dict[split_name] = dataset
                continue
                
            if len(valid_dedup_cols) < len(dedup_columns):
                log(f"Warning: Only using these columns for deduplication: {valid_dedup_cols}")
            
            log(f"Deduplicating {split_name} based on columns: {valid_dedup_cols}")
            deduped_df = df.drop_duplicates(subset=valid_dedup_cols)
            new_count = len(deduped_df)
            removed = original_count - new_count
            
            telemetry["deduped_records"] += new_count
            telemetry["duplicates_removed"] += removed
            
            log(f"Deduplication complete for {split_name}: {removed} duplicates removed ({removed/original_count*100:.1f}%)")
            result_dict[split_name] = Dataset.from_pandas(deduped_df)
            state.mark_dedup_complete(split_name, original_count, new_count)
            
            del df
            del deduped_df
            import gc
            gc.collect()
            
        except Exception as e:
            log(f"Error deduplicating {split_name}: {e}")
            result_dict[split_name] = dataset
    
    return DatasetDict(result_dict), telemetry

async def main(args, cfg):
    try:
        global dirs, MAX_WORKERS, state

        start_time = time.time()
        telemetry = {}
        config_data = validate_config(cfg)
        config_hash = get_config_hash(config_data)

        if args.workers:
            MAX_WORKERS = args.workers
        
        MAX_WORKERS = min(MAX_WORKERS, len(config_data['src_datasets']) * 2)
        log(f"Using {MAX_WORKERS} workers for concurrent operations")
        dirs = setup_directories(args.log_dir or LOG_DIR, args.output)
        state = ProcessingState(config_hash, dirs["run_dir"])
        
        if args.resume and state.is_all_complete():
            log(f"Processing already completed for this configuration. Use --force to reprocess.")
            if not args.force:
                log(f"Exiting without reprocessing. Use --force to override.")
                return
        
        log(f"Configuration: src={', '.join(config_data['src_datasets'])}, dest={config_data['dest_dataset']}")
        dedup_columns = config_data.get('dedup')

        if dedup_columns:
            log(f"Early deduplication enabled for columns: {', '.join(dedup_columns)}")
        
        src_splits = config_data.get('src_splits')
        log(f"Configured source splits: {', '.join(src_splits)}")
        datasets_dict, load_telemetry = await load_datasets(config_data['src_datasets'], state, dedup_columns)
        telemetry.update(load_telemetry)
        all_available_splits = []

        for _, splits_dict in datasets_dict.items():
            for split in splits_dict.keys():
                if split not in all_available_splits:
                    all_available_splits.append(split)
        
        log(f"All available splits from sources: {', '.join(all_available_splits)}")    
        merged_dataset, merge_telemetry = merge_datasets_chunked(datasets_dict, all_available_splits, state)
        telemetry.update(merge_telemetry)

        if dedup_columns:
            log(f"Running final deduplication check on merged datasets for columns: {', '.join(dedup_columns)}")
            deduped_dataset, dedup_telemetry = deduplicate_dataset(merged_dataset, dedup_columns, state)
            merged_dataset = deduped_dataset
            telemetry.update(dedup_telemetry)
            
            if dedup_telemetry.get("duplicates_removed", 0) > 0:
                log(f"Final deduplication removed {dedup_telemetry['duplicates_removed']} duplicates across different source datasets")
        
        total_merged_records = sum(len(dataset) for dataset in merged_dataset.values())

        if total_merged_records == 0:
            error_msg = "No records were found in any merged split. Cannot continue processing empty datasets."
            log(f"CRITICAL ERROR: {error_msg}")
            raise ValueError(error_msg)
        
        if 'columns' in config_data:
            processed_dataset, process_telemetry = apply_column_operations_chunked(merged_dataset, config_data['columns'], state)
            telemetry.update(process_telemetry)
            
            sample_record = {}

            if 'id' in config_data['columns'].get('order', []): sample_record['id'] = 0

            for column in config_data['columns'].get('order', []):
                if column not in sample_record: sample_record[column] = ""
            
            for col, value in config_data['columns'].get('add', {}).items():
                sample_record[col] = value
            
            for split in src_splits:
                if split not in processed_dataset or len(processed_dataset[split]) == 0:
                    log(f"Creating empty dataset for {split} split")
                    processed_dataset[split] = Dataset.from_pandas(pd.DataFrame([sample_record])).select([])
            
            standardized_dataset = standardize_schema(processed_dataset)
        else:
            standardized_dataset = standardize_schema(merged_dataset)
        
        dest_splits = config_data.get('dest_splits')
        log(f"Filtering output to include only these splits: {', '.join(dest_splits)}")
        filtered_dataset = DatasetDict({
            split_name: standardized_dataset[split_name]
            for split_name in dest_splits
            if split_name in standardized_dataset
        })
        filtered_records = sum(len(dataset) for dataset in filtered_dataset.values())
        telemetry["filtered_records"] = filtered_records
        
        if filtered_records == 0:
            log(f"WARNING: All destination splits contain 0 records. Dataset will be empty.")
        
        missing_splits = [s for s in dest_splits if s not in standardized_dataset]

        if missing_splits:
            log(f"Warning: Requested destination splits not found in dataset: {', '.join(missing_splits)}")

        log(f"Uploading {len(filtered_dataset)} splits to destination:")

        for split_name, dataset in filtered_dataset.items():
            log(f"- {split_name}: {len(dataset)} records")

        standardized_dataset.save_to_disk(os.path.join(dirs["merged_dir"], "all_splits"))
        log(f"Saved all splits locally to {os.path.join(dirs['merged_dir'], 'all_splits')}")
        
        if not args.skip_upload:
            success = push_to_hub(filtered_dataset, config_data['dest_dataset'], config_data.get('hf_token'), config_data)
            telemetry["upload_success"] = success
            
            state.mark_all_complete()
            report_telemetry(start_time, telemetry)
            
            if success:
                log("Dataset merge and upload completed successfully!")
                log(f"Dataset available at: {config_data['dest_dataset']}")
            else:
                log("Dataset merge completed but upload failed.")
                filtered_dataset.save_to_disk(dirs["merged_dir"])
                log(f"Filtered data saved locally to {dirs['merged_dir']}")
        else:
            log("Skipping upload to HuggingFace Hub as requested")
            log(f"Dataset saved locally to {os.path.join(dirs['merged_dir'], 'all_splits')}")
            
    except Exception as e:
        log(f"Error in main process: {e}")
        raise

if __name__ == "__main__":

    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'

    parser = argparse.ArgumentParser(description="Merge datasets and push to HF")
    parser.add_argument("--config", required=True, help="Config URL")
    parser.add_argument("--log-dir", help="Log directory")
    parser.add_argument("--workers", type=int, help="Number of parallel workers for downloads")
    parser.add_argument("--output", default=os.getcwd(), help="Output directory for merged data")
    parser.add_argument("--resume", action="store_true", help="Resume processing from last saved state")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if already completed")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Chunk size for processing large datasets")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to HuggingFace Hub")
    args = parser.parse_args()

    if args.chunk_size:
        CHUNK_SIZE = args.chunk_size
    
    config_url = args.config

    try:
        global console_logger, file_logger, state
        console_logger, file_logger = setup_loggers(args.log_dir or os.path.join(os.getcwd(), "logs"))
        
        log(f"Fetching config from: {config_url}")
        response = requests.get(config_url)

        if response.status_code == 200:
            cfg = response.json()
            log("Config fetched successfully")
        else:
            log(f"Error: Failed to fetch config, status code: {response.status_code}")
            exit(1)
            
        if not cfg:
            log("Error: Failed to parse configuration")
            exit(1)

        asyncio.run(main(args, cfg))
    except ValueError as e:

        if 'console_logger' in globals():
            console_logger.error(f"Process stopped: {e}")
        else:
            print(f"Process stopped: {e}")
        exit(1)
    except Exception as e:

        if 'console_logger' in globals():
            console_logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}")
        exit(1)