async def validator(config, split=None):
    """
    Validates the configuration dictionary for the reasoning processor.
    
    Args:
        config: The configuration dictionary to validate
        split: Optional split name to validate specific split config
    
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is a string
    """
    if not isinstance(config, dict):
        return False, "Not dict"
        
    if "endpoints" not in config:
        return False, "No endpoints"
        
    if not isinstance(config["endpoints"], list) or len(config["endpoints"]) == 0:
        return False, "Need ≥1 endpoint"
        
    for endpoint in config["endpoints"]:
        if "m" not in endpoint:
            return False, f"Endpoint {endpoint.get('n', 'unknown')} missing model"
            
    # Required parameters with types
    required_params = {
        "temperature": int,
        "max_tokens": int,
        "min_length": int,
    }
    
    # Check required parameters
    for param_name, param_type in required_params.items():
        if param_name not in config:
            return False, f"No {param_name}"
        if not isinstance(config[param_name], (int, float)):  # Allow both int and float for numeric parameters
            return False, f"{param_name} must be numeric"
    
    # Check for required string parameters
    if "src" not in config:
        return False, "No source dataset specified (src)"
    
    if "dst" not in config:
        return False, "No destination dataset specified (dst)"
    
    # Check that string parameters are indeed strings
    for param_name in ["src", "dst", "hf_token"]:
        if param_name in config and not isinstance(config[param_name], str):
            return False, f"{param_name} must be a string"
            
    if "private" in config and not isinstance(config["private"], bool):
        return False, "private must be a boolean"
        
    if split is None:
        return True, "Valid for test mode"
        
    # Additional validation when a specific split is provided
    for key in ["splits", "systems", "metacogs", "columns"]:
        if key not in config:
            return False, f"No {key}"
        if not isinstance(config[key], dict):
            return False, f"{key} must be dict"
            
    for col in ["query", "response", "think"]:
        if col not in config["columns"]:
            return False, f"Missing required column mapping: {col}"
            
    if split not in config["splits"]:
        return False, f"No '{split}' in splits"
    
    system_categories = ["dark_thoughts", "benign"]
    
    # Check if split exists in systems
    found_in_systems = False
    for category in system_categories:
        if category in config["systems"] and split in config["systems"][category]:
            found_in_systems = True
            break
    if not found_in_systems:
        return False, f"No '{split}' in systems categories"
    
    # Check if split exists in metacogs
    found_in_metacogs = False
    for category in system_categories:
        if category in config["metacogs"] and split in config["metacogs"][category]:
            found_in_metacogs = True
            break
    if not found_in_metacogs:
        return False, f"No '{split}' in metacogs categories"
    
    return True, "Valid"
