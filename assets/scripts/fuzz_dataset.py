import argparse
import asyncio
import logging
import os
import sys
import time
import multiprocessing
import math
from concurrent.futures import ProcessPoolExecutor
from datasets import Dataset, DatasetDict, load_dataset
from rapidfuzz import fuzz
import pandas as pd
from tqdm.asyncio import tqdm as async_tqdm
from tqdm import tqdm
MAX_WORKERS = max(4, multiprocessing.cpu_count() - 1)
LOG_DIR = "logs"
BATCH_SIZE = 2500  # Changed from 1000 to 2500
THREADS_PER_PROCESS = 2
PROGRESS_BARS_ACTIVE = False  # Flag to track if progress bars are active
def log(msg, console=True):
    try:
        file_logger.info(msg)
        if console:
            if PROGRESS_BARS_ACTIVE:
                # Use tqdm.write to print messages without disrupting progress bars
                tqdm.write(f"[{time.strftime('%X')}] {msg}")
            else:
                try: console_logger.info(msg)
                except UnicodeEncodeError: console_logger.info(msg.encode('ascii', errors='replace').decode('ascii'))
    except Exception as e: print(f"[LOGGING ERROR] Failed to log message: {str(e)}")
def setup_loggers(path):
    os.makedirs(path, exist_ok=True)
    cl, fl = logging.getLogger("console"), logging.getLogger("file")
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    cl.addHandler(ch)
    cl.setLevel(logging.INFO)
    cl.propagate = False
    f = os.path.join(path, f"fuzz_{int(time.time())}.log")
    fh = logging.FileHandler(f, encoding='utf-8')
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    fl.addHandler(fh)
    fl.setLevel(logging.INFO)
    fl.propagate = False
    return cl, fl
def setup_dirs(ld, od=None):
    rid = str(int(time.time()))
    ld = os.path.abspath(ld)
    dd = os.path.join(od or os.getcwd(), "data")
    rd = os.path.join(dd, rid)
    fd = os.path.join(rd, "fuzzed")
    dp = os.path.join(rd, "deduped")
    for d in [ld, dd, rd, fd, dp]: os.makedirs(d, exist_ok=True)
    return {"run_id": rid, "log_dir": ld, "data_dir": dd, "run_dir": rd, "fuzzed_dir": fd, "deduped_dir": dp}
class TStats:
    def __init__(self):
        self.st = time.time()
        self.tr = 0
        self.rr = 0
        self.ps = 0
        self.lt = time.time()
    def log_split(self, sn, oc, nc):
        self.tr += oc
        self.rr += (oc - nc)
        self.ps += 1
    def get_str(self):
        e = time.time() - self.st
        r = (self.rr / self.tr * 100) if self.tr > 0 else 0
        s = self.tr / e if e > 0 else 0
        return f"TELEMETRY: Processed {self.tr:,} records in {e:.1f}s • Removed {self.rr:,} similar records ({r:.1f}%) • Speed: {s:.1f} records/s • Splits: {self.ps}"
async def load_splits(src):
    try:
        log(f"Loading dataset from {src}")
        ds = load_dataset(src)
        if isinstance(ds, Dataset):
            rc = len(ds)
            log(f"Loaded dataset with 1 default split containing {rc} records")
            return {"default": ds}, {"default": rc}
        sc = {s: len(ds[s]) for s in ds}
        tr = sum(sc.values())
        log(f"Loaded dataset with {len(sc)} splits containing {tr:,} total records:")
        for s, c in sc.items(): log(f"- {s}: {c:,} records")
        return ds, sc
    except Exception as e:
        log(f"Error loading dataset '{src}': {e}", False)
        raise
def sort_by_column_length(ds, col):
    recs = ds.to_list()
    if not recs: return ds
    log(f"Sorting dataset by length of '{col}' column (ascending)")
    df = pd.DataFrame(recs)
    if col not in df.columns:
        log(f"Warning: Cannot sort - column '{col}' not found")
        return ds
    
    # Convert column to string and handle non-string values safely
    df['_length'] = df[col].astype(str).str.len()
    
    # Check for any potential issues
    if df['_length'].isnull().any():
        log(f"Warning: Some records have null values in column '{col}'")
        df['_length'] = df['_length'].fillna(0)
    
    # Sort by length (ascending)
    df = df.sort_values(by='_length')
    
    # Get min and max for logging
    min_len = df['_length'].min()
    max_len = df['_length'].max()
    
    # Remove the temporary column
    df = df.drop('_length', axis=1)
    
    log(f"Dataset sorted by '{col}' length: {len(df)} records from {min_len} to {max_len} characters")
    
    return Dataset.from_pandas(df)
def dedup_ds(ds, col):
    recs = ds.to_list()
    oc = len(recs)
    if oc == 0: return ds, 0
    log(f"Deduplicating {oc:,} records based on column '{col}'")
    df = pd.DataFrame(recs)
    dd = df.drop_duplicates(subset=[col])
    nc = len(dd)
    rc = oc - nc
    rp = (rc / oc * 100) if oc > 0 else 0
    log(f"Removed {rc:,} exact duplicates ({rp:.1f}%)")
    return Dataset.from_pandas(dd), rc

# Process a segment of a batch in parallel
def process_batch_segment(data):
    batch, col, thresh, start_idx, end_idx = data
    txts = [str(r[col]) for r in batch]
    n = len(batch)
    keep = set(range(n))
    removed_count = 0
    
    # Only process assigned segment (start_idx to end_idx)
    for i in range(start_idx, end_idx):
        if i not in keep:
            continue
            
        # But compare against ALL records that come after i
        for j in range(i + 1, n):
            if j not in keep:
                continue
                
            sim = fuzz.ratio(txts[i], txts[j])
            if sim >= thresh:
                # If similar, remove the second record
                keep.discard(j)
                removed_count += 1
    
    # Return just the indices to keep from this segment and how many were removed
    return list(k for k in keep if start_idx <= k < end_idx), removed_count

async def process_batch_parallel(batch, col, thresh, workers):
    total_records = len(batch)
    log(f"Processing batch of {total_records} records with {workers} workers")
    
    # Calculate segment size for each worker
    segment_size = math.ceil(total_records / workers)
    
    # Create tasks for each segment
    tasks = []
    loop = asyncio.get_running_loop()
    
    with tqdm(total=total_records, desc="Batch progress", leave=False) as pbar:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Create tasks for each segment
            for i in range(workers):
                start_idx = i * segment_size
                end_idx = min(start_idx + segment_size, total_records)
                if start_idx >= total_records:
                    break
                    
                # Schedule the work
                tasks.append(
                    loop.run_in_executor(
                        executor,
                        process_batch_segment,
                        (batch, col, thresh, start_idx, end_idx)
                    )
                )
            
            # Process results as they complete
            keep_indices = set()
            total_removed = 0
            
            for i, future in enumerate(asyncio.as_completed(tasks)):
                segment_keep, segment_removed = await future
                keep_indices.update(segment_keep)
                total_removed += segment_removed
                
                # Update progress
                segment_processed = segment_size * (i + 1)
                pbar.n = min(segment_processed, total_records)
                pbar.refresh()
    
    # Create the final result with only the records to keep
    result = [batch[i] for i in sorted(keep_indices)]
    
    # Log results
    kept_count = len(result)
    removed_count = total_records - kept_count
    if removed_count > 0:
        log(f"Batch completed: Kept {kept_count}/{total_records} records ({removed_count} similar records removed)")
    
    return result, removed_count

async def dedup_split(ds, col, thresh, workers):
    global PROGRESS_BARS_ACTIVE
    
    recs = ds.to_list()
    oc = len(recs)
    if oc == 0: return ds, 0
    
    log(f"Processing {oc:,} records for similarity detection (threshold: {thresh})")
    
    # Calculate number of batches
    bs = min(BATCH_SIZE, oc)
    bc = (oc + bs - 1) // bs
    
    log(f"Using batch size of {bs} records, processing {bc} batches sequentially")
    
    # Create progress bar for overall records
    PROGRESS_BARS_ACTIVE = True
    overall_pbar = async_tqdm(total=oc, desc="Records processed", position=0, leave=True)
    
    # Process one batch at a time (sequentially)
    results = []
    total_kept = 0
    total_removed = 0
    
    for batch_idx in range(bc):
        start_idx = batch_idx * bs
        end_idx = min(start_idx + bs, oc)
        current_batch = recs[start_idx:end_idx]
        batch_size = len(current_batch)
        
        log(f"Processing batch {batch_idx+1}/{bc} (records {start_idx+1}-{end_idx})")
        
        # Process this batch in parallel using all workers
        batch_results, batch_removed = await process_batch_parallel(current_batch, col, thresh, workers)
        
        # Update results and stats
        results.extend(batch_results)
        total_kept += len(batch_results)
        total_removed += batch_removed
        
        # Update progress
        overall_pbar.n = start_idx + batch_size
        overall_pbar.set_postfix({
            "kept": f"{total_kept}/{overall_pbar.n} ({total_kept/overall_pbar.n*100:.1f}%)",
            "removed": f"{total_removed}"
        })
        overall_pbar.refresh()
        
    await overall_pbar.close()
    PROGRESS_BARS_ACTIVE = False
    
    # Convert results back to a dataset
    nc = len(results)
    rc = oc - nc
    rp = (rc / oc * 100) if oc > 0 else 0
    
    log(f"Removed {rc:,} similar records ({rp:.1f}%)")
    
    return Dataset.from_list(results), rc
async def fuzz_ds(src, dst, col, thresh, workers):
    try:
        ts = TStats()
        ds, _ = await load_splits(src)
        if isinstance(ds, DatasetDict):
            fs = next(iter(ds.values()))
            if col not in fs.column_names:
                acs = ", ".join(fs.column_names)
                raise ValueError(f"Column '{col}' not found in dataset. Available columns: {acs}")
        else:
            if col not in ds.column_names:
                acs = ", ".join(ds.column_names)
                raise ValueError(f"Column '{col}' not found in dataset. Available columns: {acs}")
        log(f"Using column '{col}' for deduplication and similarity detection")
        dd = {}
        fd = {}
        to = 0
        ta = 0
        tf = 0
        for sn, sd in ds.items():
            log(f"Processing split '{sn}'...")
            oc = len(sd)
            to += oc
            st = time.time()
            dd_ds, dr = dedup_ds(sd, col)
            dd[sn] = dd_ds
            dc = oc - dr
            ta += dc
            e = time.time() - st
            rps = oc / e if e > 0 else 0
            log(f"Deduplication for split '{sn}' completed in {e:.2f}s ({rps:.1f} records/s):")
            log(f"- Original: {oc:,} records")
            log(f"- After deduplication: {dc:,} records")
            log(f"- Removed: {dr:,} exact duplicate records ({dr/oc*100:.1f}%)")
            log(f"Sorting split '{sn}' by '{col}' length")
            dd_ds = sort_by_column_length(dd_ds, col)
            st = time.time()
            fd_ds, sr = await dedup_split(dd_ds, col, thresh, workers)
            fc = dc - sr
            tf += fc
            e = time.time() - st
            rps = dc / e if e > 0 else 0
            log(f"Fuzzing for split '{sn}' completed in {e:.2f}s ({rps:.1f} records/s):")
            log(f"- After deduplication: {dc:,} records")
            log(f"- After fuzzing: {fc:,} records")
            log(f"- Removed: {sr:,} similar records ({sr/dc*100:.1f}%)")
            fd[sn] = fd_ds
            ts.log_split(sn, oc, fc)
            if time.time() - ts.lt > 30:
                log(ts.get_str())
                ts.lt = time.time()
        dr = DatasetDict(dd)
        fr = DatasetDict(fd)
        dr.save_to_disk(dirs["deduped_dir"])
        log(f"Deduplicated dataset saved locally to {dirs['deduped_dir']}")
        fr.save_to_disk(dirs["fuzzed_dir"])
        log(f"Fuzzed dataset saved locally to {dirs['fuzzed_dir']}")
        dp = ((to - ta) / to * 100) if to > 0 else 0
        fp = ((ta - tf) / ta * 100) if ta > 0 else 0
        tr = ((to - tf) / to * 100) if to > 0 else 0
        log("Processing complete. Summary:")
        log(f"- Original total records: {to:,}")
        log(f"- Records after deduplication: {ta:,} ({dp:.1f}% reduction)")
        log(f"- Final records after fuzzing: {tf:,} ({fp:.1f}% additional reduction)")
        log(f"- Total reduction: {to - tf:,} records ({tr:.1f}%)")
        log(ts.get_str())
        return fr
    except Exception as e:
        log(f"Error during dataset processing: {e}")
        raise
async def upload_ds(ds, dst):
    try:
        log(f"Uploading fuzzed dataset to {dst}...")
        ds.push_to_hub(dst)
        log(f"Successfully uploaded dataset to {dst}")
        return True
    except Exception as e:
        log(f"Error uploading dataset: {e}")
        return False
async def main():
    global console_logger, file_logger, dirs, BATCH_SIZE, MAX_WORKERS, THREADS_PER_PROCESS
    p = argparse.ArgumentParser(
        description="Process a dataset by removing duplicates and fuzzy matching similar records",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--src", required=True, help="Source dataset name")
    p.add_argument("--dest", required=True, help="Destination dataset name")
    p.add_argument("--column", required=True, help="Column name for matching")
    p.add_argument("--threshold", type=float, default=80, help="Similarity threshold (0-100)")
    p.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"Number of parallel processes")
    p.add_argument("--threads", type=int, default=THREADS_PER_PROCESS, help=f"Threads per process")
    p.add_argument("--log-dir", default=LOG_DIR, help=f"Log directory")
    p.add_argument("--output", default=os.getcwd(), help="Output directory for local data")
    p.add_argument("--dry", action="store_true", help="Skip uploading to HuggingFace Hub")
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Batch size for processing")
    args = p.parse_args()
    if args.batch_size: BATCH_SIZE = args.batch_size
    if args.workers: MAX_WORKERS = args.workers
    if args.threads: THREADS_PER_PROCESS = args.threads
    console_logger, file_logger = setup_loggers(args.log_dir)
    dirs = setup_dirs(args.log_dir, args.output)
    wc = MAX_WORKERS
    cpu_count = multiprocessing.cpu_count()
    log(f"Starting dataset processing with configuration:")
    log(f"- Run ID: {dirs['run_id']}")
    log(f"- Source dataset: {args.src}")
    log(f"- Destination dataset: {args.dest}")
    log(f"- Column for matching: {args.column}")
    log(f"- Similarity threshold: {args.threshold}")
    log(f"- Available CPUs: {cpu_count}")
    log(f"- Worker processes: {wc}")
    log(f"- Threads per process: {THREADS_PER_PROCESS}")
    log(f"- Batch size: {BATCH_SIZE}")
    log(f"- Output directory: {args.output}")
    try:
        st = time.time()
        fd = await fuzz_ds(args.src, args.dest, args.column, args.threshold, wc)
        if not args.dry:
            s = await upload_ds(fd, args.dest)
            if s: log(f"Dataset successfully processed and uploaded to {args.dest}")
            else: log(f"Dataset successfully processed but upload failed. Results saved locally to {dirs['fuzzed_dir']}")
        else: log(f"Dataset successfully processed. Upload skipped (dry run). Results saved locally to {dirs['fuzzed_dir']}")
        et = time.time() - st
        log(f"Total processing time: {et:.2f}s ({et/60:.2f} minutes)")
    except Exception as e:
        log(f"Error in main process: {e}")
        return 1
    return 0
if __name__ == "__main__":
    if os.name == 'nt': os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.exit(asyncio.run(main()))