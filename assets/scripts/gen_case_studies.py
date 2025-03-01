import argparse as ap, os, asyncio, logging, time, requests, random, json
from openai import AsyncOpenAI
from tenacity import retry, wait_random, stop_after_attempt, retry_if_exception
from asyncio import TimeoutError
from datasets import load_dataset, Dataset, DatasetDict
from functools import lru_cache

MAX_WORKERS = 15
MAX_RETRIES = 10
MAX_RETRY_DELAY = 0.3
API_BASE_URL = "api.scaleway.ai"
REQUEST_COUNTER = 0
ENDPOINT_COOLDOWN = 12
CHECKPOINT_INTERVAL = 1000
REQUEST_TIMEOUT = 600
TEST_TIMEOUT = 30
BATCH_SIZE = 250

def log(message: str, console_output: bool = True) -> None:
    try:
        file_logger.info(message)
        if (console_output):
            try:
                cl.info(message)
            except UnicodeEncodeError:
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                cl.info(safe_message)
    except Exception as e:
        try:
            print(f"[LOGGING ERROR] Failed to log message: {str(e)}")
        except:
            pass

def setup_loggers(log_path: str) -> tuple[logging.Logger, logging.Logger]:
    os.makedirs(log_path, exist_ok=True)
    cl, fl = logging.getLogger("console"), logging.getLogger("file")
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    cl.addHandler(ch)
    cl.setLevel(logging.INFO)
    cl.propagate = False
    file = os.path.join(log_path, f"cs_{int(time.time())}.log")
    fh = logging.FileHandler(file, encoding='utf-8')
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    fl.addHandler(fh)
    fl.setLevel(logging.INFO)
    fl.propagate = False
    return cl, fl

async def fetch_config():
    try:
        log(f"Fetching config from: {args.config}")
        response = requests.get(args.config)
        if response.status_code == 200:
            config_json = response.json()
            log("Config fetched successfully")
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
                        await asyncio.sleep(3)
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

class TelemetryStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.processed_files = set()

    def log_success(self, language, case_study_idx):
        self.total_attempts += 1
        
        unique_id = f"{language}_{case_study_idx}"
        if unique_id not in self.processed_files:
            self.successful_generations += 1
            self.processed_files.add(unique_id)
        
    def log_failure(self, language, error_type):
        self.total_attempts += 1
        self.failed_generations += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def reset_stats(self, expected_total=0):
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
        
        if rpm > 0:
            est_minutes = remaining / (rpm * (1 - error_rate/100))
            time_remaining = f"{est_minutes:.1f} min" if est_minutes < 60 else f"{est_minutes/60:.1f} hours"
        else:
            time_remaining = "unknown"
            
        return (f"TELEMETRY: {self.successful_generations}/{total_needed} complete ({self.successful_generations/total_needed*100:.1f}%) • "
                f"{remaining} remaining • {rpm:.1f} req/min • "
                f"{error_rate:.1f}% errors • Est. remaining: {time_remaining}")

telemetry_stats = TelemetryStats()

def should_retry(exception):
    if isinstance(exception, ResponseTooShortError):
        return True
    
    if isinstance(exception, Exception) and ("429" in str(exception) or 
                                           "TOO MANY TOKENS" in str(exception) or 
                                           "rate limit" in str(exception).lower()):
        return True
    return False

@retry(stop=stop_after_attempt(MAX_RETRIES), 
       wait=wait_random(min=0.1, max=MAX_RETRY_DELAY), 
       retry=should_retry,
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
                    
                    if time.time() - telemetry_stats.last_log_time > 30:
                        if 'total_case_studies' in globals():
                            total_needed = total_case_studies
                        else:
                            total_needed = 0
                        log(telemetry_stats.get_telemetry_string(total_needed))
                        telemetry_stats.last_log_time = time.time()
                        
                except Exception as e:
                    log(f"Error saving case study #{case_study_idx} to file: {str(e)}", False)
                    telemetry_stats.log_failure("FileSaveError")
                    
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

async def save_intermediate_results_unified(successful_records, failed_records, processed_count, destination):
    try:
        english_records = [r for r in successful_records if r["language"] == "english"]
        chinese_records = [r for r in successful_records if r["language"] == "chinese"]
        english_failed = [r for r in failed_records if r["language"] == "english"]
        chinese_failed = [r for r in failed_records if r["language"] == "chinese"]
        
        empty_record = {
            "id": 0,
            "language": "",
            "case_study_info": "",
            "prompt": "",
            "original_info": "",
            "stakeholder": "",
            "motivation": "",
            "model": config.get("model", "unknown"),
            "elapsed_time": 0.0,
            "endpoint": ""
        }
        
        dataset_splits = {
            'english': Dataset.from_list(english_records) if english_records else Dataset.from_list([empty_record]).select([]),
            'chinese': Dataset.from_list(chinese_records) if chinese_records else Dataset.from_list([empty_record]).select([])
        }
        
        if english_failed:
            dataset_splits['english_failed'] = Dataset.from_list(english_failed)
        if chinese_failed:
            dataset_splits['chinese_failed'] = Dataset.from_list(chinese_failed)
            
        dataset_dict = DatasetDict(dataset_splits)
        save_path = os.path.join(dirs["checkpoints_dir"], f"checkpoint_{processed_count}")
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
    global total_case_studies
    total_case_studies = len(prepared_records) * 2
    
    telemetry_stats.reset_stats()
    
    start_time = time.time()
    times = []
    ckpt_times = []
    
    try:
        records = []
        success = []
        failed = []
        
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
            result = {
                "id": len(records) + 1 if add_id else 0,
                "language": language,
                "case_study_info": record.get("case_study_info", ""),
                "prompt": record.get("prompt", ""),
                "original_info": record.get("original_info", ""),
                "stakeholder": record.get("stakeholder", ""),
                "motivation": record.get("motivation", ""),
                "model": config.get("model", "unknown"),
                "elapsed_time": record.get("elapsed_time", 0.0),
                "endpoint": record.get("endpoint", "")
            }
            return result
        
        async def process_case_study(record, language, idx, total, semaphore):
            async with semaphore:
                language_key = 'en' if language == 'english' else 'zh'
                error_key = f"{language_key}_error"
                lang_name = "English" if language == 'english' else "Chinese"
                system_prompt = config['systems'].get(language_key, "")
                
                source_record_idx = record.get('original_idx', -1)
                stakeholder_idx = record.get('stakeholder_idx', -1)
                stakeholder_name = record.get('stakeholder', 'Unknown')
                case_study_idx = idx
                
                if not system_prompt:
                    error_msg = f"Missing system prompt for {lang_name}"
                    log(f"Error: {error_msg}")
                    failed_record = process_record({
                        "original_info": record['case_study_info'],
                        "stakeholder": record.get('stakeholder', ''),
                        "motivation": record.get('motivation', ''),
                        "endpoint": f"error - {error_msg}"
                    }, language)
                    failed.append(failed_record)
                    return False
                
                if 'prompts' in record and language_key in record['prompts'] and record['prompts'][language_key]:
                    try:
                        endpoint_idx = get_next_endpoint(endpoints)
                        endpoint_config = endpoints[endpoint_idx]
                        endpoint_formatted = format_endpoint(endpoint_config)
                        
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
                            
                            has_content = bool(case_study_info and case_study_info.strip())
                            if has_content:
                                result_record = process_record({
                                    "case_study_info": case_study_info,
                                    "original_info": record['case_study_info'],
                                    "prompt": record['prompts'][language_key],
                                    "stakeholder": record.get('stakeholder', ''),
                                    "motivation": record.get('motivation', ''),
                                    "elapsed_time": elapsed_time,
                                    "endpoint": endpoint_formatted,
                                    "model": config.get("model", "unknown")
                                }, language)
                                success.append(result_record)
                                records.append(result_record)
                                telemetry_stats.log_success(language_key, case_study_idx)
                                size_in_bytes = len(case_study_info.encode('utf-8'))
                                formatted_size = f"{size_in_bytes:,}"
                                log(f"Completed {lang_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1} ({stakeholder_name}) - {elapsed_time:.2f}s (size {formatted_size} B)")
                                log(telemetry_stats.get_telemetry_string(total_case_studies))
                                
                                return True
                            else:
                                raise ValueError("Empty result returned")
                                
                        except Exception as e:
                            temp_dir = os.path.join(dirs["temp_dir"], language_key)
                            filepath = os.path.join(temp_dir, f"{case_study_idx:06d}.txt")
                            if os.path.exists(filepath):
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        recovered_content = f.read()
                                    
                                    if recovered_content and len(recovered_content) > 100:
                                        log(f"Recovered file for {lang_name} case study {idx} despite error: {str(e)}")
                                        
                                        result_record = process_record({
                                            "case_study_info": recovered_content,
                                            "original_info": record['case_study_info'],
                                            "prompt": record['prompts'][language_key],
                                            "stakeholder": record.get('stakeholder', ''),
                                            "motivation": record.get('motivation', ''),
                                            "elapsed_time": 0.0,
                                            "endpoint": endpoint_formatted + "-recovered",
                                            "model": config.get("model", "unknown")
                                        }, language)
                                        
                                        success.append(result_record)
                                        records.append(result_record)
                                        
                                        telemetry_stats.log_success(language_key, case_study_idx)
                                        
                                        log(f"Successfully recovered {lang_name} case study {idx} from saved file")
                                        return True
                                except Exception as recovery_error:
                                    log(f"Failed to recover from temp file: {str(recovery_error)}")
                            
                            error_msg = str(e)
                            log(f"Error generating {lang_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {error_msg}")
                            file_logger.error(f"Generation error for {language}: {error_msg}")
                            
                            failed_record = process_record({
                                "original_info": record['case_study_info'],
                                "prompt": record['prompts'][language_key],
                                "stakeholder": record.get('stakeholder', ''),
                                "motivation": record.get('motivation', ''),
                                "endpoint": f"error - {error_msg}",
                                "model": config.get("model", "unknown")
                            }, language)
                            failed.append(failed_record)
                            records.append(failed_record)
                            telemetry_stats.log_failure(language_key, type(e).__name__)
                            return False
                    except Exception as e:
                        error_msg = str(e)
                        log(f"Error generating {lang_name} case study {idx}/{total} - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1}: {error_msg}")
                        file_logger.error(f"Generation error for {language}: {error_msg}")
                        
                        failed_record = process_record({
                            "original_info": record['case_study_info'],
                            "prompt": record['prompts'][language_key],
                            "stakeholder": record.get('stakeholder', ''),
                            "motivation": record.get('motivation', ''),
                            "endpoint": f"error - {error_msg}",
                            "model": config.get("model", "unknown")
                        }, language)
                        failed.append(failed_record)
                        records.append(failed_record)
                        telemetry_stats.log_failure(language_key, type(e).__name__)
                        return False
                else:
                    error_msg = record.get(error_key, f"Failed to generate {language} prompt")
                    log(f"Missing prompt for case study {idx}/{total} - {lang_name}: {error_msg}")
                    
                    failed_record = process_record({
                        "original_info": record['case_study_info'],
                        "stakeholder": record.get('stakeholder', ''),
                        "motivation": record.get('motivation', ''),
                        "endpoint": f"error - {error_msg}",
                        "model": config.get("model", "unknown")
                    }, language)
                    failed.append(failed_record)
                    records.append(failed_record)
                    return False
                    
        total_case_studies = len(prepared_records) * 2
        log(f"Starting to generate {total_case_studies} case studies ({len(prepared_records)} stakeholders × 2 languages)")
        
        start_idx = resume_from
        to_process = prepared_records[start_idx:]
        semaphore = asyncio.Semaphore(dirs["workers"])
        log(f"Using semaphore with {dirs['workers']} workers for concurrent processing")
        log(f"Using batch size of {dirs['batch_size']} (worker count: {dirs['workers']})")
        
        total_success = 0
        total_processed = 0
        counter = 0
        
        for start in range(0, len(to_process), dirs["batch_size"]):
            start_time = time.time()
            end = min(start + dirs["batch_size"], len(to_process))
            batch = to_process[start:end]
            size = len(batch)
            log(f"Processing batch of {size} stakeholders ({start+start_idx+1} to {end+start_idx} out of {len(prepared_records)})")
            
            tasks = []
            for i, record in enumerate(batch):
                counter += 1
                tasks.append(process_case_study(record, 'english', counter, total_case_studies, semaphore))
                
                counter += 1
                tasks.append(process_case_study(record, 'chinese', counter, total_case_studies, semaphore))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                total_processed += 1
                
                if isinstance(result, Exception):
                    language = 'english' if i % 2 == 0 else 'chinese'
                    record = batch[i // 2]
                    source_record_idx = record.get('original_idx', -1)
                    stakeholder_idx = record.get('stakeholder_idx', -1)
                    log(f"Error in batch processing - Source #{source_record_idx+1}, Stakeholder #{stakeholder_idx+1} ({language}): {str(result)}")
                
                if checkpoint_interval > 0 and total_processed > 0 and (total_processed % checkpoint_interval == 0):
                    ckpt_start = time.time()
                    log(f"Saving checkpoint after {total_processed} total case studies ({len(success)} successful)")
                    await save_intermediate_results_unified(success, failed, total_processed, destination)
                    await save_metadata(end + start_idx, checkpoint_interval, len(prepared_records), destination)
                    ckpt_duration = time.time() - ckpt_start
                    ckpt_times.append(ckpt_duration)
                    log(f"Checkpoint saved in {ckpt_duration:.2f} seconds")

            duration = time.time() - start_time
            times.append(duration)
            avg_time = sum(times) / len(times)
            current_stakeholder_idx = end + start_idx
            total_success = len(success)

            log(f"Progress: {current_stakeholder_idx}/{len(prepared_records)} stakeholders processed ({current_stakeholder_idx/len(prepared_records)*100:.1f}%)")
            log(f"- Successful case studies: {total_success}/{total_processed} ({total_success/total_processed*100:.1f}%)")
            log(f"- Failed case studies: {len(failed)}/{total_processed} ({len(failed)/total_processed*100:.1f}%)")
            log(f"- Batch completed in {duration:.2f}s (avg: {avg_time:.2f}s/batch)")
        
        total_stakeholders = len(prepared_records)
        total_success = len(success)
        total_duration = time.time() - start_time

        log(f"Completed generation of all case studies")
        log(f"- Total stakeholders processed: {total_stakeholders}")
        log(f"- Total case studies attempted: {total_processed}")
        log(f"- Successful case studies: {total_success}/{total_processed} ({total_success/total_processed*100:.1f}%)")
        log(f"- Failed case studies: {len(failed)}/{total_processed} ({len(failed)/total_processed*100:.1f}%)")
        log(f"- Total runtime: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")

        if times:
            log(f"- Average batch processing time: {sum(times)/len(times):.2f}s")
        if ckpt_times:
            log(f"- Average checkpoint time: {sum(ckpt_times)/len(ckpt_times):.2f}s")
            log(f"- Total time spent on checkpoints: {sum(ckpt_times):.2f}s ({sum(ckpt_times)/total_duration*100:.1f}% of total runtime)")

        ckpt_start = time.time()

        log(f"Saving final checkpoint with all {total_success} successful case studies")

        await save_intermediate_results_unified(success, failed, total_processed, destination)
        await save_metadata(total_stakeholders, checkpoint_interval, len(prepared_records), destination)

        ckpt_duration = time.time() - ckpt_start

        log(f"Final checkpoint saved in {ckpt_duration:.2f} seconds")
        log(f"Preparing to upload dataset to {destination}")
        
        try:
            en_records = [r for r in success if r["language"] == "english"]
            zh_records = [r for r in success if r["language"] == "chinese"]
            en_failed = [r for r in failed if r["language"] == "english"]
            zh_failed = [r for r in failed if r["language"] == "chinese"]
            
            empty_record = {
                "id": 0,
                "case_study_info": "",
                "prompt": "",
                "original_info": "",
                "stakeholder": "",
                "motivation": "",
                "elapsed_time": 0.0,
                "endpoint": "",
                "language": "",
                "model": config.get("model", "unknown")
            }
            
            splits = {}
            splits['english'] = Dataset.from_list(en_records) if en_records else Dataset.from_list([empty_record]).select([]) 
            splits['chinese'] = Dataset.from_list(zh_records) if zh_records else Dataset.from_list([empty_record]).select([])
            
            if en_failed:
                splits['english_failed'] = Dataset.from_list(en_failed)
            if zh_failed:
                splits['chinese_failed'] = Dataset.from_list(zh_failed)
            
            dict = DatasetDict(splits)
            total_count = sum(len(split) for split in dict.values())
            log(f"Created dataset dictionary with {total_count} total records")
            for split_name, split in dict.items():
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
                dict.push_to_hub(destination, token=hf_token, private=True)
            else:
                log("No HF_TOKEN in config, trying default credentials")
                dict.push_to_hub(destination, private=True)
                
            log(f"Successfully pushed to hub: {destination}")
        except Exception as e:
            log(f"Error pushing to hub: {str(e)}", True)
            raise
            
        log(f"Results uploaded to {destination}:")
        log(f"- Total successful case studies: {len(success)}")
        log(f"- English successful: {len(en_records)}")
        log(f"- Chinese successful: {len(zh_records)}")
        failed_total = len(failed)
        if failed_total > 0:
            log(f"- Total failed case studies: {failed_total}")
            log(f"- English failed: {len(en_failed)}")
            log(f"- Chinese failed: {len(zh_failed)}")
        
        await clear_metadata()
        
        return True
    except Exception as e:
        log(f"Error uploading results: {type(e).__name__}: {str(e)}", True)
        return False

@lru_cache(maxsize=512)
def prepare_prompt(source_data: str, stakeholder: str, motivation: str, language: str) -> str:
    if not source_data or not stakeholder:
        return None
    system_prompt = config['systems'].get(language, "")
    prompt_template = config['prompts'].get(language, "")
    if not prompt_template or not system_prompt:
        log(f"No template/system found for language: {language}", False)
        return None
    source_data = source_data.strip()
    stakeholder = stakeholder.strip()
    motivation = motivation.strip() or "Unknown motivations or intentions"
    try:
        return prompt_template.format(
            case_study_info=source_data,
            stakeholder=stakeholder,
            motivation=motivation
        )
    except KeyError as e:
        log(f"Error formatting prompt: Missing key {e} in template", False)
        return f"{source_data}\n\nStakeholder: {stakeholder}\nMotivation: {motivation}"
    except Exception as e:
        log(f"Error formatting prompt: {str(e)}", False)
        return None

@lru_cache(maxsize=1024)
def clean_stakeholder(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.replace("## Stakeholders", "")
    text = text.replace("### List of Named Stakeholders", "")
    text = text.replace("List of Named Stakeholders", "")
    text = text.replace("Role:", "")
    if text.startswith("###"):
        text = text.lstrip("#").strip()
    lines = text.strip().split('\n')
    clean = []
    for line in lines:
        if not line.strip():
            continue
        clean_line = line.strip()
        clean_line = clean_line.lstrip("-").lstrip("*").lstrip("•").strip()
        if clean_line and clean_line[0].isdigit() and clean_line.find('.') > 0:
            try:
                clean_line = clean_line[clean_line.find('.')+1:].strip()
            except:
                pass
        if clean_line.lower().startswith("role:"):
            clean_line = clean_line[5:].strip()
        if clean_line:
            clean.append(clean_line)
    if clean:
        return clean[0]
    return ""

async def expand_dataset(dataset) -> list:
    expanded, skipped, valid = [], 0, 0
    total_records = len(dataset)
    stakeholder_counts = []  # Renamed to avoid conflict with stakeholders variable below
    cleaned_count = 0
    for idx, row in enumerate(dataset):
        try:
            info = row.get('case_study_info', '')
            stakeholders_data = row.get('stakeholders', {})  # Renamed to avoid conflict
            stakeholder_list = stakeholders_data.get('stakeholder', [])
            motivations = stakeholders_data.get('motivation', [])
            if stakeholder_list and motivations and len(stakeholder_list) == len(motivations):
                valid += 1
                stakeholder_counts.append(len(stakeholder_list))
                for s_idx, (stakeholder_text, motivation) in enumerate(zip(stakeholder_list, motivations)):
                    original_stakeholder = stakeholder_text
                    cleaned_stakeholder = clean_stakeholder(stakeholder_text)  # Renamed parameter to avoid conflict
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
    prepared, failed_en, failed_zh, failed_all = [], 0, 0, 0
    stakeholders = len(records)
    failed_reasons = {'en': {}, 'zh': {}}
    for record in records:
        try:
            en_prompt, en_e = None, None
            zh_prompt, zh_e = None, None
            try:
                en_prompt = prepare_prompt(
                    record['case_study_info'], 
                    record['stakeholder'], 
                    record['motivation'], 
                    'en'
                )
            except Exception as e:
                en_e = str(e)
                e_type = type(e).__name__
                failed_reasons['en'][e_type] = failed_reasons['en'].get(e_type, 0) + 1
            try:
                zh_prompt = prepare_prompt(
                    record['case_study_info'], 
                    record['stakeholder'], 
                    record['motivation'], 
                    'zh'
                )
            except Exception as e:
                zh_e = str(e)
                e_type = type(e).__name__
                failed_reasons['zh'][e_type] = failed_reasons['zh'].get(e_type, 0) + 1
            result = {**record}
            if en_prompt or zh_prompt:
                result['prompts'] = {}
                if en_prompt:
                    result['prompts']['en'] = en_prompt
                if zh_prompt:
                    result['prompts']['zh'] = zh_prompt
                if en_e:
                    result['en_error'] = en_e
                if zh_e:
                    result['zh_error'] = zh_e
                prepared.append(result)
                if not en_prompt:
                    failed_en += 1
                if not zh_prompt:
                    failed_zh += 1
            else:
                result['en_error'] = en_e or "Failed to generate prompt"
                result['zh_error'] = zh_e or "Failed to generate prompt"
                prepared.append(result)
                failed_all += 1
        except Exception as e:
            log(f"Error preparing prompts for record: {e}", False)
            prepared.append({
                **record,
                'en_error': str(e),
                'zh_error': str(e)
            })
            failed_all += 1
    success_en = stakeholders - failed_en - failed_all
    success_zh = stakeholders - failed_zh - failed_all
    total_success = success_en + success_zh
    log(f"Prompt preparation statistics:")
    log(f"- Total stakeholders processed: {stakeholders}")
    log(f"- Prepared records: {len(prepared)}")
    log(f"- English prompts successful: {success_en}/{stakeholders} ({success_en/stakeholders*100:.1f}%)")
    log(f"- Chinese prompts successful: {success_zh}/{stakeholders} ({success_zh/stakeholders*100:.1f}%)")
    log(f"- Total successful prompts: {total_success}")
    log(f"- Overall success rate: {(total_success/(stakeholders*2))*100:.1f}%")
    if any(failed_reasons['en'].values()):
        log("English failures by error type:")
        for e_type, count in sorted(failed_reasons['en'].items(), key=lambda x: x[1], reverse=True):
            log(f"- {e_type}: {count}")
    if any(failed_reasons['zh'].values()):
        log("Chinese failures by error type:")
        for e_type, count in sorted(failed_reasons['zh'].items(), key=lambda x: x[1], reverse=True):
            log(f"- {e_type}: {count}")
    return prepared

async def setup_directories(args):
    run_id = str(int(time.time()))
    output_dir = os.path.abspath(args.output)
    log_dir = args.log_dir or os.path.join(output_dir, "logs")
    data_dir = os.path.join(output_dir, "data")
    run_dir = os.path.join(data_dir, run_id)
    cs_dir = os.path.join(run_dir, "case_studies")
    temp_dir = os.path.join(run_dir, "temp")
    ckpt_dir = os.path.join(run_dir, "checkpoints")
    for directory in [data_dir, run_dir, cs_dir, temp_dir, ckpt_dir]:
        os.makedirs(directory, exist_ok=True)
    en_dir = os.path.join(temp_dir, "en")
    zh_dir = os.path.join(temp_dir, "zh")
    for directory in [en_dir, zh_dir]:
        os.makedirs(directory, exist_ok=True)
    
    max_workers = args.workers or MAX_WORKERS
    workers = min(max_workers, len(config['endpoints']))
    
    if workers < max_workers:
        log(f"Capping workers from {max_workers} to {workers} based on available endpoints")
    
    batch_size = args.batch_size or BATCH_SIZE
    if batch_size < workers:
        log(f"Warning: Batch size ({batch_size}) is smaller than worker count ({workers})")
    
    ckpt_interval = args.checkpoint_interval if args.checkpoint_interval > 0 else float('inf')
    
    return {
        "run_id": run_id,
        "output_path": output_dir,
        "log_dir": log_dir,
        "data_dir": data_dir,
        "run_dir": run_dir,
        "case_studies_dir": cs_dir,
        "checkpoints_dir": ckpt_dir,
        "temp_dir": temp_dir,
        "temp_dir_en": en_dir,
        "temp_dir_zh": zh_dir,
        "workers": workers,
        "batch_size": batch_size,
        "endpoints_count": len(config['endpoints']),
        "checkpoint_interval": ckpt_interval
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
    
    cl.info("Test results:")
    for provider, name, test_time, result in test_results:
        if result == "RATE_LIMITED":
            status = "Rate Limited"
            cl.info(f"- endpoint {status}! [ {provider}-{name}: rate limited ]")
        else:
            status = "OK" if result == "OK" else "Fail"
            cl.info(f"- endpoint {status}! [ {provider}-{name}: {test_time}s ]")
    
    times = [tt for _, _, tt, result in test_results if result == "OK" and tt]
    if times:
        avg_time = round(sum(times) / len(times), 2)
        cl.info(f"- average time: {avg_time}s")
    
    stats = {}
    for provider, _, _, result in test_results:
        if provider not in stats:
            stats[provider] = {"total": 0, "success": 0}
        stats[provider]["total"] += 1
        if result == "OK" or result == "RATE_LIMITED":
            stats[provider]["success"] += 1
    
    cl.info("Provider summary:")
    for provider, stats in stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        cl.info(f"- {provider}: {stats['success']}/{stats['total']} endpoints ok ({success_rate:.1f}%)")
    
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
        ready_endpoints = await test_endpoints(dirs["workers"])
        if ready_endpoints == 0:
            raise ValueError("No working endpoints found. Cannot proceed.")
        log(f"Found {ready_endpoints} working endpoints out of {len(config['endpoints'])} total")
        if ready_endpoints < dirs["workers"]:
            dirs["workers"] = max(1, ready_endpoints)
            log(f"Reduced worker count to {dirs['workers']} based on available endpoints")
        log("Loading dataset...")
        dataset = await load_source_dataset(args.offset, args.max_records)
        if not dataset:
            raise ValueError("Failed to load dataset")
        log("Expanding dataset records...")
        expanded = await expand_dataset(dataset)
        log("Preparing prompts...")
        prepared = await prepare_all_prompts(expanded)
        dest = config.get('dest')
        if not dest:
            raise ValueError("No destination dataset in config")
        if "hf_token" in config:
            log("HF_TOKEN found in config")
        else:
            log("Warning: No HF_TOKEN found in config. Authentication may fail.")
        upload_success = await upload_results(prepared, dest, args.checkpoint_interval)
        if not upload_success:
            raise ValueError("Failed to upload dataset")
        log(f"Successfully initialized dataset structure at {dest}")
    except Exception as e:
        log(f"Fatal error: {str(e)}", True)
        raise e

if __name__ == "__main__":
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    parser = ap.ArgumentParser()
    parser.add_argument("--config", required=True, help="URL to the configuration file")
    parser.add_argument("--output", default=os.getcwd(), help="Output directory for case studies")
    parser.add_argument("--log-dir", help="Directory to save log files")
    parser.add_argument("--workers", type=int, help="Number of parallel workers for endpoint testing")
    parser.add_argument("--batch-size", type=int, help="Number of records to process in a batch (default: 100")
    parser.add_argument("--checkpoint-interval", type=int, default=CHECKPOINT_INTERVAL, help="Interval to save intermediate checkpoints (default: 100)")
    parser.add_argument("--resume", action="store_true", help="Resume from previous processing session")
    parser.add_argument("--max-records", type=int, default=0, help="Maximum number of records to process")
    parser.add_argument("--offset", type=int, default=0, help="Offset to start processing records from")
    parser.add_argument("--source", help="Override source dataset name (e.g., DataTonic/dark_thoughts_stakeholders_80)")
    parser.add_argument("--dest", help="Override destination dataset name (e.g., DataTonic/dark_thoughts_casestudy_r1_scaleway_A2)")
    args = parser.parse_args()
    try:
        global console_logger, file_logger, config, dirs
        cl, file_logger = setup_loggers(
            args.log_dir or os.path.join(os.getcwd(), "logs")
        )
        config = asyncio.run(fetch_config())
        if config:
            asyncio.run(main(args))
        else:
            cl.error("No config")
    except Exception as e:
        cl.error(f"Fatal error: {e}")
        exit(1)