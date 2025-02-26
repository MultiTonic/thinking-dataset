import argparse as ap, os, asyncio, logging, time, requests
from openai import AsyncOpenAI
from tenacity import retry, wait_random, stop_after_attempt
from tqdm.asyncio import tqdm_asyncio
from asyncio import TimeoutError
from datasets import load_dataset, Dataset, DatasetDict
from huggingface_hub import HfApi

DEFAULT_CONFIG_URL = "https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw"
MAX_RETRIES = 3
MAX_RETRY_DELAY = 0.3
API_BASE_URL = "api.scaleway.ai"

# Remove the hardcoded HF_TOKEN since it's now in the config

def log(message: str, console_output: bool = True) -> None:
    file_logger.info(message)
    if (console_output):
        console_logger.info(message)

def setup_loggers(log_path: str) -> tuple[logging.Logger, logging.Logger]:
    os.makedirs(log_path, exist_ok=True)
    console_logger, file_logger = logging.getLogger("console"), logging.getLogger("file")
    for logger, handler in [
        (console_logger, logging.StreamHandler()),
        (file_logger, logging.FileHandler(os.path.join(log_path, f"cs_{int(time.time())}.log")))
    ]:
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
        logger.addHandler(handler)
    return console_logger, file_logger

async def fetch_config():
    try:
        log(f"Fetching config from: {DEFAULT_CONFIG_URL}")
        response = requests.get(DEFAULT_CONFIG_URL)
        if response.status_code == 200:
            config_json = response.json()
            log("Config fetched successfully")
            return {
                key: config_json[key] 
                for key in ['endpoints', 'model', 'src', 'dest', 'systems', 'prompts', 
                           'max_tokens', 'tempurature', 'hf_token'] 
                if key in config_json
            }
        log(f"Failed to fetch config: {response.status_code}", False)
        return None
    except Exception as e:
        log(f"Error fetching config: {e}", False)
        return None

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_random(min=0.1, max=MAX_RETRY_DELAY), reraise=True)
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
                    async with asyncio.timeout(30):
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
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: 30.0s (Timeout)")
                    return provider, name, 30.0, None
                except Exception:
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: API Error")
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

async def load_source_dataset():
    try:
        source = config.get('src')
        if not source:
            raise ValueError("No source dataset in config")
        dataset = load_dataset(source, split="english")
        total_records = len(dataset)
        total_stakeholders = sum(
            len(record.get('stakeholders', {}).get('stakeholder', []))
            for record in dataset
        )
        log(f"Dataset loaded successfully:")
        log(f"- source: {source}")
        log(f"- total records: {total_records}")
        log(f"- total stakeholders: {total_stakeholders}")
        log(f"- total generations needed: {total_stakeholders * 2}")
        log(f"- average stakeholders per record: {total_stakeholders/total_records:.2f}")
        return dataset
    except Exception as e:
        log(f"Error loading dataset '{config.get('src')}': {e}", False)
        return None

async def mock_generate_case_study(prompt, endpoint_config):
    start_time = time.time()
    elapsed_time = round(time.time() - start_time, 3)
    return "", elapsed_time

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

async def upload_results(prepared_records: list, destination: str) -> bool:
    try:
        english_records = []
        chinese_records = []
        english_failed_records = []
        chinese_failed_records = []
        available_endpoints = config.get('endpoints', [])
        endpoints_count = len(available_endpoints)
        if not endpoints_count:
            log("Warning: No endpoints configured for distribution")
        
        def process_records(records, start_id=1):
            processed = []
            for idx, record in enumerate(records):
                processed.append({
                    "id": start_id + idx,
                    "case_study_info": record.get("case_study_info", ""),
                    "prompt": record.get("prompt", ""),
                    "original_info": record.get("original_info", ""),
                    "stakeholder": record.get("stakeholder", ""),
                    "motivation": record.get("motivation", ""),
                    "elapsed_time": record.get("elapsed_time", 0.0),
                    "endpoint": record.get("endpoint", "")
                })
            return processed
        
        async def process_language_record(record, language, endpoint_config, endpoint_formatted):
            language_key = 'en' if language == 'english' else 'zh'
            error_key = f"{language_key}_error"
            target_list = english_records if language == 'english' else chinese_records
            failed_list = english_failed_records if language == 'english' else chinese_failed_records
            
            if 'prompts' in record and language_key in record['prompts'] and record['prompts'][language_key]:
                case_study_info, elapsed_time = await mock_generate_case_study(record['prompts'][language_key], endpoint_config)
                target_list.append({
                    "case_study_info": case_study_info,
                    "original_info": record['case_study_info'],
                    "prompt": record['prompts'][language_key],
                    "stakeholder": record.get('stakeholder', ''),
                    "motivation": record.get('motivation', ''),
                    "elapsed_time": elapsed_time,
                    "endpoint": endpoint_formatted
                })
            else:
                error_msg = record.get(error_key, f"Failed to generate {language} prompt")
                failed_list.append({
                    "case_study_info": "",
                    "original_info": record['case_study_info'],
                    "prompt": "",
                    "stakeholder": record.get('stakeholder', ''),
                    "motivation": record.get('motivation', ''),
                    "elapsed_time": 0.0,
                    "endpoint": f"{endpoint_formatted} : error - {error_msg}"
                })
        
        for idx, record in enumerate(prepared_records):
            endpoint_config = None
            endpoint_formatted = "unknown"
            if available_endpoints:
                endpoint_config = available_endpoints[idx % endpoints_count]
                endpoint_formatted = format_endpoint(endpoint_config)
            
            # Process both English and Chinese records using the helper function
            await process_language_record(record, 'english', endpoint_config, endpoint_formatted)
            await process_language_record(record, 'chinese', endpoint_config, endpoint_formatted)
        
        # Process records and assign IDs within each split
        english_records = process_records(english_records, 1)
        chinese_records = process_records(chinese_records, 1)
        english_failed_records = process_records(english_failed_records, 1)
        chinese_failed_records = process_records(chinese_failed_records, 1)
        
        total_records = len(prepared_records)
        log(f"Preparing to upload dataset to {destination}")
        log(f"- Total stakeholders processed: {total_records}")
        log(f"- Successful English records: {len(english_records)} ({len(english_records)/total_records*100:.1f}%)")
        log(f"- Failed English records: {len(english_failed_records)} ({len(english_failed_records)/total_records*100:.1f}%)")
        log(f"- Successful Chinese records: {len(chinese_records)} ({len(chinese_records)/total_records*100:.1f}%)")
        log(f"- Failed Chinese records: {len(chinese_failed_records)} ({len(chinese_failed_records)/total_records*100:.1f}%)")
        log(f"- Total successful records: {len(english_records) + len(chinese_records)}")
        log(f"- Total failed records: {len(english_failed_records) + len(chinese_failed_records)}")
        log(f"- Endpoints used: {endpoints_count}")
        
        try:
            dataset_splits = {
                'english': Dataset.from_list(english_records),
                'chinese': Dataset.from_list(chinese_records),
            }
            if english_failed_records:
                dataset_splits['english_failed'] = Dataset.from_list(english_failed_records)
            if chinese_failed_records:
                dataset_splits['chinese_failed'] = Dataset.from_list(chinese_failed_records)
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
            # Use HF token from config instead of hardcoded value
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
        log(f"- Total successful records: {len(english_records) + len(chinese_records)}")
        log(f"- English successful: {len(english_records)}")
        log(f"- Chinese successful: {len(chinese_records)}")
        failed_total = len(english_failed_records) + len(chinese_failed_records)
        if failed_total > 0:
            log(f"- Total failed records: {failed_total}")
            if english_failed_records:
                log(f"- English failed: {len(english_failed_records)}")
            if chinese_failed_records:
                log(f"- Chinese failed: {len(chinese_failed_records)}")
        return True
    except Exception as e:
        log(f"Error uploading results: {type(e).__name__}: {str(e)}", True)
        return False

async def dataset_exists(name: str) -> bool:
    try:
        return bool(HfApi().dataset_info(name))
    except:
        return False

async def prepare_prompt(case_study_info: str, stakeholder: str, motivation: str, language: str) -> str:
    if not case_study_info or not stakeholder:
        return None
    system_prompt = config['systems'].get(language, "")
    prompt_template = config['prompts'].get(language, "")
    if not prompt_template or not system_prompt:
        log(f"No template/system found for language: {language}", False)
        return None
    return prompt_template.format(
        case_study_info=case_study_info.strip(),
        stakeholder=stakeholder.strip(),
        motivation=motivation.strip() or "Unknown motivations or intentions"
    )

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
        cleaned_line = cleaned_line.lstrip('-').lstrip('*').lstrip('•').strip()
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
                        log(f"Skipping stakeholder in record {idx}: Empty after cleaning", False)
            else:
                skipped += 1
                log(f"Skipping record {idx}: Invalid stakeholders structure", False)
        except Exception as ex:
            log(f"Error expanding record {idx}: {ex}", False)
            skipped += 1
    avg_stakeholders = sum(stakeholder_counts) / len(stakeholder_counts) if stakeholder_counts else 0
    max_stakeholders = max(stakeholder_counts) if stakeholder_counts else 0
    log(f"Dataset expansion statistics:")
    log(f"- Original records: {total_records}")
    log(f"- Valid records: {valid}")
    log(f"- Skipped records: {skipped}")
    log(f"- Total stakeholders: {len(expanded)}")
    log(f"- Stakeholders cleaned: {cleaned_count}")
    log(f"- Total generations needed: {len(expanded) * 2}")
    log(f"- Average stakeholders per valid record: {avg_stakeholders:.2f}")
    log(f"- Max stakeholders in a record: {max_stakeholders}")
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
    log(f"- Records with at least one language: {len(prepared_records)}")
    log(f"- English prompts successful: {successful_english}/{total_stakeholders} ({successful_english/total_stakeholders*100:.1f}%)")
    log(f"- Chinese prompts successful: {successful_chinese}/{total_stakeholders} ({successful_chinese/total_stakeholders*100:.1f}%)")
    log(f"- Records with both languages: {total_stakeholders - failed_english - failed_chinese - failed_both}")
    log(f"- Records with English only: {failed_chinese - failed_both}")
    log(f"- Records with Chinese only: {failed_english - failed_both}")
    log(f"- Records with neither language: {failed_both}")
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
    case_studies_dir = os.path.join(output_path, "data/case_studies")
    temp_dir = os.path.join(output_path, "data/temp")
    for directory in [data_dir, case_studies_dir, temp_dir]:
        os.makedirs(directory, exist_ok=True)
    return {
        "run_id": run_id,
        "output_path": output_path,
        "log_dir": log_dir,
        "data_dir": data_dir,
        "case_studies_dir": case_studies_dir,
        "temp_dir": temp_dir,
        "workers": args.workers or 5,
        "endpoints_count": len(config['endpoints'])
    }

async def test_endpoints(workers_count):
    semaphore = asyncio.Semaphore(workers_count)
    log(f"Starting endpoint tests with {workers_count} parallel workers")
    test_results = await tqdm_asyncio.gather(
        *[test_endpoint(endpoint, semaphore) for endpoint in config["endpoints"]],
        desc="Testing endpoints"
    )
    console_logger.info("Test results:")
    for provider, name, test_time, result in test_results:
        status = "OK" if result == "OK" else "Fail"
        console_logger.info(f"- endpoint {status}! [ {provider}-{name}: {test_time}s ]")
    valid_times = [tt for _, _, tt, _ in test_results if tt]
    if valid_times:
        avg_time = round(sum(valid_times) / len(valid_times), 2)
        console_logger.info(f"- average time: {avg_time}s")
    provider_stats = {}
    for provider, _, _, result in test_results:
        if provider not in provider_stats:
            provider_stats[provider] = {"total": 0, "success": 0}
        provider_stats[provider]["total"] += 1
        if result == "OK":
            provider_stats[provider]["success"] += 1
    console_logger.info("Provider summary:")
    for provider, stats in provider_stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        console_logger.info(f"- {provider}: {stats['success']}/{stats['total']} endpoints ok ({success_rate:.1f}%)")

async def main(args):
    try:
        dirs = await setup_directories(args)
        for key, value in dirs.items():
            log(f"{key.replace('_', ' ').title()}: {value}")
        required_keys = ['model', 'max_tokens', 'tempurature', 'systems', 'prompts']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")
        log(f"Config loaded:")
        for key in ['model', 'max_tokens', 'tempurature']:
            if key in config:
                log(f"- {key}: {config[key]}")
        if not isinstance(config, dict) or 'endpoints' not in config:
            raise ValueError("Invalid config")
        await test_endpoints(dirs["workers"])
        log("Loading dataset...")
        dataset = await load_source_dataset()
        if not dataset:
            raise ValueError("Failed to load dataset")
        log("Expanding dataset records...")
        expanded_records = await expand_dataset(dataset)
        log("Preparing prompts...")
        prepared_records = await prepare_all_prompts(expanded_records)
        destination = config.get('dest')
        if not destination:
            raise ValueError("No destination dataset in config")
        
        # Check for the HF token in the config
        if "hf_token" in config:
            log("HF_TOKEN found in config")
        else:
            log("Warning: No HF_TOKEN found in config. Authentication may fail.")
        
        upload_success = await upload_results(prepared_records, destination)
        if not upload_success:
            raise ValueError("Failed to upload dataset")
        log(f"Successfully initialized dataset structure at {destination}")
    except Exception as e:
        log(f"Fatal error: {str(e)}", True)
        raise e

if __name__ == "__main__":
    parser = ap.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG_URL)
    parser.add_argument("--output", default=os.getcwd())
    parser.add_argument("--log-dir")
    parser.add_argument("--workers", type=int)
    args = parser.parse_args()
    DEFAULT_CONFIG_URL = args.config
    try:
        global console_logger, file_logger, config
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