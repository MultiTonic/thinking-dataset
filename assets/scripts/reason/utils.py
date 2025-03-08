import os
import time
import json
import requests
from telemetry import Telemetry
from validator import validator

def check_min_length(response_text: str, min_length: int):
    """
    Check if a response text meets the minimum length requirement.
    
    Args:
        response_text: The text to check
        min_length: The minimum required length
        
    Returns:
        bool: True if the text meets the minimum length or min_length is 0
        
    Raises:
        ValueError: If the text is shorter than the minimum required length
    """
    if min_length and len(response_text) < min_length:
        raise ValueError(f"Response length {len(response_text)} is shorter than minimum required length {min_length}")
    return True

def should_retry(exception):
    """
    Determine if an exception should trigger a retry.
    
    Args:
        exception: The exception to evaluate
        
    Returns:
        bool: True if the exception should trigger a retry, False otherwise
    """
    if isinstance(exception, ValueError) and "shorter than minimum required length" in str(exception):
        return True
    
    error_message = str(exception).lower()
    if "429" in error_message or "too many tokens" in error_message or "rate limit" in error_message:
        return True
        
    if "timeout" in error_message:
        return True
        
    return False

def create_chat_messages(query, response, split, category, config, file_logger=None, test_mode=False):
    """
    Create a structured chat message list for API calls.
    
    Args:
        query: The query text
        response: The response text
        split: The split name
        category: The content category
        config: Configuration dictionary with systems and metacogs
        file_logger: Optional logger for file output
        test_mode: Whether in test mode
        
    Returns:
        tuple: (messages_list, metacog_prompt)
        
    Raises:
        ValueError: If the category is not supported
    """
    if category not in ["dark_thoughts", "benign"]:
        raise ValueError(f"Invalid category '{category}' - must be 'dark_thoughts' or 'benign'")
    
    language_code = config["splits"].get(split, "")
    system_prompts = config.get("systems", {})
    metacog_prompts = config.get("metacogs", {})
    
    system_prompt = system_prompts[category][language_code]
    metacog_prompt = metacog_prompts[category][language_code]
    
    if file_logger and not test_mode:
        file_logger.info(f"Chat created for category '{category}': system {len(system_prompt)}, query {len(query)}, response {len(response)}, metacog {len(metacog_prompt)} chars")
        
    return [
        {"role":"system","content":system_prompt},
        {"role":"user","content":query},
        {"role":"assistant","content":response},
        {"role":"user","content":metacog_prompt}
    ], metacog_prompt

async def setup_dirs(args):
    """
    Create directory structure for the processing run.
    
    Args:
        args: Command line arguments with output and log_dir properties
        
    Returns:
        dict: Dictionary containing paths for different directories
    """
    run_id = str(int(time.time()))
    output_path = os.path.abspath(args.output)
    log_directory = args.log_dir or os.path.join(output_path, "logs")
    
    data_directory = os.path.join(output_path, "data")
    run_directory = os.path.join(data_directory, run_id)
    case_study_directory = os.path.join(run_directory, "case_study")
    temp_directory = os.path.join(run_directory, "temp")
    checkpoint_directory = os.path.join(run_directory, "checkpoints")
    
    # Create all required directories
    for directory in [data_directory, run_directory, case_study_directory, temp_directory, checkpoint_directory]:
        os.makedirs(directory, exist_ok=True)
    
    return {
        "r": run_id,
        "o": output_path,
        "l": log_directory,
        "d": data_directory, 
        "rd": run_directory,
        "cs": case_study_directory,
        "t": temp_directory,
        "ck": checkpoint_directory
    }

async def fetch_config(url, logger=None):
    """
    Fetch configuration from a URL and parse it as JSON.
    
    Args:
        url: URL to fetch configuration from
        logger: Optional logging function
        
    Returns:
        dict: Parsed JSON configuration or None if failed
    """
    try:
        if logger: logger(f"Fetching config from: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            config_json = response.json()
            if logger: logger("Config fetched successfully")
            return config_json
        if logger: logger(f"Failed to fetch config: {response.status_code}")
        return None
    except Exception as error:
        if logger: logger(f"Error fetching config: {error}")
        return None

def find_latest_run(data_dir):
    """
    Find the most recent run directory in the data directory.
    
    Args:
        data_dir: Path to the data directory
        
    Returns:
        str: Path to the most recent run directory, or None if no runs found
    """
    try:
        if not os.path.exists(data_dir):
            return None
        
        run_dirs = []
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path) and item.isdigit():
                # Convert directory name (timestamp) to int for sorting
                run_dirs.append((int(item), item_path))
        
        if not run_dirs:
            return None
            
        # Sort by timestamp (first element in tuple) in descending order
        sorted_runs = sorted(run_dirs, key=lambda x: x[0], reverse=True)
        # Return the path (second element in tuple)
        return sorted_runs[0][1]
    except Exception:
        return None

async def setup_env(arguments, log_fn=None):
    """Set up the runtime environment based on arguments"""
    telemetry_stats = Telemetry()
    
    if arguments.test:
        return telemetry_stats, {}
    
    if arguments.resume:
        # Try to find the latest run directory
        data_dir = os.path.join(os.path.abspath(arguments.output), "data")
        latest_run_dir = find_latest_run(data_dir)
        
        if latest_run_dir and log_fn:
            run_id = os.path.basename(latest_run_dir)
            log_fn(f"Resuming from previous run: {run_id}")
            
            # Set up directories using the existing run_id
            directories = {
                "r": run_id,
                "o": os.path.abspath(arguments.output),
                "l": arguments.log_dir,
                "d": data_dir,
                "rd": latest_run_dir,
                "cs": os.path.join(latest_run_dir, "case_study"),
                "t": os.path.join(latest_run_dir, "temp"),
                "ck": os.path.join(latest_run_dir, "checkpoints"),
            }
            
            # Check if a state file exists
            state_file = os.path.join(latest_run_dir, "processing_state.json")
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                    
                    directories["resume_state"] = state
                    log_fn(f"Found processing state:")
                    log_fn(f"- Last batch: {state.get('batch_index', 'unknown')}")
                    log_fn(f"- Records processed: {state.get('total_processed', 0)}")
                    log_fn(f"- Last split: {state.get('split_name', 'unknown')}")
                except Exception as e:
                    log_fn(f"Warning: Could not load processing state: {str(e)}")
            
            return telemetry_stats, directories
    
    # Create new directories for a fresh run
    directories = await setup_dirs(arguments) 
    
    if log_fn:
        log_fn(f"Run ID: {directories['r']}")
        log_fn(f"Data dir: {directories['d']}")
        log_fn(f"Config URL: {arguments.config}")
    
    return telemetry_stats, directories

async def load_config(config_url, log_fn=None):
    """Load and validate the configuration"""
    config = await fetch_config(config_url, logger=log_fn)
    if not config:
        if log_fn: log_fn("Failed to load config")
        return None
    
    is_valid, validation_message = await validator(config)
    if not is_valid:
        if log_fn: log_fn(f"Invalid configuration: {validation_message}")
        return None
        
    if log_fn: log_fn("Config successfully loaded")
    return config
