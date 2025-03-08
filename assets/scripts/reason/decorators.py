import os
import traceback
import functools
import argparse
from typing import Callable

from constants import (
    MAX_WORKERS, CHECKPOINT_INTERVAL, BATCH_SIZE
)

def error_handler(log_fn: Callable = print):
    """
    A decorator to handle exceptions in async functions.
    
    Args:
        log_fn: A function to use for logging errors
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                log_fn(f"Fatal error: {str(e)}\n{tb}")
                raise e
        return wrapper
    return decorator

def sync_error_handler(log_fn: Callable = print, exit_on_error: bool = True):
    """
    A decorator to handle exceptions in synchronous functions.
    
    Args:
        log_fn: A function to use for logging errors
        exit_on_error: Whether to exit the program on error
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_fn(f"Fatal error: {e}")
                if exit_on_error:
                    exit(1)
                raise e
        return wrapper
    return decorator

def parse_args():
    """
    A decorator to automatically parse command line arguments and pass them to the decorated function.
    
    Returns:
        Decorator function
    
    Example:
        @parse_args()
        def run_main(args):
            print(f"Running with {args.config}")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # If args are already provided, just call the function
            if args and isinstance(args[0], argparse.Namespace):
                return func(*args, **kwargs)
                
            # Create argument parser
            parser = argparse.ArgumentParser()
            
            # Add standard arguments
            parser.add_argument("--config", required=True, help="URL to the configuration file")
            parser.add_argument("--test", action="store_true", help="Only test endpoints and exit")
            parser.add_argument("--resume", action="store_true", help="Resume from previous run")
            parser.add_argument("--src", help="Source dataset to load (overrides config)")
            parser.add_argument("--dst", help="Destination dataset to push to (overrides config)")
            parser.add_argument("--log-dir", default=os.path.join(os.getcwd(), "logs"), help="Directory to save log files")
            parser.add_argument("--output", default=os.getcwd(), help="Output directory")
            parser.add_argument("--workers", type=int, help=f"Number of parallel workers (default: {MAX_WORKERS})")
            parser.add_argument("--offset", type=int, default=0, help="Offset to start processing records from")
            parser.add_argument("--max-records", type=int, default=0, help="Maximum records to process per split")
            parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Number of records to process in a batch (default: {BATCH_SIZE})")
            parser.add_argument("--checkpoint-interval", type=int, default=CHECKPOINT_INTERVAL, help=f"Interval to save intermediate checkpoints (default: {CHECKPOINT_INTERVAL})")
                
            # Parse arguments
            parsed_args = parser.parse_args()
            
            # Pass the parsed arguments to the decorated function
            return func(parsed_args, *args, **kwargs)
        return wrapper
    return decorator

def log_config(log_fn: Callable = print):
    """
    A decorator that logs configuration details and sets up required directories.
    
    Args:
        log_fn: The function to use for logging
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(args, *other_args, **kwargs):
            config = kwargs.get('config', None)
            directories = kwargs.get('directories', None)
            test_mode = kwargs.get('test_mode', False)
            
            # Ensure we have the config and directories
            if not config or not directories:
                # Get these from the main function's globals
                import inspect
                frame = inspect.currentframe().f_back
                if 'config' in frame.f_globals:
                    config = frame.f_globals['config']
                if 'directories' in frame.f_globals:
                    directories = frame.f_globals['directories']
                if 'test_mode' in frame.f_globals:
                    test_mode = frame.f_globals['test_mode']
            
            if config and directories:
                # Log column mappings
                log_fn(f"Column mappings:")
                for col_name, mapped_name in config['columns'].items():
                    log_fn(f"- {col_name}: {mapped_name}")
                
                # Create temp directories for languages if needed
                if not test_mode and "splits" in config and "t" in directories:
                    for split, lang_code in config.get("splits", {}).items():
                        lang_dir = os.path.join(directories["t"], lang_code)
                        os.makedirs(lang_dir, exist_ok=True)
                        log_fn(f"Created temp directory for language: {lang_code}")
                
                log_fn(f"Config loaded with {len(config.get('endpoints',[]))} endpoints")
            
            return await func(args, *other_args, **kwargs)
        return wrapper
    return decorator

def setup_processing(log_fn: Callable = print):
    """
    A decorator that configures processing parameters based on arguments and config.
    
    Args:
        log_fn: The function to use for logging
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(args, *other_args, **kwargs):
            config = kwargs.get('config', None)
            
            # Ensure we have the config
            if not config:
                # Access directly from the global scope of the main function
                import inspect
                frame = inspect.currentframe().f_back
                # Try using the global config directly
                if frame and 'config' in frame.f_globals:
                    config = frame.f_globals['config']
            
            if not config:
                log_fn("ERROR: Could not access configuration. This is likely a bug.")
                return await func(args, *other_args, **kwargs)
            
            # Handle dataset source
            source = args.src or config.get('src', '')
            if args.src:
                log_fn(f"Overriding source from '{config.get('src','')}' to '{args.src}'")
                config['src'] = args.src
            
            # Explicitly log the source from config if it exists but is being reported as missing
            if 'src' in config and config['src'] and not source:
                log_fn(f"WARNING: Source dataset '{config['src']}' exists in config but not being recognized")
                source = config['src']  # Force it to use the config value
            
            if not source:
                log_fn("ERROR: No source dataset specified in config or arguments (--src)")
            else:
                log_fn(f"Using source dataset: {source}")
            
            # Handle destination
            destination = args.dst or config.get('dst', '')
            if args.dst:
                log_fn(f"Overriding destination from '{config.get('dst','')}' to '{args.dst}'")
                config['dst'] = args.dst
            
            # Explicitly log the destination from config if it exists but is being reported as missing
            if 'dst' in config and config['dst'] and not destination:
                log_fn(f"WARNING: Destination dataset '{config['dst']}' exists in config but not being recognized")
                destination = config['dst']  # Force it to use the config value
                
            if not destination:
                log_fn("ERROR: No destination dataset specified in config or arguments (--dst)")
            else:
                log_fn(f"Using destination dataset: {destination}")
            
            # Get splits from config
            splits = list(config["splits"].keys()) if hasattr(config["splits"], "keys") else []
            if not splits:
                log_fn("ERROR: No splits found in config")
            else:
                log_fn(f"Found {len(splits)} splits in config: {', '.join(splits)}")
            
            # Adjust batch size and checkpoint interval based on max_records
            batch_size = args.batch_size if args.batch_size is not None else BATCH_SIZE
            checkpoint_interval = args.checkpoint_interval if args.checkpoint_interval is not None else CHECKPOINT_INTERVAL
            
            # If max_records is specified and less than batch_size, adjust batch_size
            if args.max_records > 0:
                if args.max_records < batch_size:
                    batch_size = args.max_records
                    log_fn(f"Adjusted batch size to {batch_size} to match max_records")
                    
                # If max_records is less than checkpoint_interval, adjust checkpoint_interval
                if args.max_records < checkpoint_interval:
                    checkpoint_interval = args.max_records
                    log_fn(f"Adjusted checkpoint interval to {checkpoint_interval} to match max_records")
            
            log_fn(f"Using batch size of {batch_size} for processing records")
            log_fn(f"Using checkpoint interval of {checkpoint_interval} records")
            
            # Add to kwargs
            kwargs['source'] = source
            kwargs['destination'] = destination
            kwargs['splits'] = splits
            kwargs['batch_size'] = batch_size
            kwargs['checkpoint_interval'] = checkpoint_interval
            
            return await func(args, *other_args, **kwargs)
        return wrapper
    return decorator
