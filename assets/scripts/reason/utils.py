import os
import time
import requests

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

def should_retry_exception(exception):
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
