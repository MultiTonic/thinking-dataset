import random
import time
import asyncio
from asyncio import TimeoutError

from openai import AsyncOpenAI
from ollama import AsyncClient
from tenacity import retry, stop_after_attempt, wait_random

def initialize_endpoints(endpoints_config):
    """
    Initialize endpoints with status tracking fields.
    
    Args:
        endpoints_config: List of endpoint configurations from the config
        
    Returns:
        list: Endpoints with added tracking fields
    """
    endpoints = []
    for endpoint in endpoints_config:
        endpoints.append({
            **endpoint,
            'last_call': 0,
            'in_use': False
        })
    random.shuffle(endpoints)
    return endpoints

def get_next_endpoint(endpoints, endpoint_cooldown, logger=None):
    """
    Get the next available endpoint or wait for one to become available.
    
    Args:
        endpoints: List of endpoints with tracking fields
        endpoint_cooldown: Cooldown period in seconds
        logger: Optional logging function
        
    Returns:
        int: Index of the next available endpoint
    """
    current_time = time.time()
    available_endpoints = []
    
    # Find all available endpoints that aren't cooling down or in use
    for endpoint_index, endpoint_config in enumerate(endpoints):
        provider = endpoint_config.get('p', '').lower()
        if not endpoint_config['in_use'] and (provider == "ollama" or current_time - endpoint_config['last_call'] >= endpoint_cooldown):
            available_endpoints.append((endpoint_index, endpoint_config))
    
    # If no endpoints are available, find the one that will be available soonest
    if not available_endpoints:
        soonest_ready_endpoint = min(endpoints, key=lambda endpoint: 
            endpoint['last_call'] if endpoint.get('p','').lower() == "ollama" else (
                endpoint['last_call'] + endpoint_cooldown if not endpoint['in_use'] else float('inf')))
        endpoint_index = endpoints.index(soonest_ready_endpoint)
        
        # If it's not an Ollama endpoint, we need to wait for the cooldown
        if soonest_ready_endpoint.get('p','').lower() != "ollama":
            wait_time = max(0, (soonest_ready_endpoint['last_call'] + endpoint_cooldown) - current_time)
            if wait_time > 0 and logger:
                logger(f"All endpoints busy or cooling down, will wait {wait_time:.2f}s for next available")
                time.sleep(wait_time)
        return endpoint_index
    
    # Sort by last call time so we pick the one that's been idle longest
    available_endpoints.sort(key=lambda x: x[1]['last_call'])
    return available_endpoints[0][0]

async def test_openai_endpoint(endpoint_config, messages, _):
    """Call OpenAI API for endpoint testing"""
    async with AsyncOpenAI(base_url=endpoint_config['u'], api_key=endpoint_config.get('k', '')) as client:
        return await client.chat.completions.create(
            model=endpoint_config['m'],
            messages=messages,
            max_tokens=10,
            temperature=0,
            stream=False
        )

async def test_ollama_endpoint(endpoint_config, messages, _):
    """Call Ollama API for endpoint testing"""
    client = AsyncClient(host=endpoint_config['u'])
    return await client.chat(
        model=endpoint_config['m'],
        messages=messages,
        stream=False,
        options={"temperature": 0, "num_predict": 10, "num_ctx": 4096}
    )

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2), reraise=True)
async def test_endpoint(endpoint_config, test_timeout, semaphore, logger=None, file_logger=None, test_mode=False):
    """
    Test a specific endpoint to verify its availability.
    
    Args:
        endpoint_config: Dictionary with endpoint configuration
        test_timeout: Timeout in seconds for the test call
        semaphore: Asyncio semaphore to limit concurrent calls
        logger: Function to log messages to console
        file_logger: Logger for recording to file
        test_mode: Whether we're in test mode
        
    Returns:
        tuple: (provider, name, elapsed_time, response_content)
    """
    async with semaphore:
        try:
            start_time = time.time()
            provider = endpoint_config.get('p', 'unknown')
            name = endpoint_config.get('n', 'unknown')
            provider_lower = provider.lower()
            msg = [
                {"role": "system", "content": "Test message"},
                {"role": "user", "content": "Respond with 'OK' if you can read this."}
            ]
            
            try:
                async with asyncio.timeout(test_timeout):
                    if provider_lower == "openai":
                        response = await test_openai_endpoint(endpoint_config, msg, None)
                    elif provider_lower == "ollama":
                        response = await test_ollama_endpoint(endpoint_config, msg, None)
                    else:
                        if logger: logger(f"Unknown provider type: {provider_lower}")
                        return provider, name, 0.0, None
            except TimeoutError:
                if not test_mode and file_logger:
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: {test_timeout}s (Timeout)")
                return provider, name, test_timeout, None
            except Exception as e:
                error_msg = str(e)
                if not test_mode and file_logger:
                    file_logger.info(f"Endpoint Fail: {provider}-{name}: API Error - {error_msg}")
                if "429" in error_msg or "TOO MANY TOKENS" in error_msg or "rate limit" in error_msg.lower():
                    if logger: logger(f"Rate limit detected for endpoint {provider}-{name}, considering it valid but busy")
                    await asyncio.sleep(3)
                    return provider, name, 0.1, "RATE_LIMITED"
                raise
                
            elapsed_time = round(time.time() - start_time, 2)
            
            if provider_lower == "openai" and response and response.choices and response.choices[0].message:
                if not test_mode and file_logger:
                    file_logger.info(f"Endpoint OK: {provider}-{name}: {elapsed_time}s")
                return provider, name, elapsed_time, response.choices[0].message.content
            elif provider_lower == "ollama" and response and response.message and response.message.content:
                if not test_mode and file_logger:
                    file_logger.info(f"Endpoint OK: {provider}-{name}: {elapsed_time}s")
                return provider, name, elapsed_time, response.message.content
                
            if not test_mode and file_logger:
                file_logger.info(f"Endpoint Fail: {provider}-{name}: {elapsed_time}s (No Response)")
            return provider, name, elapsed_time, None
            
        except Exception as e:
            if not test_mode and file_logger:
                file_logger.info(f"Endpoint Fail: {provider}-{name}: {str(e)}")
            raise

async def test_all_endpoints(endpoints_config, worker_count, test_timeout, logger=None, console_logger=None, file_logger=None, test_mode=False):
    """
    Test all endpoints in the configuration to determine which ones are working.
    
    Args:
        endpoints_config: List of endpoint configurations to test
        worker_count: Maximum number of concurrent tests
        test_timeout: Timeout in seconds for each test
        logger: Function to log messages
        console_logger: Logger for console output 
        file_logger: Logger for file recording
        test_mode: Whether we're in test mode
        
    Returns:
        tuple: (working_count, working_indices)
    """
    semaphore = asyncio.Semaphore(worker_count)
    
    if logger:
        logger(f"Starting endpoint tests with {worker_count} parallel workers (timeout: {test_timeout}s)")
    
    test_results = []
    test_tasks = []
    
    for i, endpoint in enumerate(endpoints_config):
        test_tasks.append(test_endpoint(endpoint, test_timeout, semaphore, logger, file_logger, test_mode))
    
    results = await asyncio.gather(*test_tasks, return_exceptions=True)
    working_indices = []
    
    for i, result in enumerate(results):
        endpoint = endpoints_config[i]
        if isinstance(result, Exception):
            if logger:
                logger(f"Error testing endpoint {i+1}/{len(endpoints_config)}: {str(result)}")
            test_results.append((endpoint.get('p', 'unknown'), endpoint.get('n', 'unknown'), 0.0, None))
        else:
            provider, name, test_time, response = result
            is_ok = response == "OK" or response == "RATE_LIMITED"
            status = "OK" if response == "OK" else "Rate Limited" if response == "RATE_LIMITED" else "Failed"
            
            if logger:
                logger(f"Tested endpoint {i+1}/{len(endpoints_config)}: {provider}-{name} - {status}")
                
            test_results.append(result)
            
            if is_ok:
                working_indices.append(i)
    
    if console_logger:
        console_logger.info("Test results:")
        for provider, name, test_time, response in test_results:
            if response == "RATE_LIMITED":
                status = "Rate Limited"
                console_logger.info(f"- endpoint {status}! [ {provider}-{name}: rate limited ]")
            else:
                status = "OK" if response == "OK" else "Fail"
                console_logger.info(f"- endpoint {status}! [ {provider}-{name}: {test_time}s ]")
        
        times = [tt for _, _, tt, response in test_results if response == "OK" and tt]
        if times:
            avg = round(sum(times) / len(times), 2)
            console_logger.info(f"- average time: {avg}s")
        
        stats = {}
        for provider, _, _, response in test_results:
            if provider not in stats:
                stats[provider] = {"total": 0, "success": 0}
            stats[provider]["total"] += 1
            if response == "OK" or response == "RATE_LIMITED":
                stats[provider]["success"] += 1
                
        console_logger.info("Provider summary:")
        for provider, stat in stats.items():
            success_rate = (stat["success"] / stat["total"]) * 100 if stat["total"] > 0 else 0
            console_logger.info(f"- {provider}: {stat['success']}/{stat['total']} endpoints ok ({success_rate:.1f}%)")
    
    working_count = sum(1 for _, _, _, response in test_results if response == "OK" or response == "RATE_LIMITED")
    return working_count, working_indices
