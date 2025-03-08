import os
import asyncio
import traceback

from endpoints import setup_endpoints
from logger import log_message, setup_loggers
from processor import process_splits
from hub import prepare_final_dataset
from utils import setup_env, load_config
from decorators import error_handler, sync_error_handler, parse_args
from constants import (
    MAX_WORKERS, TEST_TIMEOUT, BATCH_SIZE, CHECKPOINT_INTERVAL
)

def log(message, console_output=True):
    """Shorthand function for logging messages"""
    log_message(message, console_output, file_logger, test_mode, console_logger)

def log_configuration_details(config, directories, test_mode):
    """Log details about the loaded configuration"""
    # Log column mappings
    log(f"Column mappings:")
    for col_name, mapped_name in config['columns'].items():
        log(f"- {col_name}: {mapped_name}")
        
    # Create temp directories for languages if needed
    if not test_mode and "splits" in config and "t" in directories:
        for split, lang_code in config.get("splits", {}).items():
            lang_dir = os.path.join(directories["t"], lang_code)
            os.makedirs(lang_dir, exist_ok=True)
            log(f"Created temp directory for language: {lang_code}")
            
    log(f"Config loaded with {len(config.get('endpoints',[]))} endpoints")

@error_handler(log_fn=log)
async def main(args, **kwargs):
    try:
        global directories, config, endpoints, test_mode, arguments, telemetry_stats
        arguments = args
        test_mode = arguments.test
        
        # Initialize environment - now using function from utils.py
        telemetry_stats, directories = await setup_env(arguments, log)
        
        # Log resume status if applicable
        if arguments.resume and "resume_state" in directories:
            log(f"Resuming from previous run: {directories['r']}")
            resume_state = directories["resume_state"]
            log(f"- Last processed split: {resume_state.get('split_name', 'unknown')}")
            log(f"- Records processed: {resume_state.get('total_processed', 0)}")
            log(f"- Last batch: {resume_state.get('batch_index', 'unknown')}")
            log(f"- Source dataset: {resume_state.get('source', 'unknown')}")
            log(f"- Destination dataset: {resume_state.get('destination', 'unknown')}")
        elif arguments.resume:
            log("Resume flag specified but no previous state found. Starting as a new run.")
        
        # Load configuration - now using function from utils.py
        config = await load_config(arguments.config, log)
        if not config:
            return
        
        # Apply decorators explicitly now that we have the config
        log_configuration_details(config, directories, test_mode)  # Not async, no await needed
        
        # Explicitly log source and destination for debugging
        log(f"Config contains source: {'src' in config}")
        if 'src' in config:
            log(f"Source dataset in config: {config['src']}")
        
        log(f"Config contains destination: {'dst' in config}")
        if 'dst' in config:
            log(f"Destination dataset in config: {config['dst']}")
        
        # Set up endpoints - now using function from endpoints.py
        endpoints = await setup_endpoints(
            config, 
            MAX_WORKERS, 
            arguments, 
            TEST_TIMEOUT, 
            logger=log, 
            console_logger=console_logger, 
            file_logger=file_logger, 
            test_mode=test_mode
        )
        
        if not endpoints:
            return
            
        if test_mode:
            log("Test completed successfully.")
            return
        
        # Get processing parameters directly from config
        source = args.src or config.get('src', '')
        destination = args.dst or config.get('dst', '')
        splits = list(config["splits"].keys()) if hasattr(config["splits"], "keys") else []
        batch_size = args.batch_size if args.batch_size is not None else BATCH_SIZE
        checkpoint_interval = args.checkpoint_interval if args.checkpoint_interval is not None else CHECKPOINT_INTERVAL
        
        # Add explicit logging for missing parameters
        if not source:
            log("ERROR: Source dataset not specified. Use --src or add 'src' to config.")
            return
        if not destination:
            log("ERROR: Destination dataset not specified. Use --dst or add 'dst' to config.")
            return
        if not splits:
            log("ERROR: No splits found in configuration.")
            return
        
        log(f"Processing source dataset: {source}")
        log(f"Destination dataset: {destination}")
        log(f"Processing {len(splits)} splits: {', '.join(splits)}")
        
        # Check if we need to handle resumption from a completed processing
        from resume import check_and_handle_resumption
        resumption_handled = await check_and_handle_resumption(
            arguments, directories, source, destination, log, config=config
        )
        
        if resumption_handled:
            log(f"Resumption processing completed")
            return
        
        # Normal processing flow - only execute if resumption wasn't handled
        log("Starting to process splits...")
        all_datasets, total_records = await process_splits(
            splits, source, config, arguments, directories, endpoints, telemetry_stats, 
            batch_size, checkpoint_interval, log, file_logger, test_mode
        )
        
        if not all_datasets:
            log("No datasets were successfully processed.")
            return
        
        # Prepare and upload the final dataset
        log("Preparing final dataset...")
        success = await prepare_final_dataset(all_datasets, total_records, directories, destination, config=config, log_fn=log)
        
        if success:
            # Mark as successfully pushed
            from processor import save_processing_state
            await save_processing_state(
                -1, total_records, "all_complete", directories, 
                source=source, destination=destination, 
                log_fn=log, processing_complete=True, pushed_to_hub=True
            )
            log("Dataset successfully prepared and uploaded.")
        
        log(f"Finished processing all splits")
        
    except Exception as e:
        tb = traceback.format_exc()
        log(f"Fatal error: {str(e)}\n{tb}")
        raise e

@parse_args()
@sync_error_handler(log_fn=print, exit_on_error=True)
def run_main(args):
    """Run the main function with proper error handling and automatic argument parsing"""
    global test_mode, console_logger, file_logger
    
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    test_mode = args.test
    
    # Set up loggers
    console_logger, file_logger = setup_loggers(args.log_dir, test_mode)
    asyncio.run(main(args))

if __name__=="__main__": 
    run_main()