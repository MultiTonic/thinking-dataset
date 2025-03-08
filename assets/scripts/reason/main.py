import argparse as ap
import asyncio
import os
import traceback

from datasets import DatasetDict

from endpoints import initialize_endpoints, test_all_endpoints
from logger import log_message, setup_loggers
from processor import proc_1sp
from push_hub import push_dataset_to_hub
from telemetry_stats import TelemetryStats
from utils import fetch_config, setup_dirs
from validate_config import validate_config

# Constants with descriptive names
MAX_WORKERS = 16
TEST_TIMEOUT = 30
CHECKPOINT_INTERVAL = 100
BATCH_SIZE = 100
MAX_RETRIES = 10
REQUEST_TIMEOUT = 600
ENDPOINT_COOLDOWN = 12

def log(message, console_output=True):
    """Shorthand function for logging messages"""
    log_message(message, console_output, file_logger, test_mode, console_logger)

async def main(args):
    try:
        global directories, config, endpoints, test_mode, arguments, telemetry_stats
        arguments = args
        test_mode = arguments.test
        telemetry_stats = TelemetryStats()
        directories = await setup_dirs(arguments) if not test_mode else {}
        
        if not test_mode:
            log(f"Run ID: {directories['r']}")
            log(f"Data dir: {directories['d']}")
            log(f"Config URL: {arguments.config}")
            
        config = await fetch_config(arguments.config, logger=log)
        if not config:
            log("Failed to load config")
            return
        
        # Use the validate_config module
        is_valid, validation_message = await validate_config(config)
        if not is_valid:
            log(f"Invalid configuration: {validation_message}")
            return
        log("Config successfully loaded")
        
        # Log column mappings, including optional source_data if present
        log(f"Column mappings:")
        for col_name, mapped_name in config['columns'].items():
            log(f"- {col_name}: {mapped_name}")
            
        if not test_mode and "splits" in config and "t" in directories:
            for split, lang_code in config.get("splits", {}).items():
                lang_dir = os.path.join(directories["t"], lang_code)
                os.makedirs(lang_dir, exist_ok=True)
                log(f"Created temp directory for language: {lang_code}")
                
        log(f"Config loaded with {len(config.get('endpoints',[]))} endpoints")
        
        worker_count = arguments.workers if arguments.workers is not None else MAX_WORKERS
        max_workers = min(worker_count, len(config['endpoints']))
        
        if arguments.workers is not None and max_workers < arguments.workers:
            log(f"Capping workers from {arguments.workers} to {max_workers} based on available endpoints")
        
        # Test all endpoints
        ready_endpoints, working_indices = await test_all_endpoints(
            config["endpoints"], 
            max_workers, 
            TEST_TIMEOUT,
            logger=log, 
            console_logger=console_logger, 
            file_logger=file_logger, 
            test_mode=test_mode
        )
        
        if ready_endpoints == 0:
            log("No working endpoints found.")
            return
            
        log(f"Found {ready_endpoints} working endpoints out of {len(config['endpoints'])} total")
        working_endpoints = [config["endpoints"][i] for i in working_indices]
        log(f"Using {len(working_endpoints)} working endpoints for processing")
        
        endpoints = initialize_endpoints(working_endpoints)
        
        if test_mode:
            log("Test completed successfully.")
            return
            
        # Handle dataset source
        if arguments.src:
            log(f"Overriding source from '{config.get('src','')}' to '{arguments.src}'")
            config['src'] = arguments.src
            
        source = config.get('src')
        if not source:
            log("No source dataset specified in config or arguments")
            return
            
        # Handle destination
        destination = arguments.dst or config.get('dst')
        if not destination:
            log("No destination dataset specified in config or arguments")
            return
            
        # Get splits from config
        splits = list(config["splits"].keys()) if hasattr(config["splits"], "keys") else []
        if not splits:
            log("No splits found in config")
            return
            
        log(f"Found {len(splits)} splits in config: {', '.join(splits)}")
        
        batch_size = arguments.batch_size if arguments.batch_size is not None else BATCH_SIZE
        checkpoint_interval = arguments.checkpoint_interval if arguments.checkpoint_interval is not None else CHECKPOINT_INTERVAL
        
        log(f"Using batch size of {batch_size} for processing records")
        log(f"Using checkpoint interval of {checkpoint_interval} records")
        
        # Process each split using the proc_1sp function from processor module
        all_datasets = {}
        total_records = 0
        
        for split_name in splits:
            split_code = config["splits"][split_name]
            dataset_dict, count = await proc_1sp(
                split_name, split_code, source, arguments.offset, arguments.max_records, 
                directories, config, endpoints, telemetry_stats, arguments, 
                BATCH_SIZE, CHECKPOINT_INTERVAL, MAX_WORKERS, MAX_RETRIES, 
                REQUEST_TIMEOUT, ENDPOINT_COOLDOWN, log, file_logger, test_mode
            )
            
            if dataset_dict:
                all_datasets.update(dataset_dict)
                total_records += count
            
        # Prepare and upload the final dataset
        if all_datasets:
            log(f"TELEMETRY: Final dataset preparation started")
            dataset_dict = DatasetDict(all_datasets)
            
            log(f"Created dataset dictionary with {total_records} total records across {len(all_datasets)} splits")
            
            for split_name, split_data in dataset_dict.items():
                log(f"- Split '{split_name}': {len(split_data)} records, columns: {', '.join(split_data.column_names)}")
                
            log(f"Average records per split: {total_records/len(all_datasets):.1f}")
            
            # Save locally
            dataset_dict.save_to_disk(directories["cs"])
            log(f"Saved unified dataset to {directories['cs']}")
            
            # Push to HuggingFace Hub
            if destination:
                log(f"Pushing dataset to Hugging Face Hub: {destination}")
                success = await push_dataset_to_hub(dataset_dict, destination, config=config, log_fn=log)
                if not success:
                    log(f"Failed to push dataset to Hugging Face Hub")
                    
        log(f"Finished processing all splits")
        
    except Exception as e:
        tb = traceback.format_exc()
        log(f"Fatal error: {str(e)}\n{tb}")
        raise e
        
if __name__=="__main__": 
    if os.name=='nt':os.environ['PYTHONIOENCODING']='utf-8'
    
    # Parse command line arguments
    parser = ap.ArgumentParser()
    parser.add_argument("--config", required=True, help="URL to the configuration file")
    parser.add_argument("--test", action="store_true", help="Only test endpoints and exit")
    parser.add_argument("--src", help="Source dataset to load (overrides config)")
    parser.add_argument("--dst", help="Destination dataset to push to (overrides config)")
    parser.add_argument("--log-dir", default=os.path.join(os.getcwd(),"logs"), help="Directory to save log files")
    parser.add_argument("--output", default=os.getcwd(), help="Output directory")
    parser.add_argument("--workers", type=int, help="Number of parallel workers for endpoint testing")
    parser.add_argument("--offset", type=int, default=0, help="Offset to start processing records from")
    parser.add_argument("--max-records", type=int, default=0, help="Maximum number of records to process per split")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, 
                       help=f"Number of records to process in a batch (default: {BATCH_SIZE})")
    parser.add_argument("--checkpoint-interval", type=int, default=CHECKPOINT_INTERVAL, 
                       help=f"Interval to save intermediate checkpoints (default: {CHECKPOINT_INTERVAL})")
    
    args = parser.parse_args()
    global test_mode, console_logger, file_logger
    test_mode = args.test
    
    try:
        # Set up loggers
        console_logger, file_logger = setup_loggers(args.log_dir, test_mode)
        asyncio.run(main(args))
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)