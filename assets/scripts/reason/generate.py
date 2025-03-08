import asyncio
import time
import os

from utils import create_chat_messages, check_min_length, check_max_length
from api import call_openai, call_ollama

async def generate_thinking(row, split_name, endpoint_idx, endpoints, config, telemetry_stats, 
                           request_timeout, endpoint_cooldown, directories, logger, file_logger, test_mode):
    """
    Generate thinking output for a record using the specified endpoint.
    
    Args:
        row: The data record
        split_name: Name of the dataset split
        endpoint_idx: Index of the endpoint to use
        endpoints: List of available endpoints
        config: Configuration dictionary
        telemetry_stats: Statistics tracking object
        request_timeout: Timeout for API requests
        endpoint_cooldown: Cooldown period for endpoints
        directories: Dictionary with directory paths
        logger: Logging function
        file_logger: File logger
        test_mode: Whether in test mode
        
    Returns:
        tuple: (generated_thinking, elapsed_time, metacog_prompt, endpoint_name)
    """
    start_time = time.time()
    endpoint_config = endpoints[endpoint_idx]
    endpoint_config['in_use'] = True
    provider = endpoint_config.get('p', 'unknown').lower()
    name = endpoint_config.get('n', 'unknown')
    endpoint_name = f"{provider}-{name}"
    
    # Get record ID for telemetry
    record_id = str(row.get('id', endpoint_idx))
    
    # Log that we're starting to process this record with this endpoint
    logger(f"[{record_id}] Starting request with endpoint {endpoint_name}")
    
    try:
        # Get query and response columns
        query_column = config['columns']['query']
        response_column = config['columns']['response']
        
        # Get query and response text
        query_text = row[query_column]
        response_text = row[response_column]
        
        # Determine category - default to benign if not provided
        category = row.get('category', 'benign')
        if category not in ['dark_thoughts', 'benign']:
            category = 'benign'
            
        # Create the messages for the API call
        messages, metacog_prompt = create_chat_messages(
            query_text, response_text, split_name, category, 
            config, file_logger=file_logger, test_mode=test_mode
        )
        
        try:
            # Set up the API call with timeout
            async with asyncio.timeout(request_timeout):
                # Use the appropriate API caller based on provider
                if provider == 'openai':
                    thinking = await call_openai(endpoint_config, messages, config)
                elif provider == 'ollama':
                    thinking = await call_ollama(endpoint_config, messages, config)
                else:
                    raise ValueError(f"Unsupported API provider: {provider}")
                    
                # Check if the response meets minimum length requirement
                min_length = config.get('min_length', 0)
                check_min_length(thinking, min_length)
                
                # Check if the response exceeds maximum length (potential hallucination)
                max_tokens = config.get('max_tokens', 4096)
                check_max_length(thinking, max_tokens)
                
                # Save the successful response to a temp file
                if not test_mode and directories and "t" in directories and thinking:
                    # Get language code for this split
                    lang_code = config["splits"].get(split_name)
                    if lang_code:
                        # Create path for temp directory
                        temp_dir = os.path.join(directories["t"], lang_code)
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # Create file path with record ID
                        file_path = os.path.join(temp_dir, f"{record_id}.txt")
                        
                        try:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(thinking)
                            logger(f"[{record_id}] Saved thinking output to temp file: {file_path}")
                        except Exception as write_err:
                            logger(f"[{record_id}] Warning: Failed to save response to temp file: {str(write_err)}")
                
        except asyncio.TimeoutError:
            logger(f"[{record_id}] Request timed out after {request_timeout}s")
            # Mark as a special timeout error that should be retried
            error = asyncio.TimeoutError("Request timed out")
            # Pass the endpoint index with the error to help identify which endpoint had issues
            setattr(error, 'endpoint_idx', endpoint_idx)
            
            endpoint_config['last_call'] = time.time()
            endpoint_config['in_use'] = False
            telemetry_stats.log_failure(split_name, record_id, "TimeoutError")
            raise error
        except Exception as e:
            # Mark the endpoint with rate limit flag if needed
            if "429" in str(e) or "too many tokens" in str(e) or "rate limit" in str(e).lower():
                endpoint_config['rate_limited'] = True
                logger(f"[{record_id}] Rate limit hit on {endpoint_name}")
                
            # Pass the endpoint index with the error to help identify which endpoint had issues
            setattr(e, 'endpoint_idx', endpoint_idx)
            
            endpoint_config['last_call'] = time.time()
            endpoint_config['in_use'] = False
            # Fixed: Pass record_id as the second argument 
            telemetry_stats.log_failure(split_name, record_id, type(e).__name__)
            raise
            
        # Track successful processing
        elapsed_time = round(time.time() - start_time, 3)
        endpoint_config['last_call'] = time.time()
        endpoint_config['in_use'] = False
        telemetry_stats.log_success(split_name, elapsed_time)
        
        return thinking, elapsed_time, metacog_prompt, endpoint_name
            
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 3) if 'start_time' in locals() else 0.0
        if 'endpoint_config' in locals():
            endpoint_config['last_call'] = time.time()
            endpoint_config['in_use'] = False
            
        # Add endpoint index to the exception for handling in retry logic
        setattr(e, 'endpoint_idx', endpoint_idx)
        raise
