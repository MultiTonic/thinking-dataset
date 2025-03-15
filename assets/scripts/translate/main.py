import argparse
import asyncio
import json
import time
import os
from typing import Dict, List

import pandas as pd
import nltk
from datasets import load_dataset
from tqdm.asyncio import tqdm
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from config import Config
from runpod import (
    RunPodEndpoint, launch_runpods, terminate_runpods, 
    find_and_terminate_all_runpods, test_runpod_endpoints,
    startup_runpods, check_runpods_status, shutdown_runpods
)

nltk.download('punkt')

def load_state(state_file: str) -> Dict:
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return {"completed": {}, "pending": {}, "last_batch": {}}

def save_state(state: Dict, state_file: str):
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

def save_checkpoint(df: pd.DataFrame, split_name: str, tgt_lang: str, batch_start: int, batch_end: int, state: Dict, run_dirs: Dict):
    output_split_dir = os.path.join(run_dirs["output_dir"], f"data/{split_name}-translated")
    os.makedirs(output_split_dir, exist_ok=True)
    temp_path = os.path.join(output_split_dir, f"{tgt_lang}_batch_{batch_start}-{batch_end}.parquet")
    df.iloc[batch_start:batch_end].to_parquet(temp_path)
    state["pending"][f"{split_name}_{tgt_lang}"] = {
        "last_batch_start": batch_start,
        "last_batch_end": batch_end,
        "temp_file": temp_path
    }
    save_state(state, run_dirs["state_file"])
    print(f"Offloaded batch {batch_start}-{batch_end} to {temp_path}")

def create_retry_decorator(max_retries):
    return retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_random_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )

async def handle_translation_batch(endpoint: RunPodEndpoint, batch_texts: List[str], src_lang: str, tgt_lang: str, max_retries: int = 3) -> List[str]:
    retry_decorator = create_retry_decorator(max_retries)
    
    @retry_decorator
    async def _translate_batch():
        try:
            return await asyncio.gather(*[
                endpoint.translate_text(text, src_lang, tgt_lang) for text in batch_texts
            ])
        except Exception as e:
            print(f"Batch translation error: {type(e).__name__}: {str(e)}")
            raise
    
    return await _translate_batch()

async def process_split_to_language(split_name: str, src_lang: str, tgt_lang: str, endpoints: List[RunPodEndpoint], state: Dict, config: Config, run_dirs: Dict):
    # Skip if the source and target languages are the same
    if src_lang.lower() == tgt_lang.lower():
        print(f"Skipping translation from {src_lang} to {tgt_lang} (same language)")
        return
        
    print(f"Starting translation from {src_lang} to {tgt_lang} for {split_name} split")
    
    dataset = load_dataset(config.dataset_name, token=config.hf_token)
    data = dataset[split_name]
    
    # Create output dataframe using columns directly from the dataset
    df = pd.DataFrame({
        "id": list(range(len(data))),
        "think": data["think"],
        "response": data["response"],
        "query": data["query"],
        "category": data["category"],
        "endpoint": data["endpoint"],
        "source": data["source"]
    })
    
    # Create columns for translated content
    df["think_translated"] = ["" for _ in range(len(df))]
    df["response_translated"] = ["" for _ in range(len(df))]
    df["query_translated"] = ["" for _ in range(len(df))]
    
    # Setup output directory - organize by source and target language
    output_split_name = f"{split_name}_from_{src_lang.lower()}_to_{tgt_lang.lower()}"
    output_split_dir = os.path.join(run_dirs["output_dir"], f"data/{output_split_name}")
    os.makedirs(output_split_dir, exist_ok=True)
    
    # Check if we've already completed this translation
    if f"{split_name}_{src_lang}_{tgt_lang}" in state["completed"]:
        print(f"Translation from {src_lang} to {tgt_lang} for {split_name} already completed, skipping...")
        return
        
    print(f"Translating {split_name} split from {src_lang} to {tgt_lang}...")
    last_batch_start = state.get("pending", {}).get(f"{split_name}_{src_lang}_{tgt_lang}", {}).get("last_batch_start", 0)
    
    endpoint_idx = 0
    
    # Track successful and failed translations
    success_records = []
    failed_records = []
    
    # Process in batches
    for i in tqdm(range(last_batch_start, len(df), config.batch_size), desc=f"{split_name}: {src_lang} -> {tgt_lang}"):
        batch_end = min(i + config.batch_size, len(df))
        batch_think = df["think"][i:batch_end].tolist()
        batch_response = df["response"][i:batch_end].tolist()
        batch_query = df["query"][i:batch_end].tolist()
        
        endpoint = endpoints[endpoint_idx % len(endpoints)]
        endpoint_idx += 1
        
        # Translate thinking, response, and query with retry logic using config max_retries
        for j in range(batch_end - i):
            idx = i + j
            row = df.iloc[idx].copy()
            row_failed = False
            
            try:
                row["think_translated"] = await endpoint.translate_text(
                    batch_think[j], src_lang, tgt_lang)
            except Exception as e:
                error_msg = f"Think error: {str(e)}"
                print(f"Failed to translate thinking for row {idx}: {str(e)}")
                row["think_translated"] = error_msg
                row_failed = True
            
            try:
                row["response_translated"] = await endpoint.translate_text(
                    batch_response[j], src_lang, tgt_lang)
            except Exception as e:
                error_msg = f"Response error: {str(e)}"
                print(f"Failed to translate response for row {idx}: {str(e)}")
                row["response_translated"] = error_msg
                row_failed = True
            
            try:
                row["query_translated"] = await endpoint.translate_text(
                    batch_query[j], src_lang, tgt_lang)
            except Exception as e:
                error_msg = f"Query error: {str(e)}"
                print(f"Failed to translate query for row {idx}: {str(e)}")
                row["query_translated"] = error_msg
                row_failed = True
            
            # Add to appropriate list
            if row_failed:
                failed_records.append(row)
            else:
                success_records.append(row)
        
        # Updated to use checkpoint_interval instead of offload_interval
        if (i // config.batch_size) % config.checkpoint_interval == 0 and i > 0:
            # Convert to DataFrame and save checkpoint
            combined_df = pd.concat([pd.DataFrame(success_records), pd.DataFrame(failed_records)])
            save_checkpoint(combined_df, output_split_name, tgt_lang, 0, batch_end, state, run_dirs)
    
    # Create dataframes from records
    success_df = pd.DataFrame(success_records) if success_records else pd.DataFrame(columns=df.columns)
    failed_df = pd.DataFrame(failed_records) if failed_records else pd.DataFrame(columns=df.columns)
    
    print(f"Translation complete: {len(success_df)} succeeded, {len(failed_df)} failed")
    
    # Create descriptive names for dataset splits
    src_lang_lower = src_lang.lower()
    tgt_lang_lower = tgt_lang.lower()
    translation_direction = f"{src_lang_lower}_to_{tgt_lang_lower}"
    
    # Save the successful translations with descriptive name
    if len(success_df) > 0:
        output_filename = f"{translation_direction}.parquet"
        output_path = os.path.join(output_split_dir, output_filename)
        success_df.to_parquet(output_path)
        print(f"Saved {len(success_df)} successful translations to {output_path}")
    
    # Save the failed translations if any exist with descriptive name
    if len(failed_df) > 0:
        failed_filename = f"{translation_direction}_failed.parquet"
        failed_path = os.path.join(output_split_dir, failed_filename)
        failed_df.to_parquet(failed_path)
        print(f"Saved {len(failed_df)} failed translations to {failed_path}")
    
    # Create additional metadata file with translation details
    metadata = {
        "source_language": src_lang,
        "target_language": tgt_lang,
        "source_split": split_name,
        "records_processed": len(df),
        "records_succeeded": len(success_df),
        "records_failed": len(failed_df),
        "success_rate": len(success_df) / len(df) if len(df) > 0 else 0,
        "timestamp": time.time(),
        "translation_direction": translation_direction
    }
    
    metadata_path = os.path.join(output_split_dir, "translation_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Update state
    state["completed"][f"{split_name}_{src_lang}_{tgt_lang}"] = True
    if f"{split_name}_{src_lang}_{tgt_lang}" in state["pending"]:
        del state["pending"][f"{split_name}_{src_lang}_{tgt_lang}"]
    save_state(state, run_dirs["state_file"])
    
    print(f"Saved {src_lang} to {tgt_lang} translation for {split_name} (Success rate: {metadata['success_rate']*100:.2f}%)")

async def main():
    config = Config(args.config)
    
    # Handle special operation modes
    if args.shutdown:
        if not config.runpod_api_key:
            print("Error: runpod_api_key not found in config and RUNPOD_API_KEY not set in environment")
            return
        await shutdown_runpods(config)
        return
    
    if args.startup:
        if not config.runpod_api_key:
            print("Error: runpod_api_key not found in config and RUNPOD_API_KEY not set in environment")
            return
        await startup_runpods(config)
        return
    
    if args.status:
        if not config.runpod_api_key:
            print("Error: runpod_api_key not found in config and RUNPOD_API_KEY not set in environment")
            return
        await check_runpods_status(config)
        return
    
    # Regular processing logic continues below
    run_dirs = config.setup_run_dir()
    print(f"Run ID: {run_dirs['run_id']}")
    
    config.output_dir = run_dirs["output_dir"]
    config.state_file = run_dirs["state_file"]
    
    print(f"Output directory: {config.output_dir}")
    print(f"State file: {config.state_file}")
    
    if not config.runpod_api_key:
        print("Error: runpod_api_key not found in config and RUNPOD_API_KEY not set in environment")
        return

    if not config.hf_token:
        print("Error: hf_token not found in config and HF_TOKEN not set in environment")
        return

    # Load state and launch RunPods
    state = load_state(run_dirs["state_file"])
    runpod_info = launch_runpods(config)

    try:
        if not runpod_info:
            raise ValueError("No RunPod instances were successfully launched. Cannot proceed.")
            
        endpoints = [
            RunPodEndpoint(
                pod_id,
                max_retries=config.max_retries,
                request_timeout=config.request_timeout,
                is_pod_id=True
            )
            for i, (pod_id, _) in enumerate(runpod_info) if pod_id
        ]
        
        if not endpoints:
            raise ValueError("No valid RunPod endpoints created. Cannot proceed.")
            
        print(f"Initialized {len(endpoints)} endpoints: {[e.endpoint for e in endpoints]}")

        # Use source and target languages from config
        target_languages = config.target_languages
        source_languages = config.source_languages
        
        # Create all translation tasks
        tasks = []
        for split_name in ["english", "chinese"]:
            # Determine source language based on split name, with proper capitalization
            src_lang = next((lang for lang in source_languages 
                            if lang.lower() == split_name), None)
            
            # Raise error if split name doesn't match any source language - this is a critical error
            if not src_lang:
                raise ValueError(f"Critical error: The split '{split_name}' doesn't match any configured source languages in {source_languages}. Please update your configuration.")
            
            print(f"Processing split '{split_name}' with source language '{src_lang}'")
            
            # Translate to all target languages
            for tgt_lang in target_languages:
                # Skip self-translation (case-insensitive comparison)
                if src_lang.lower() == tgt_lang.lower():
                    continue
                    
                tasks.append(process_split_to_language(
                    split_name=split_name,
                    src_lang=src_lang,
                    tgt_lang=tgt_lang,
                    endpoints=endpoints,
                    state=state,
                    config=config,
                    run_dirs=run_dirs
                ))
        
        # Log total translation task count
        print(f"Starting {len(tasks)} translation tasks across {len(source_languages)} source splits and {len(target_languages)} target languages")
        
        # Execute all translation tasks
        await asyncio.gather(*tasks)
        print(f"Translation process completed! Results saved to: {run_dirs['run_dir']}")
    finally:
        terminate_runpods(runpod_info, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate dataset across multiple languages.")
    parser.add_argument("--config", type=str, default="./config/translate_config.yaml", 
                        help="Path to configuration file (YAML)")
    parser.add_argument("--shutdown", action="store_true",
                        help="Shutdown all active RunPod instances and exit")
    parser.add_argument("--startup", action="store_true",
                        help="Start up RunPod instances without beginning translation")
    parser.add_argument("--status", action="store_true",
                        help="Check status of all RunPod instances")
    args = parser.parse_args()
    asyncio.run(main())