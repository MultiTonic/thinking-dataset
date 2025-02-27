import argparse as ap, os, asyncio, logging, time, requests, random, json
from openai import AsyncOpenAI
from tenacity import retry, wait_random, stop_after_attempt, retry_if_exception
from asyncio import TimeoutError
from datasets import load_dataset, Dataset, DatasetDict
from functools import lru_cache

DEFAULT_CONFIG_URL = "https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw"
MAX_WORKERS = 10
MAX_RETRIES = 3
MAX_RETRY_DELAY = 0.3
API_BASE_URL = "api.scaleway.ai"
REQUEST_COUNTER = 0
ENDPOINT_COOLDOWN = 120
CHECKPOINT_INTERVAL = 100
REQUEST_TIMEOUT = 300
TEST_TIMEOUT = 30

def log(message: str, console_output: bool = True) -> None:
    try:
        file_logger.info(message)
        if (console_output):
            try:
                console_logger.info(message)
            except UnicodeEncodeError:
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                console_logger.info(safe_message)
    except Exception as e:
        try:
            print(f"[LOGGING ERROR] Failed to log message: {str(e)}")
        except:
            pass

def setup_loggers(log_path: str) -> tuple[logging.Logger, logging.Logger]:
    os.makedirs(log_path, exist_ok=True)
    console_logger, file_logger = logging.getLogger("console"), logging.getLogger("file")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    console_logger.addHandler(console_handler)
    console_logger.setLevel(logging.INFO)
    console_logger.propagate = False
    log_file = os.path.join(log_path, f"cs_{int(time.time())}.log")
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
            required_keys = ['endpoints', 'model', 'src', 'dest', 'systems', 'prompts']
            missing_keys = [key for key in required_keys if key not in config_json]
            if missing_keys:
                log(f"Warning: Config is missing some required keys: {', '.join(missing_keys)}", True)
            if 'systems' in config_json:
                if not all(lang in config_json['systems'] for lang in ['en', 'zh']):
                    log("Warning: Config is missing system prompts for 'en' or 'zh'", True)
            if 'prompts' in config_json:
                if not all(lang in config_json['prompts'] for lang in ['en', 'zh']):
                    log("Warning: Config is missing prompt templates for 'en' or 'zh'", True)
            if 'endpoints' in config_json and isinstance(config_json['endpoints'], list):
                valid_endpoints = []
                for idx, endpoint in enumerate(config_json['endpoints']):
                    if not all(key in endpoint for key in ['p', 'u', 'k']):
                        log(f"Warning: Endpoint {idx+1} is missing required keys", False)
                    else:
                        valid_endpoints.append(endpoint)
                if len(valid_endpoints) == 0:
                    log("Error: No valid endpoints found in config", True)
                elif len(valid_endpoints) < len(config_json['endpoints']):
                    log(f"Warning: Only {len(valid_endpoints)} of {len(config_json['endpoints'])} endpoints are valid", True)
                    config_json['endpoints'] = valid_endpoints
            else:
                log("Error: 'endpoints' key is missing or not a list", True)
            return config_json
        log(f"Failed to fetch config: {response.status_code}", False)
        return None
    except Exception as e:
        log(f"Error fetching config: {e}", False)
        return None

def init_endpoints(endpoints_config):
    endpoints = []
    for endpoint in endpoints_config:
        endpoints.append({
            **endpoint,
            'last_call': 0,
            'in_use': False
        })
    random.shuffle(endpoints)
    return endpoints

def get_next_endpoint(endpoints):
    now = time.time()
    available_endpoints = []
    for i, endpoint in enumerate(endpoints):
        if not endpoint['in_use'] and now - endpoint['last_call'] >= ENDPOINT_COOLDOWN:
            available_endpoints.append((i, endpoint))
    if not available_endpoints:
        soonest_ready = min(endpoints, key=lambda e: e['last_call'] + ENDPOINT_COOLDOWN if not e['in_use'] else float('inf'))
        idx = endpoints.index(soonest_ready)
        wait_time = max(0, (soonest_ready['last_call'] + ENDPOINT_COOLDOWN) - now)
        if wait_time > 0:
            log(f"All endpoints busy or cooling down, will wait {wait_time:.2f}s for next available")
            time.sleep(wait_time)
        return idx
    available_endpoints.sort(key=lambda x: x[1]['last_call'])
    return available_endpoints[0][0]

class ResponseTooShortError(Exception):
    def __init__(self, actual_length, min_length):
        self.actual_length = actual_length
        self.min_length = min_length
        self.message = f"Response length {actual_length} is shorter than minimum required length {min_length}"
        super().__init__(self.message)

def check_min_length(response_text: str, min_length: int):
    if min_length and len(response_text) < min_length:
        raise ResponseTooShortError(len(response_text), min_length)
    return True

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_random(min=1, max=5), reraise=True)
async def test_endpoint(endpoint_config, semaphore):
    async with semaphore:
        try:
            start_time = time.time()
            provider = endpoint_config.get('p', 'unknown')
            name = endpoint_config.get('n', 'unknown')
            async with AsyncOpenAI(
                base_url=f"https://{API_BASE_URL}/{endpoint_config['u']}/v1",
                api_key=endpoint_config['k']
            ) as client:
                try:
                    async with asyncio.timeout(TEST_TIMEOUT):
                        response = await client.chat.completions.create(
                            model=config.get('model', 'deepseek-r1-distill-llama-70b'),
                            messages=[
                                {"role": "system", "content": "Test message"},
                                {"role": "user", "content": "Respond with 'OK' if you can read this."}
                            ],
                            max_tokens=10,
                            temperature=0
                        )
                except TimeoutError:
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: {TEST_TIMEOUT}s (Timeout)")
                    return provider, name, TEST_TIMEOUT, None
                except Exception as e:
                    err_msg = str(e)
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: API Error - {err_msg}")
                    if "429" in err_msg or "TOO MANY TOKENS" in err_msg or "rate limit" in err_msg.lower():
                        log(f"Rate limit detected for endpoint {provider}-{name}, considering it valid but busy")
                        await asyncio.sleep(2)
                        return provider, name, 0.1, "RATE_LIMITED"
                    raise
                    
                elapsed_time = round(time.time() - start_time, 2)
                if response and response.choices and response.choices[0].message:
                    file_logger.info(f"Endpoint OK: {provider}-{name}: {elapsed_time}s")
                    return provider, name, elapsed_time, response.choices[0].message.content
                file_logger.info(f"Endpoint Fail: {provider}-{name}: {elapsed_time}s (No Response)")
                return provider, name, elapsed_time, None
        except Exception as e:
            file_logger.info(f"Endpoint Fail: {provider}-{name}: {str(e)}")
            raise

async def load_source_dataset(offset=0, max_records=0):
    try:
        source = config.get('src')
        if not source:
            raise ValueError("No source dataset in config")
        full_dataset = load_dataset(source, split="english")
        total_records = len(full_dataset)
        if offset > 0 or max_records > 0:
            if offset >= total_records:
                log(f"Error: Offset {offset} exceeds dataset size {total_records}")
                return None
            end_idx = total_records if max_records == 0 else min(offset + max_records, total_records)
            dataset = full_dataset.select(range(offset, end_idx))
            log(f"Using dataset slice: source records {offset} to {end_idx-1} (out of {total_records} total)")
        else:
            dataset = full_dataset
            log(f"Using complete dataset: {total_records} source records")
        selected_records = len(dataset)
        total_stakeholders = sum(
            len(record.get('stakeholders', {}).get('stakeholder', []))
            for record in dataset
        )
        log(f"Dataset loaded successfully:")
        log(f"- source: {source}")
        log(f"- total source records: {total_records}")
        log(f"- selected source records: {selected_records}")
        log(f"- total stakeholders across selected records: {total_stakeholders}")
        log(f"- total case studies needed: {total_stakeholders * 2} (English + Chinese for each stakeholder)")
        log(f"- average stakeholders per source record: {total_stakeholders/selected_records:.2f}")
        return dataset
    except Exception as e:
        log(f"Error loading dataset '{config.get('src')}': {e}", False)
        return None

def should_retry_on_too_short(exception):
    return isinstance(exception, ResponseTooShortError) or retry_if_exception(exception)

# Add a global stats tracker
class TelemetryStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.processed_files = set()  # Track unique files we've processed

    def log_success(self, language, case_study_idx):
        self.total_attempts += 1
        
        # Only count each file once using a set to track unique IDs
        unique_id = f"{language}_{case_study_idx}"
        if unique_id not in self.processed_files:
            self.successful_generations += 1
            self.processed_files.add(unique_id)
        
    def log_failure(self, language, error_type):
        self.total_attempts += 1
        self.failed_generations += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def reset_stats(self, expected_total):
        """Reset stats at the beginning of a new processing run"""
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.processed_files = set()
    
    def get_telemetry_string(self, total_needed):
        elapsed = time.time() - self.start_time
        remaining = total_needed - self.successful_generations
        rpm = (self.total_attempts / elapsed * 60) if elapsed > 0 else 0
        error_rate = (self.failed_generations / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        # Estimate remaining time
        if rpm > 0:
            est_minutes = remaining / (rpm * (1 - error_rate/100))
            time_remaining = f"{est_minutes:.1f} min" if est_minutes < 60 else f"{est_minutes/60:.1f} hours"
        else:
            time_remaining = "unknown"
            
        return (f"TELEMETRY: {self.successful_generations}/{total_needed} complete ({self.successful_generations/total_needed*100:.1f}%) • "
                f"{remaining} remaining • {rpm:.1f} req/min • "
                f"{error_rate:.1f}% errors • Est. remaining: {time_remaining}")

# Create global stats tracker
telemetry_stats = TelemetryStats()

# Modify retry conditions to only retry on rate limit errors, not for other exceptions
def should_retry(exception):
    if isinstance(exception, ResponseTooShortError):
        return True
    
    # Only retry for rate limit related errors (429)
    if isinstance(exception, Exception) and ("429" in str(exception) or 
                                           "TOO MANY TOKENS" in str(exception) or 
                                           "rate limit" in str(exception).lower()):
        return True
    return False

@retry(stop=stop_after_attempt(MAX_RETRIES), 
       wait=wait_random(min=0.1, max=MAX_RETRY_DELAY), 
       retry=should_retry,  # Use our specific retry condition
       reraise=True)
async def generate_case_study(prompt, system_prompt, endpoint_idx, language, case_study_idx, source_record_idx, stakeholder_idx, stakeholder_name):
    global endpoints, telemetry_stats
    try:
        start_time = time.time()
        endpoint_config = endpoints[endpoint_idx]
        endpoint_config['in_use'] = True
        provider = endpoint_config.get('p', 'unknown')
        name = endpoint_config.get('n', 'unknown')
        language_name = "English" if language == 'en' else "Chinese"
        min_length = config.get('min_length', 0)
        
        # Log with source record and stakeholder info
        log(f"Generating {language_name} case study #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1} ({stakeholder_name}) using {provider}-{name}")
        
        async with AsyncOpenAI(
            base_url=f"https://{API_BASE_URL}/{endpoint_config['u']}/v1",
            api_key=endpoint_config['k']
        ) as client:
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    response = await client.chat.completions.create(
                        model=config.get('model', 'deepseek-r1-distill-llama-70b'),
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=config.get('max_tokens', 4096),
                        temperature=config.get('temperature', 0.7),
                        top_p=0.95,
                        presence_penalty=0
                    )
            except TimeoutError:
                file_logger.info(f"Case Study Fail: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: Timeout after {REQUEST_TIMEOUT}s")
                endpoint_config['last_call'] = time.time()
                endpoint_config['in_use'] = False
                telemetry_stats.log_failure(language, "timeout")
                return "", REQUEST_TIMEOUT
            except Exception as e:
                err_msg = str(e)
                file_logger.info(f"Case Study Fail: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: API Error - {err_msg}")
                endpoint_config['last_call'] = time.time()
                endpoint_config['in_use'] = False
                if "429" in err_msg or "TOO MANY TOKENS" in err_msg:
                    log(f"Rate limit hit for endpoint {provider}-{name}, backing off...")
                    await asyncio.sleep(10)
                telemetry_stats.log_failure(language, type(e).__name__)
                raise
                
            elapsed_time = round(time.time() - start_time, 2)
            if response and response.choices and response.choices[0].message:
                result = response.choices[0].message.content
                if min_length > 0 and len(result) < min_length:
                    log(f"Response too short for {language_name} case study #{case_study_idx}: {len(result)}/{min_length} characters")
                    endpoint_config['last_call'] = time.time()
                    endpoint_config['in_use'] = False
                    telemetry_stats.log_failure(language, "TooShort")
                    raise ResponseTooShortError(len(result), min_length)
                    
                file_logger.info(f"Case Study OK: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {elapsed_time}s - {len(result)} chars")
                temp_dir = os.path.join(dirs["temp_dir"], language)
                os.makedirs(temp_dir, exist_ok=True)
                filepath = os.path.join(temp_dir, f"{case_study_idx:06d}.txt")
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result)
                    log(f"Saved {language_name} case study #{case_study_idx} to {filepath}")
                    
                    # Don't increment telemetry counter here - we'll do it in process_case_study
                    if time.time() - telemetry_stats.last_log_time > 30:  # Log telemetry every 30 seconds
                        if 'total_case_studies' in globals():
                            total_needed = total_case_studies
                        else:
                            total_needed = 0
                        log(telemetry_stats.get_telemetry_string(total_needed))
                        telemetry_stats.last_log_time = time.time()
                        
                except Exception as e:
                    log(f"Error saving case study #{case_study_idx} to file: {str(e)}", False)
                    telemetry_stats.log_failure(language, "FileSaveError")
                    
                endpoint_config['last_call'] = time.time()
                endpoint_config['in_use'] = False
                return result, elapsed_time
                
            file_logger.info(f"Case Study Fail: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {elapsed_time}s (No Response)")
            endpoint_config['last_call'] = time.time()
            endpoint_config['in_use'] = False
            telemetry_stats.log_failure(language, "EmptyResponse")
            return "", elapsed_time
    except ResponseTooShortError as e:
        file_logger.info(f"Case Study too short: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {e.message}")
        telemetry_stats.log_failure(language, "TooShort")
        raise
    except Exception as e:
        file_logger.info(f"Case Study Fail: {language_name} #{case_study_idx} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {str(e)}")
        telemetry_stats.log_failure(language, type(e).__name__)
        elapsed_time = round(time.time() - start_time, 3) if 'start_time' in locals() else 0.0
        if 'endpoint_config' in locals():
            endpoint_config['last_call'] = time.time()
            endpoint_config['in_use'] = False
        raise

def format_endpoint(config):
    if not config:
        return "unknown"
    provider = config.get('p', 'unknown')
    uuid = config.get('u', '')
    name = config.get('n', '')
    if uuid and name:
        return f"{provider}-{uuid}-{name}"
    elif uuid:
        return f"{provider}-{uuid}"
    elif name:
        return f"{provider}-{name}"
    else:
        return provider

async def save_metadata(processed_count: int, checkpoint_interval: int, total_records: int, destination: str):
    try:
        metadata = {
            "last_update_time": time.time(),
            "processed_count": processed_count,
            "total_records": total_records,
            "checkpoint_interval": checkpoint_interval,
            "destination": destination,
            "source": config.get("src", ""),
            "run_id": dirs["run_id"],
            "current_batch": processed_count // checkpoint_interval if checkpoint_interval > 0 else 0,
        }
        metadata_path = os.path.join(dirs["run_dir"], "processing_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        log(f"Saved processing metadata (processed {processed_count}/{total_records} records)")
        return True
    except Exception as e:
        log(f"Warning: Failed to save metadata: {str(e)}", False)
        return False

async def load_metadata():
    try:
        metadata_path = os.path.join(dirs["run_dir"], "processing_metadata.json")
        if not os.path.exists(metadata_path):
            return None
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        last_update = time.strftime('%Y-%m-%d %H:%M:%S', 
                                   time.localtime(metadata.get("last_update_time", 0)))
        log(f"Found existing processing metadata from {last_update}")
        log(f"- Previously processed: {metadata.get('processed_count', 0)}/{metadata.get('total_records', 0)} records")
        log(f"- Previous destination: {metadata.get('destination', 'unknown')}")
        return metadata
    except Exception as e:
        log(f"Warning: Failed to load metadata: {str(e)}", False)
        return None

async def clear_metadata():
    try:
        metadata_path = os.path.join(dirs["run_dir"], "processing_metadata.json")
        if (os.path.exists(metadata_path)):
            os.remove(metadata_path)
            log("Cleared processing metadata")
        return True
    except Exception as e:
        log(f"Warning: Failed to clear metadata: {str(e)}", False)
        return False

async def save_intermediate_results_unified(successful_records, failed_records, batch_idx, destination):
    """Save intermediate results with unified record schema."""
    try:
        # Split by language
        english_records = [r for r in successful_records if r["language"] == "english"]
        chinese_records = [r for r in successful_records if r["language"] == "chinese"]
        english_failed = [r for r in failed_records if r["language"] == "english"]
        chinese_failed = [r for r in failed_records if r["language"] == "chinese"]
        
        # Create empty record template for schema consistency
        empty_record = {
            "id": 0,
            "case_study_info": "",
            "prompt": "",
            "original_info": "",
            "stakeholder": "",
            "motivation": "",
            "elapsed_time": 0.0,
            "endpoint": "",
            "language": ""
        }
        
        # Create datasets with consistent schema
        dataset_splits = {
            'english': Dataset.from_list(english_records) if english_records else Dataset.from_list([empty_record]).select([]),
            'chinese': Dataset.from_list(chinese_records) if chinese_records else Dataset.from_list([empty_record]).select([])
        }
        
        if english_failed:
            dataset_splits['english_failed'] = Dataset.from_list(english_failed)
        if chinese_failed:
            dataset_splits['chinese_failed'] = Dataset.from_list(chinese_failed)
            
        dataset_dict = DatasetDict(dataset_splits)
        save_path = os.path.join(dirs["checkpoints_dir"], f"checkpoint_{batch_idx}")
        dataset_dict.save_to_disk(save_path)
        log(f"Saved checkpoint to {save_path}")
        
        case_studies_path = os.path.join(dirs["case_studies_dir"], "latest")
        dataset_dict.save_to_disk(case_studies_path)
        log(f"Updated latest case studies at {case_studies_path}")
        
        hf_token = config.get('hf_token')
        if hf_token:
            try:
                dataset_dict.push_to_hub(destination, token=hf_token, private=True)
                log(f"Updated destination dataset with progress: {destination}")
            except Exception as e:
                log(f"Could not update HF dataset, but local checkpoint saved: {str(e)}")
                
        successful_count = len(english_records) + len(chinese_records)
        failed_count = len(english_failed) + len(chinese_failed)
        log(f"Checkpoint saved: {successful_count} successful, {failed_count} failed case studies")
        
        return True
    except Exception as e:
        log(f"Error saving intermediate results: {str(e)}")
        return False

async def upload_results(prepared_records: list, destination: str, checkpoint_interval: int) -> bool:
    # Define global variable for telemetry
    global total_case_studies
    total_case_studies = len(prepared_records) * 2  # English + Chinese for each stakeholder
    
    # Reset telemetry stats at the start of processing
    telemetry_stats.reset_stats(total_case_studies)
    
    try:
        # Create a unified record structure with language field
        all_records = []
        successful_records = []
        failed_records = []
        
        resume_from = 0
        metadata = await load_metadata()
        if metadata and args.resume:
            if metadata.get("destination") == destination:
                resume_from = metadata.get("processed_count", 0)
                log(f"Resuming from case study {resume_from} (out of {len(prepared_records)*2} potential case studies)")
            else:
                log(f"Warning: Found metadata but destination mismatch. Starting from beginning.")
                
        en_temp_dir = os.path.join(dirs["temp_dir"], "en")
        zh_temp_dir = os.path.join(dirs["temp_dir"], "zh")
        os.makedirs(en_temp_dir, exist_ok=True)
        os.makedirs(zh_temp_dir, exist_ok=True)
        
        def process_record(record, language, add_id=True):
            # Standardize record format - same schema for all
            result = {
                "case_study_info": record.get("case_study_info", ""),
                "prompt": record.get("prompt", ""),
                "original_info": record.get("original_info", ""),
                "stakeholder": record.get("stakeholder", ""),
                "motivation": record.get("motivation", ""),
                "elapsed_time": record.get("elapsed_time", 0.0),
                "endpoint": record.get("endpoint", ""),
                "language": language  # Add language field for easier sorting
            }
            if add_id:
                result["id"] = len(all_records) + 1
            return result
        
        async def process_case_study(record, language, idx, total, semaphore):
            async with semaphore:
                language_key = 'en' if language == 'english' else 'zh'
                error_key = f"{language_key}_error"
                language_name = "English" if language == 'english' else "Chinese"
                system_prompt = config['systems'].get(language_key, "")
                
                # Extract source record info
                source_record_idx = record.get('original_idx', -1)
                stakeholder_idx = record.get('stakeholder_idx', -1)
                stakeholder_name = record.get('stakeholder', 'Unknown')
                case_study_idx = idx
                
                if not system_prompt:
                    error_msg = f"Missing system prompt for {language_name}"
                    log(f"Error: {error_msg}")
                    failed_record = process_record({
                        "original_info": record['case_study_info'],
                        "stakeholder": record.get('stakeholder', ''),
                        "motivation": record.get('motivation', ''),
                        "endpoint": f"error - {error_msg}"
                    }, language)
                    failed_records.append(failed_record)
                    return False
                
                if 'prompts' in record and language_key in record['prompts'] and record['prompts'][language_key]:
                    try:
                        endpoint_idx = get_next_endpoint(endpoints)
                        endpoint_config = endpoints[endpoint_idx]
                        endpoint_formatted = format_endpoint(endpoint_config)
                        
                        # Try just once to generate - no more retrying except for rate limits
                        try:
                            case_study_info, elapsed_time = await generate_case_study(
                                record['prompts'][language_key], 
                                system_prompt,
                                endpoint_idx,
                                language_key,
                                case_study_idx,
                                source_record_idx,
                                stakeholder_idx,
                                stakeholder_name
                            )
                            
                            # If successful generation
                            has_content = bool(case_study_info and case_study_info.strip())
                            if has_content:
                                result_record = process_record({
                                    "case_study_info": case_study_info,
                                    "original_info": record['case_study_info'],
                                    "prompt": record['prompts'][language_key],
                                    "stakeholder": record.get('stakeholder', ''),
                                    "motivation": record.get('motivation', ''),
                                    "elapsed_time": elapsed_time,
                                    "endpoint": endpoint_formatted
                                }, language)
                                
                                successful_records.append(result_record)
                                all_records.append(result_record)
                                
                                # Now increment telemetry counter only once per file
                                telemetry_stats.log_success(language_key, case_study_idx)
                                
                                log(f"Completed {language_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1} ({stakeholder_name}) - {elapsed_time:.2f}s")
                                
                                # Log telemetry after each completion
                                log(telemetry_stats.get_telemetry_string(total_case_studies))
                                
                                return True
                            else:
                                # Empty result should be counted as failure
                                raise ValueError("Empty result returned")
                                
                        except Exception as e:
                            # Try to recover from temp file if it exists
                            temp_dir = os.path.join(dirs["temp_dir"], language_key)
                            filepath = os.path.join(temp_dir, f"{case_study_idx:06d}.txt")
                            if os.path.exists(filepath):
                                # Found a saved file! Let's consider this a success
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        recovered_content = f.read()
                                    
                                    if recovered_content and len(recovered_content) > 100:  # Sanity check for valid content
                                        log(f"Recovered file for {language_name} case study {idx} despite error: {str(e)}")
                                        
                                        result_record = process_record({
                                            "case_study_info": recovered_content,
                                            "original_info": record['case_study_info'],
                                            "prompt": record['prompts'][language_key],
                                            "stakeholder": record.get('stakeholder', ''),
                                            "motivation": record.get('motivation', ''),
                                            "elapsed_time": 0.0,  # We don't know the real time
                                            "endpoint": endpoint_formatted + "-recovered"
                                        }, language)
                                        
                                        successful_records.append(result_record)
                                        all_records.append(result_record)
                                        
                                        # Increment telemetry for recovered files too - but only once
                                        telemetry_stats.log_success(language_key, case_study_idx)
                                        
                                        log(f"Successfully recovered {language_name} case study {idx} from saved file")
                                        return True
                                except Exception as recovery_error:
                                    log(f"Failed to recover from temp file: {str(recovery_error)}")
                            
                            # No recovery possible, treat as failure
                            error_msg = str(e)
                            log(f"Error generating {language_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {error_msg}")
                            file_logger.error(f"Generation error for {language}: {error_msg}")
                            
                            failed_record = process_record({
                                "original_info": record['case_study_info'],
                                "prompt": record['prompts'][language_key],
                                "stakeholder": record.get('stakeholder', ''),
                                "motivation": record.get('motivation', ''),
                                "endpoint": f"error - {error_msg}"
                            }, language)
                            failed_records.append(failed_record)
                            all_records.append(failed_record)
                            telemetry_stats.log_failure(language_key, type(e).__name__)
                            return False
                    except Exception as e:
                        error_msg = str(e)
                        log(f"Error generating {language_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {error_msg}")
                        file_logger.error(f"Generation error for {language}: {error_msg}")
                        
                        failed_record = process_record({
                            "original_info": record['case_study_info'],
                            "prompt": record['prompts'][language_key],
                            "stakeholder": record.get('stakeholder', ''),
                            "motivation": record.get('motivation', ''),
                            "endpoint": f"error - {error_msg}"
                        }, language)
                        failed_records.append(failed_record)
                        all_records.append(failed_record)
                        telemetry_stats.log_failure(language_key, type(e).__name__)
                        return False
                else:
                    error_msg = record.get(error_key, f"Failed to generate {language} prompt")
                    log(f"Missing prompt for case study {idx}/{total} - {language_name}: {error_msg}")
                    
                    failed_record = process_record({
                        "original_info": record['case_study_info'],
                        "stakeholder": record.get('stakeholder', ''),
                        "motivation": record.get('motivation', ''),
                        "endpoint": f"error - {error_msg}"
                    }, language)
                    failed_records.append(failed_record)
                    all_records.append(failed_record)
                    return False
                    
        total_case_studies = len(prepared_records) * 2  # English + Chinese for each stakeholder
        log(f"Starting to generate {total_case_studies} case studies ({len(prepared_records)} stakeholders × 2 languages)")
        
        start_idx = resume_from
        records_to_process = prepared_records[start_idx:]
        semaphore = asyncio.Semaphore(dirs["workers"])
        log(f"Using semaphore with {dirs['workers']} workers for concurrent processing")
        
        total_successful_case_studies = 0
        case_study_counter = 0
        
        # Process all batches without checkpointing between batches
        for batch_start in range(0, len(records_to_process), dirs["workers"]):
            batch_end = min(batch_start + dirs["workers"], len(records_to_process))
            batch = records_to_process[batch_start:batch_end]
            batch_size = len(batch)
            log(f"Processing batch of {batch_size} stakeholders ({batch_start+start_idx+1} to {batch_end+start_idx} out of {len(prepared_records)})")
            
            tasks = []
            for i, record in enumerate(batch):
                idx = batch_start + start_idx + i
                case_study_counter += 1
                tasks.append(process_case_study(record, 'english', case_study_counter, total_case_studies, semaphore))
                
                case_study_counter += 1
                tasks.append(process_case_study(record, 'chinese', case_study_counter, total_case_studies, semaphore))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    record_idx = batch_start + start_idx + (i // 2)
                    language = 'english' if i % 2 == 0 else 'chinese'
                    record = batch[i // 2]
                    source_record_idx = record.get('original_idx', -1)
                    stakeholder_idx = record.get('stakeholder_idx', -1)
                    log(f"Error in batch processing - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1} ({language}): {str(result)}")
            
            current_stakeholder_idx = batch_end + start_idx
            successful_case_studies_count = len(successful_records)
            total_successful_case_studies = successful_case_studies_count
            
            log(f"Progress: {current_stakeholder_idx}/{len(prepared_records)} stakeholders processed ({current_stakeholder_idx/len(prepared_records)*100:.1f}%)")
            log(f"- Successful case studies: {successful_case_studies_count}/{case_study_counter} ({successful_case_studies_count/case_study_counter*100:.1f}%)")
            log(f"- Failed case studies: {len(failed_records)}/{case_study_counter} ({len(failed_records)/case_study_counter*100:.1f}%)")
            
            # Only save intermediate checkpoints if we've reached the checkpoint interval 
            # AND we're not at the end of processing
            if checkpoint_interval > 0 and successful_case_studies_count > 0 and (successful_case_studies_count % checkpoint_interval == 0) and batch_end < len(records_to_process):
                log(f"Saving checkpoint after {successful_case_studies_count} successful case studies")
                await save_intermediate_results_unified(successful_records, failed_records, successful_case_studies_count, destination)
                await save_metadata(current_stakeholder_idx, checkpoint_interval, len(prepared_records), destination)
        
        # Now that ALL batches are processed, finalize results
        # Always save a final checkpoint with all results
        total_stakeholders = len(prepared_records)
        successful_case_studies_count = len(successful_records)
        log(f"Completed generation of all case studies")
        log(f"- Total stakeholders processed: {total_stakeholders}")
        log(f"- Total case studies attempted: {case_study_counter}")
        log(f"- Successful case studies: {successful_case_studies_count}/{case_study_counter} ({successful_case_studies_count/case_study_counter*100:.1f}%)")
        log(f"- Failed case studies: {len(failed_records)}/{case_study_counter} ({len(failed_records)/case_study_counter*100:.1f}%)")
        
        # Save a final checkpoint before attempting upload
        log(f"Saving final checkpoint with all {successful_case_studies_count} successful case studies")
        await save_intermediate_results_unified(successful_records, failed_records, successful_case_studies_count, destination)
        await save_metadata(total_stakeholders, checkpoint_interval, len(prepared_records), destination)
            
        # Now upload the finalized results
        log(f"Preparing to upload dataset to {destination}")
        
        try:
            # Split records by language but ensure same schema
            english_records = [r for r in successful_records if r["language"] == "english"]
            chinese_records = [r for r in successful_records if r["language"] == "chinese"]
            english_failed = [r for r in failed_records if r["language"] == "english"]
            chinese_failed = [r for r in failed_records if r["language"] == "chinese"]
            
            # Ensure all splits have the same schema even if empty
            empty_record = {
                "id": 0,
                "case_study_info": "",
                "prompt": "",
                "original_info": "",
                "stakeholder": "",
                "motivation": "",
                "elapsed_time": 0.0,
                "endpoint": "",
                "language": ""
            }
            
            # Create datasets with consistent schema
            dataset_splits = {}
            
            # Create english dataset
            dataset_splits['english'] = Dataset.from_list(english_records) if english_records else Dataset.from_list([empty_record]).select([])
            
            # Create chinese dataset with same schema
            dataset_splits['chinese'] = Dataset.from_list(chinese_records) if chinese_records else Dataset.from_list([empty_record]).select([])
            
            # Create failed datasets with same schema
            if english_failed:
                dataset_splits['english_failed'] = Dataset.from_list(english_failed)
            if chinese_failed:
                dataset_splits['chinese_failed'] = Dataset.from_list(chinese_failed)
            
            dataset_dict = DatasetDict(dataset_splits)
            total_records_count = sum(len(split) for split in dataset_dict.values())
            log(f"Created dataset dictionary with {total_records_count} total records")
            for split_name, split in dataset_dict.items():
                log(f"- {split_name}: {len(split)} records")
                if len(split) > 0:
                    log(f"  - Columns: {', '.join(split.column_names)}")
        except Exception as e:
            log(f"Error creating dataset dictionary: {str(e)}", False)
            raise
            
        try:
            hf_token = config.get('hf_token')
            if hf_token:
                log("Using HF_TOKEN from config")
                dataset_dict.push_to_hub(destination, token=hf_token, private=True)
            else:
                log("No HF_TOKEN in config, trying default credentials")
                dataset_dict.push_to_hub(destination, private=True)
                
            log(f"Successfully pushed to hub: {destination}")
        except Exception as e:
            log(f"Error pushing to hub: {str(e)}", True)
            raise
            
        log(f"Results uploaded to {destination}:")
        log(f"- Total successful case studies: {len(successful_records)}")
        log(f"- English successful: {len(english_records)}")
        log(f"- Chinese successful: {len(chinese_records)}")
        failed_total = len(failed_records)
        if failed_total > 0:
            log(f"- Total failed case studies: {failed_total}")
            log(f"- English failed: {len(english_failed)}")
            log(f"- Chinese failed: {len(chinese_failed)}")
        
        await clear_metadata()
        
        return True
    except Exception as e:
        log(f"Error uploading results: {type(e).__name__}: {str(e)}", True)
        return False

@lru_cache(maxsize=512)
async def prepare_prompt(case_study_info: str, stakeholder: str, motivation: str, language: str) -> str:
    if not case_study_info or not stakeholder:
        return None
    system_prompt = config['systems'].get(language, "")
    prompt_template = config['prompts'].get(language, "")
    if not prompt_template or not system_prompt:
        log(f"No template/system found for language: {language}", False)
        return None
    case_study_info = case_study_info.strip()
    stakeholder = stakeholder.strip()
    motivation = motivation.strip() or "Unknown motivations or intentions"
    try:
        return prompt_template.format(
            case_study_info=case_study_info,
            stakeholder=stakeholder,
            motivation=motivation
        )
    except KeyError as e:
        log(f"Error formatting prompt: Missing key {e} in template", False)
        return f"{case_study_info}\n\nStakeholder: {stakeholder}\nMotivation: {motivation}"
    except Exception as e:
        log(f"Error formatting prompt: {str(e)}", False)
        return None

@lru_cache(maxsize=1024)
def clean_stakeholder(stakeholder_text: str) -> str:
    if not stakeholder_text or not isinstance(stakeholder_text, str):
        return ""
    stakeholder_text = stakeholder_text.replace("## Stakeholders", "")
    stakeholder_text = stakeholder_text.replace("### List of Named Stakeholders", "")
    stakeholder_text = stakeholder_text.replace("List of Named Stakeholders", "")
    stakeholder_text = stakeholder_text.replace("Role:", "")
    if stakeholder_text.startswith("###"):
        stakeholder_text = stakeholder_text.lstrip("#").strip()
    lines = stakeholder_text.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        if not line.strip():
            continue
        cleaned_line = line.strip()
        cleaned_line = cleaned_line.lstrip("-").lstrip("*").lstrip("•").strip()
        if cleaned_line and cleaned_line[0].isdigit() and cleaned_line.find('.') > 0:
            try:
                cleaned_line = cleaned_line[cleaned_line.find('.')+1:].strip()
            except:
                pass
        if cleaned_line.lower().startswith("role:"):
            cleaned_line = cleaned_line[5:].strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    if cleaned_lines:
        return cleaned_lines[0]
    return ""

async def expand_dataset(dataset) -> list:
    expanded, skipped, valid = [], 0, 0
    total_records = len(dataset)
    stakeholder_counts = []
    cleaned_count = 0
    for idx, row in enumerate(dataset):
        try:
            info = row.get('case_study_info', '')
            stakeholders = row.get('stakeholders', {})
            stakeholder_list = stakeholders.get('stakeholder', [])
            motivations = stakeholders.get('motivation', [])
            if stakeholder_list and motivations and len(stakeholder_list) == len(motivations):
                valid += 1
                stakeholder_counts.append(len(stakeholder_list))
                for s_idx, (stakeholder, motivation) in enumerate(zip(stakeholder_list, motivations)):
                    original_stakeholder = stakeholder
                    cleaned_stakeholder = clean_stakeholder(stakeholder)
                    if cleaned_stakeholder != original_stakeholder:
                        cleaned_count += 1
                    if cleaned_stakeholder:
                        expanded.append({
                            'case_study_info': info,
                            'stakeholder': cleaned_stakeholder,
                            'original_stakeholder': original_stakeholder,
                            'motivation': motivation,
                            'original_idx': idx,
                            'stakeholder_idx': s_idx
                        })
                    else:
                        skipped += 1
                        log(f"Skipping stakeholder in source record {idx}: Empty after cleaning", False)
            else:
                skipped += 1
                log(f"Skipping source record {idx}: Invalid stakeholders structure", False)
        except Exception as ex:
            log(f"Error expanding source record {idx}: {ex}", False)
            skipped += 1
    avg_stakeholders = sum(stakeholder_counts) / len(stakeholder_counts) if stakeholder_counts else 0
    max_stakeholders = max(stakeholder_counts) if stakeholder_counts else 0
    log(f"Dataset expansion statistics:")
    log(f"- Original source records: {total_records}")
    log(f"- Valid source records: {valid}")
    log(f"- Skipped source records: {skipped}")
    log(f"- Total stakeholders: {len(expanded)}")
    log(f"- Stakeholders requiring cleaning: {cleaned_count}")
    log(f"- Total case studies needed: {len(expanded) * 2} (English + Chinese)")
    log(f"- Average stakeholders per valid source record: {avg_stakeholders:.2f}")
    log(f"- Max stakeholders in a source record: {max_stakeholders}")
    log(f"- Success rate: {(valid/total_records*100):.1f}%")
    return expanded

async def prepare_all_prompts(records: list) -> list:
    prepared_records, failed_english, failed_chinese, failed_both = [], 0, 0, 0
    total_stakeholders = len(records)
    failed_reasons = {'en': {}, 'zh': {}}
    for record in records:
        try:
            english_prompt, english_error = None, None
            chinese_prompt, chinese_error = None, None
            try:
                english_prompt = await prepare_prompt(
                    record['case_study_info'], 
                    record['stakeholder'], 
                    record['motivation'], 
                    'en'
                )
            except Exception as e:
                english_error = str(e)
                error_type = type(e).__name__
                failed_reasons['en'][error_type] = failed_reasons['en'].get(error_type, 0) + 1
            try:
                chinese_prompt = await prepare_prompt(
                    record['case_study_info'], 
                    record['stakeholder'], 
                    record['motivation'], 
                    'zh'
                )
            except Exception as e:
                chinese_error = str(e)
                error_type = type(e).__name__
                failed_reasons['zh'][error_type] = failed_reasons['zh'].get(error_type, 0) + 1
            result_record = {**record}
            if english_prompt or chinese_prompt:
                result_record['prompts'] = {}
                if english_prompt:
                    result_record['prompts']['en'] = english_prompt
                if chinese_prompt:
                    result_record['prompts']['zh'] = chinese_prompt
                if english_error:
                    result_record['en_error'] = english_error
                if chinese_error:
                    result_record['zh_error'] = chinese_error
                prepared_records.append(result_record)
                if not english_prompt:
                    failed_english += 1
                if not chinese_prompt:
                    failed_chinese += 1
            else:
                result_record['en_error'] = english_error or "Failed to generate prompt"
                result_record['zh_error'] = chinese_error or "Failed to generate prompt"
                prepared_records.append(result_record)
                failed_both += 1
        except Exception as e:
            log(f"Error preparing prompts for record: {e}", False)
            prepared_records.append({
                **record,
                'en_error': str(e),
                'zh_error': str(e)
            })
            failed_both += 1
    successful_english = total_stakeholders - failed_english - failed_both
    successful_chinese = total_stakeholders - failed_chinese - failed_both
    total_successful = successful_english + successful_chinese
    log(f"Prompt preparation statistics:")
    log(f"- Total stakeholders processed: {total_stakeholders}")
    log(f"- Prepared records: {len(prepared_records)}")
    log(f"- English prompts successful: {successful_english}/{total_stakeholders} ({successful_english/total_stakeholders*100:.1f}%)")
    log(f"- Chinese prompts successful: {successful_chinese}/{total_stakeholders} ({successful_chinese/total_stakeholders*100:.1f}%)")
    log(f"- Total successful prompts: {total_successful}")
    log(f"- Overall success rate: {(total_successful/(total_stakeholders*2))*100:.1f}%")
    if any(failed_reasons['en'].values()):
        log("English failures by error type:")
        for error_type, count in sorted(failed_reasons['en'].items(), key=lambda x: x[1], reverse=True):
            log(f"- {error_type}: {count}")
    if any(failed_reasons['zh'].values()):
        log("Chinese failures by error type:")
        for error_type, count in sorted(failed_reasons['zh'].items(), key=lambda x: x[1], reverse=True):
            log(f"- {error_type}: {count}")
    return prepared_records

async def setup_directories(args):
    run_id = str(int(time.time()))
    output_path = os.path.abspath(args.output)
    log_dir = args.log_dir or os.path.join(output_path, "logs")
    data_dir = os.path.join(output_path, "data")
    run_dir = os.path.join(data_dir, run_id)
    case_studies_dir = os.path.join(run_dir, "case_studies")
    temp_dir = os.path.join(run_dir, "temp")
    checkpoints_dir = os.path.join(run_dir, "checkpoints")
    for directory in [data_dir, run_dir, case_studies_dir, temp_dir, checkpoints_dir]:
        os.makedirs(directory, exist_ok=True)
    en_dir = os.path.join(temp_dir, "en")
    zh_dir = os.path.join(temp_dir, "zh")
    for directory in [en_dir, zh_dir]:
        os.makedirs(directory, exist_ok=True)
    
    requested_workers = args.workers or MAX_WORKERS
    effective_workers = min(requested_workers, len(config['endpoints']))
    
    if effective_workers < requested_workers:
        log(f"Capping workers from {requested_workers} to {effective_workers} based on available endpoints")
    
    checkpoint_interval = args.checkpoint_interval if args.checkpoint_interval > 0 else float('inf')
    
    return {
        "run_id": run_id,
        "output_path": output_path,
        "log_dir": log_dir,
        "data_dir": data_dir,
        "run_dir": run_dir,
        "case_studies_dir": case_studies_dir,
        "checkpoints_dir": checkpoints_dir,
        "temp_dir": temp_dir,
        "temp_dir_en": en_dir,
        "temp_dir_zh": zh_dir,
        "workers": effective_workers,
        "endpoints_count": len(config['endpoints']),
        "checkpoint_interval": checkpoint_interval
    }

async def test_endpoints(workers_count):
    semaphore = asyncio.Semaphore(workers_count)
    log(f"Starting endpoint tests with {workers_count} parallel workers (timeout: {TEST_TIMEOUT}s)")
    test_results = []
    tasks = []
    for i, endpoint in enumerate(config["endpoints"]):
        tasks.append(test_endpoint(endpoint, semaphore))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, result in enumerate(results):
        endpoint = config["endpoints"][i]
        if isinstance(result, Exception):
            log(f"Error testing endpoint {i+1}/{len(config['endpoints'])}: {str(result)}")
            test_results.append((endpoint.get('p', 'unknown'), endpoint.get('n', 'unknown'), 0.0, None))
        else:
            provider, name, test_time, response = result
            is_ok = response == "OK" or response == "RATE_LIMITED"
            status_text = "OK" if response == "OK" else "Rate Limited" if response == "RATE_LIMITED" else "Failed"
            log(f"Tested endpoint {i+1}/{len(config['endpoints'])}: {provider}-{name} - {status_text}")
            test_results.append(result)
    
    console_logger.info("Test results:")
    for provider, name, test_time, result in test_results:
        if result == "RATE_LIMITED":
            status = "Rate Limited"
            console_logger.info(f"- endpoint {status}! [ {provider}-{name}: rate limited ]")
        else:
            status = "OK" if result == "OK" else "Fail"
            console_logger.info(f"- endpoint {status}! [ {provider}-{name}: {test_time}s ]")
    
    valid_times = [tt for _, _, tt, result in test_results if result == "OK" and tt]
    if valid_times:
        avg_time = round(sum(valid_times) / len(valid_times), 2)
        console_logger.info(f"- average time: {avg_time}s")
    
    provider_stats = {}
    for provider, _, _, result in test_results:
        if provider not in provider_stats:
            provider_stats[provider] = {"total": 0, "success": 0}
        provider_stats[provider]["total"] += 1
        if result == "OK" or result == "RATE_LIMITED":
            provider_stats[provider]["success"] += 1
    
    console_logger.info("Provider summary:")
    for provider, stats in provider_stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        console_logger.info(f"- {provider}: {stats['success']}/{stats['total']} endpoints ok ({success_rate:.1f}%)")
    
    return sum(1 for _, _, _, result in test_results if result == "OK" or result == "RATE_LIMITED")

async def main(args):
    try:
        global dirs, endpoints, config
        if args.source:
            log(f"Overriding source dataset from '{config.get('src', 'none')}' to '{args.source}'")
            config['src'] = args.source
        if args.dest:
            log(f"Overriding destination dataset from '{config.get('dest', 'none')}' to '{args.dest}'")
            config['dest'] = args.dest
        
        dirs = await setup_directories(args)

        metadata = await load_metadata()
        if (metadata and args.resume):
            log("Resuming from previous processing session")
        elif (metadata and not args.resume):
            log("Found existing metadata but --resume flag not specified. Starting from beginning.")
            await clear_metadata()
        for key, value in dirs.items():
            log(f"{key.replace('_', ' ').title()}: {value}")
        log(f"Config loaded with {len(config.get('endpoints', []))} endpoints")
        log(f"- Model: {config.get('model', 'not specified')}")
        log(f"- Max tokens: {config.get('max_tokens', 'not specified')}")
        log(f"- Temperature: {config.get('temperature', 'not specified')}")
        log(f"- Source dataset: {config.get('src', 'not specified')}")
        log(f"- Destination dataset: {config.get('dest', 'not specified')}")
        log(f"- Has HF token: {'Yes' if 'hf_token' in config and config['hf_token'] else 'No'}")
        log(f"- Generation request timeout: {REQUEST_TIMEOUT}s")
        log(f"- Endpoint testing timeout: {TEST_TIMEOUT}s")
        for lang, lang_name in [('en', 'English'), ('zh', 'Chinese')]: 
            system_ok = lang in config.get('systems', {})
            prompt_ok = lang in config.get('prompts', {})
            if not system_ok or not prompt_ok:
                log(f"Warning: {lang_name} support incomplete - System: {system_ok}, Prompt: {prompt_ok}")
        if not isinstance(config, dict) or 'endpoints' not in config:
            raise ValueError("Invalid config: must contain 'endpoints' key")
        endpoints = init_endpoints(config['endpoints'])
        working_endpoints = await test_endpoints(dirs["workers"])
        if working_endpoints == 0:
            raise ValueError("No working endpoints found. Cannot proceed.")
        log(f"Found {working_endpoints} working endpoints out of {len(config['endpoints'])} total")
        if working_endpoints < dirs["workers"]:
            dirs["workers"] = max(1, working_endpoints)
            log(f"Reduced worker count to {dirs['workers']} based on available endpoints")
        log("Loading dataset...")
        dataset = await load_source_dataset(args.offset, args.max_records)
        if not dataset:
            raise ValueError("Failed to load dataset")
        log("Expanding dataset records...")
        expanded_records = await expand_dataset(dataset)
        log("Preparing prompts...")
        prepared_records = await prepare_all_prompts(expanded_records)
        destination = config.get('dest')
        if not destination:
            raise ValueError("No destination dataset in config")
        if "hf_token" in config:
            log("HF_TOKEN found in config")
        else:
            log("Warning: No HF_TOKEN found in config. Authentication may fail.")
        upload_success = await upload_results(prepared_records, destination, args.checkpoint_interval)
        if not upload_success:
            raise ValueError("Failed to upload dataset")
        log(f"Successfully initialized dataset structure at {destination}")
    except Exception as e:
        log(f"Fatal error: {str(e)}", True)
        raise e

if __name__ == "__main__":
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    parser = ap.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG_URL, help="URL to the configuration file")
    parser.add_argument("--output", default=os.getcwd(), help="Output directory for case studies")
    parser.add_argument("--log-dir", help="Directory to save log files")
    parser.add_argument("--workers", type=int, help="Number of parallel workers for endpoint testing")
    parser.add_argument("--checkpoint-interval", type=int, default=CHECKPOINT_INTERVAL, help="Interval to save intermediate checkpoints (default: 100)")
    parser.add_argument("--resume", action="store_true", help="Resume from previous processing session")
    parser.add_argument("--max-records", type=int, default=0, help="Maximum number of records to process")
    parser.add_argument("--offset", type=int, default=0, help="Offset to start processing records from")
    parser.add_argument("--source", help="Override source dataset name (e.g., DataTonic/dark_thoughts_stakeholders_80)")
    parser.add_argument("--dest", help="Override destination dataset name (e.g., DataTonic/dark_thoughts_casestudy_r1_scaleway_A2)")
    args = parser.parse_args()
    DEFAULT_CONFIG_URL = args.config
    try:
        global console_logger, file_logger, config, dirs
        console_logger, file_logger = setup_loggers(
            args.log_dir or os.path.join(os.getcwd(), "logs")
        )
        config = asyncio.run(fetch_config())
        if config:
            asyncio.run(main(args))
        else:
            console_logger.error("No config")
    except Exception as e:
        console_logger.error(f"Fatal error: {e}")
        exit(1)