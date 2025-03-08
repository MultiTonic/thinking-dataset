import asyncio
import os
import time
from asyncio import TimeoutError

from api import call_ollama_api, call_openai_api
from utils import check_min_length, create_chat_messages

async def generate_thinking(record, split, endpoint_idx, endpoints, config, telemetry_stats, 
                            request_timeout, endpoint_cooldown, dirs=None, logger=None, 
                            file_logger=None, test_mode=False):
    """
    Generate a thinking/reasoning response for a given record.
    
    Args:
        record: The record to process
        split: The dataset split name
        endpoint_idx: Index of the endpoint to use from endpoints list
        endpoints: List of available endpoints
        config: Main configuration dictionary
        telemetry_stats: TelemetryStats instance for tracking metrics
        request_timeout: Timeout for the API request in seconds
        endpoint_cooldown: Cooldown period for endpoints in seconds
        dirs: Dictionary with directory paths
        logger: Function for logging
        file_logger: Logger for detailed file logging
        test_mode: Whether running in test mode
    
    Returns:
        tuple: (result_text, elapsed_time, metacog_prompt, endpoint_name)
        
    Raises:
        ValueError: If the input is invalid or API call fails
        TimeoutError: If the API request times out
    """
    endpoint_config = endpoints[endpoint_idx]
    endpoint_config['in_use'] = True
    
    try:
        record_id = record.get('id', '')
        
        start_time = time.time()
        provider = endpoint_config.get('p', '').lower()
        name = endpoint_config.get('n', '')
        query_col = config['columns']['query']
        response_col = config['columns']['response']
        query_text = record.get(query_col, "")
        response_text = record.get(response_col, "")
        
        category = record.get('category')
        
        lang_code = config["splits"].get(split, "")
        
        min_length = config.get('min_length', 0)
        
        endpoint_name = f"{provider}-{name}"
        
        if logger:
            logger(f"[{record_id}] Starting request to {endpoint_name} for category '{category}'")
        
        if file_logger and not test_mode:
            file_logger.info(f"[{record_id}] Processing: {provider}-{name}, split '{split}', "
                            f"category '{category}', query {len(query_text)} chars, "
                            f"response {len(response_text)} chars")
        
        if not query_text or not response_text:
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time()
            if logger:
                logger(f"[{record_id}] ERROR: Empty input query or response")
            telemetry_stats.log_failure(record_id, split, "EmptyInput")
            raise ValueError("Empty input query or response")
        
        try:
            messages, metacog_prompt = create_chat_messages(
                query_text, response_text, split, category, config, file_logger, test_mode)
                
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Created chat messages with {len(messages)} items")
        except Exception as e:
            if logger:
                logger(f"[{record_id}] Error creating chat messages: {str(e)}")
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Error creating chat messages: {str(e)}")
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time()
            telemetry_stats.log_failure(record_id, split, "PromptError")
            raise
        
        if logger:
            logger(f"[{record_id}] Sending request to {provider}-{name} "
                  f"({config['max_tokens']} max tokens, temperature {config['temperature']})")
        
        try:
            async with asyncio.timeout(request_timeout):
                if provider == "openai":
                    result = await call_openai_api(endpoint_config, messages, config)
                elif provider == "ollama":
                    result = await call_ollama_api(endpoint_config, messages, config)
                else:
                    endpoint_config['in_use'] = False
                    endpoint_config['last_call'] = time.time()
                    if logger:
                        logger(f"[{record_id}] ERROR: Unknown provider type: {provider}")
                    telemetry_stats.log_failure(record_id, split, "UnknownProvider")
                    raise ValueError(f"Unknown provider type: {provider}")
        except TimeoutError:
            if logger:
                logger(f"[{record_id}] ERROR: Request timeout after {request_timeout}s for {provider}-{name}")
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Request timeout after {request_timeout}s for {provider}-{name}")
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time() if provider == "ollama" else time.time() + endpoint_cooldown/2
            telemetry_stats.log_failure(record_id, split, "Timeout")
            raise
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "TOO MANY" in err_msg or "rate limit" in err_msg.lower():
                if logger:
                    logger(f"[{record_id}] Rate limit hit on {provider}-{name}")
                if file_logger and not test_mode:
                    file_logger.info(f"[{record_id}] ERROR: API call failed: {err_msg}")
            else:
                if logger:
                    logger(f"[{record_id}] ERROR: API call failed: {err_msg}")
                if file_logger and not test_mode:
                    file_logger.info(f"[{record_id}] ERROR: API call failed: {err_msg}")
            
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time()
            error_type = "RateLimit" if "429" in err_msg or "rate limit" in err_msg.lower() else type(e).__name__
            telemetry_stats.log_failure(record_id, split, error_type)
            raise
            
        elapsed_time = round(time.time() - start_time, 2)
        
        try:
            check_min_length(result, min_length)
            if logger:
                logger(f"[{record_id}] Response received ({len(result)} chars) in {elapsed_time:.2f}s")
        except ValueError as e:
            if logger:
                logger(f"[{record_id}] ERROR: Response too short: {str(e)}")
            if file_logger and not test_mode:
                file_logger.info(f"[{record_id}] Response too short: {str(e)}")
                
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time()
            
            telemetry_stats.log_failure(record_id, split, "ResponseTooShort")
            raise
        
        if not test_mode and dirs and "t" in dirs:
            temp_dir = os.path.join(dirs["t"], lang_code)
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, f"{record_id}.txt")
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                if file_logger:
                    file_logger.info(f"[{record_id}] Saved response to {temp_file}")
            except Exception:
                pass
            
        endpoint_config['in_use'] = False
        endpoint_config['last_call'] = time.time()
        
        if logger:
            logger(f"[{record_id}] Successfully generated reasoning ({len(result)} chars) in {elapsed_time:.2f}s using {provider}-{name}")
        if file_logger and not test_mode:
            file_logger.info(f"[{record_id}] Generated reasoning ({len(result)} chars) in {elapsed_time:.2f}s using {provider}-{name}")
        
        telemetry_stats.log_success(record_id, split)
        
        current_time = time.time()
        if hasattr(telemetry_stats, 'last_log_time') and current_time - telemetry_stats.last_log_time > 30:
            total_records_estimate = config.get('max_records', 100) or 100
            if logger and hasattr(telemetry_stats, 'get_telemetry_string'):
                logger(telemetry_stats.get_telemetry_string(total_records_estimate))
                telemetry_stats.last_log_time = current_time
            
        return result, elapsed_time, metacog_prompt, endpoint_name
    except Exception as e:
        if 'endpoint_config' in locals():
            endpoint_config['in_use'] = False
            endpoint_config['last_call'] = time.time()
            
        if 'record_id' in locals() and 'split' in locals() and hasattr(telemetry_stats, 'log_failure'):
            error_type = type(e).__name__
            telemetry_stats.log_failure(record_id, split, error_type)
        raise
