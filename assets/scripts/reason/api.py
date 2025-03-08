from openai import AsyncOpenAI
from ollama import AsyncClient
from constants import REQUEST_TIMEOUT

async def call_openai(endpoint_config, messages, config):
    """
    Call the OpenAI API with the given endpoint configuration and messages.
    
    Args:
        endpoint_config: Dictionary containing endpoint configuration
        messages: List of message dictionaries to send to the API
        config: Main configuration dictionary with temperature and max_tokens
        
    Returns:
        str: The generated text response
        
    Raises:
        Exception: If API call fails or returns no content
    """
    try:
        async with AsyncOpenAI(
            base_url=endpoint_config['u'], 
            api_key=endpoint_config.get('k', ''),
            timeout=config.get('request_timeout', REQUEST_TIMEOUT)  # Use constant from constants.py
        ) as client:
            response = await client.chat.completions.create(
                model=endpoint_config['m'],
                messages=messages,
                max_tokens=config['max_tokens'],
                temperature=config['temperature'],
                stream=False,
                timeout=config.get('request_timeout', REQUEST_TIMEOUT)  # Use constant from constants.py
            )
            if response and response.choices and response.choices[0].message:
                return response.choices[0].message.content
            else:
                raise Exception("No response content returned from API")
    except Exception as e:
        raise

async def call_ollama(endpoint_config, messages, config):
    """
    Call the Ollama API with the given endpoint configuration and messages.
    
    Args:
        endpoint_config: Dictionary containing endpoint configuration
        messages: List of message dictionaries to send to the API
        config: Main configuration dictionary with temperature and max_tokens
        
    Returns:
        str: The generated text response
        
    Raises:
        Exception: If API call fails or returns no content
    """
    try:
        client = AsyncClient(host=endpoint_config['u'])
        max_tokens = config['max_tokens']
        response = await client.chat(
            model=endpoint_config['m'],
            messages=messages,
            options={
                "temperature": config['temperature'],
                "num_ctx": max_tokens,
                "num_predict": max_tokens,
                "timeout": config.get('request_timeout', REQUEST_TIMEOUT)  # Use constant from constants.py
            },
            stream=False
        )
        if response and response.message:
            return response.message.content
        else:
            raise Exception("No response content returned from Ollama API")
    except Exception as e:
        raise
