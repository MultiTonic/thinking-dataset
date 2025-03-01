import argparse
import json
import logging
import os
import time
import asyncio
from datetime import datetime
from functools import lru_cache
import aiohttp
from evaluate import load
from datasets import load_dataset, get_dataset_config_names

RUN_ID = f"{int(time.time())}"
DEFAULT_URL = "http://localhost:11434/api/generate"
MAX_WORKERS = 1
c_log = logging.getLogger("console")
f_log = logging.getLogger("file")

LANGUAGES = [
    "Arabic", "Bengali", "Czech", "German", "English", "Spanish", "Persian", "French",
    "Hebrew", "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean", "Lao",
    "Malay", "Burmese", "Dutch", "Polish", "Portuguese", "Russian", "Thai", "Tagalog",
    "Turkish", "Urdu", "Vietnamese", "Chinese"
]

LANG_CODES = {
    "ar": "Arabic", "bn": "Bengali", "cs": "Czech", "de": "German", 
    "en": "English", "es": "Spanish", "fa": "Persian", "fr": "French",
    "he": "Hebrew", "hi": "Hindi", "id": "Indonesian", "it": "Italian", 
    "ja": "Japanese", "km": "Khmer", "ko": "Korean", "lo": "Lao",
    "ms": "Malay", "my": "Burmese", "nl": "Dutch", "pl": "Polish", 
    "pt": "Portuguese", "ru": "Russian", "th": "Thai", "tl": "Tagalog",
    "tr": "Turkish", "ur": "Urdu", "vi": "Vietnamese", "zh": "Chinese"
}

LANG_NAMES = {v.lower(): k for k, v in LANG_CODES.items()}
DATASET_TYPES = ["smolsent", "smoldoc", "gatitos"]

def log(msg, console=True):
    try:
        if hasattr(f_log, 'handlers') and f_log.handlers:
            f_log.info(msg)
        if console:
            if hasattr(c_log, 'handlers') and c_log.handlers:
                try: c_log.info(msg)
                except UnicodeEncodeError: c_log.info(msg.encode('ascii', errors='replace').decode('ascii'))
            else:
                print(f"[{time.strftime('%X')}] {msg}")
    except Exception as e: print(f"[LOGGING ERROR] Failed to log message: {str(e)}")

def setup_loggers(log_path):
    global c_log, f_log
    os.makedirs(log_path, exist_ok=True)
    
    c_log = logging.getLogger("console")
    f_log = logging.getLogger("file")
    
    if c_log.handlers: c_log.handlers.clear()
    if f_log.handlers: f_log.handlers.clear()
    
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    c_log.addHandler(c_handler)
    c_log.setLevel(logging.INFO)
    c_log.propagate = False
    
    log_file = os.path.join(log_path, f"eval_{RUN_ID}.log")
    f_handler = logging.FileHandler(log_file, encoding='utf-8')
    f_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    f_log.addHandler(f_handler)
    f_log.setLevel(logging.INFO)
    f_log.propagate = False
    
    print(f"Loggers initialized, writing to {log_file}")
    return c_log, f_log

def setup_dirs(output_dir=None):
    base_dir = os.path.abspath(output_dir) if output_dir else os.getcwd()
    logs_dir = os.path.join(base_dir, "logs")
    results_dir = os.path.join(base_dir, "results")
    
    dirs = {
        "base": base_dir,
        "results": results_dir,
        "logs_dir": logs_dir
    }
    
    for path in dirs.values():
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")
    
    return dirs

async def query_ollama_async(prompt, model, api_url, session, semaphore):
    async with semaphore:
        start = time.time()
        log(f"Querying model '{model}' with prompt: {prompt[:50]}...")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            async with session.post(api_url, json=payload) as resp:
                resp.raise_for_status()
                result = await resp.json()
                text = result["response"].strip()
                
                elapsed = time.time() - start
                log(f"Response received in {elapsed:.2f}s ({len(text)} chars)")
                
                return text, elapsed
        except Exception as e:
            log(f"Error connecting to Ollama API: {e}")
            if "Connection refused" in str(e):
                log(f"Make sure Ollama is running and accessible at {api_url}")
            return f"ERROR: {str(e)}", time.time() - start

def report_telemetry(start, eval_times, pred_times):
    elapsed = time.time() - start
    
    log("=== Telemetry Report ===")
    log(f"- Total runtime: {elapsed:.2f}s ({elapsed/60:.2f} min)")
    
    if eval_times:
        avg_eval = sum(eval_times) / len(eval_times)
        log(f"- Average eval computation time: {avg_eval:.4f}s")
        eval_rate = len(eval_times) / elapsed * 60
        log(f"- Evaluation rate: {eval_rate:.2f} evals/minute")
    
    if pred_times:
        avg_pred = sum(pred_times) / len(pred_times)
        log(f"- Average model prediction time: {avg_pred:.2f}s")
        pred_rate = len(pred_times) / sum(pred_times) * 60
        log(f"- Model prediction rate: {pred_rate:.2f} predictions/minute")
    
    return {
        "runtime": elapsed,
        "avg_eval_time": sum(eval_times) / len(eval_times) if eval_times else 0,
        "avg_pred_time": sum(pred_times) / len(pred_times) if pred_times else 0,
        "eval_rate": len(eval_times) / elapsed * 60 if elapsed > 0 and eval_times else 0,
        "pred_rate": len(pred_times) / sum(pred_times) * 60 if pred_times and sum(pred_times) > 0 else 0,
    }

@lru_cache(maxsize=100)
def format_prompt(text, src_lang, tgt_lang):
    return f"Translate this from {src_lang} to {tgt_lang}:\n{src_lang}: {text}\n{tgt_lang}:"

@lru_cache(maxsize=32)
def get_available_language_pairs(dataset_type="smolsent"):
    try:
        configs = get_dataset_config_names("google/smol")
        dataset_configs = [config for config in configs if config.startswith(f"{dataset_type}__")]
        
        language_pairs = []
        for config in dataset_configs:
            parts = config.split("__")
            if len(parts) >= 2:
                lang_pair = parts[1]
                if "_" in lang_pair:
                    src, tgt = lang_pair.split("_")
                    language_pairs.append((src, tgt))
        
        return language_pairs
    except Exception as e:
        log(f"Error getting available language pairs: {e}")
        return []

@lru_cache(maxsize=32)
def _load_smol_dataset_cached(dataset_type, src_code, tgt_code, max_samples_str):
    max_samples = int(max_samples_str) if max_samples_str != "None" else None
    try:
        dataset_name = f"{dataset_type}__{src_code}_{tgt_code}"
        log(f"Loading dataset: google/smol, subset: {dataset_name}")
        
        dataset = load_dataset("google/smol", dataset_name, split="train")
        
        if max_samples and max_samples > 0 and max_samples < len(dataset):
            dataset = dataset.select(range(max_samples))
        
        src_texts = list(dataset["src"])
        tgt_texts = [[trg] for trg in dataset["trg"]]
        
        log(f"Loaded {len(src_texts)} translation pairs from {dataset_name}")
        return src_texts, tgt_texts
    except Exception as e:
        error_msg = str(e)
        if "BuilderConfig" in error_msg and "not found" in error_msg and "Available" in error_msg:
            # Extract available configs list
            available_configs = []
            try:
                start_idx = error_msg.find('[')
                end_idx = error_msg.rfind(']')
                if start_idx > 0 and end_idx > start_idx:
                    configs_str = error_msg[start_idx+1:end_idx]
                    available_configs = [c.strip().strip("'") for c in configs_str.split(',')]
            except:
                pass
                
            # Count configs by type
            type_counts = {"smolsent": 0, "smoldoc": 0, "gatitos": 0, "other": 0}
            for cfg in available_configs:
                if cfg.startswith("smolsent__"):
                    type_counts["smolsent"] += 1
                elif cfg.startswith("smoldoc__"):
                    type_counts["smoldoc"] += 1
                elif cfg.startswith("gatitos__"):
                    type_counts["gatitos"] += 1
                else:
                    type_counts["other"] += 1
            
            # Check specifically if similar datasets exist
            target_examples = []
            for pair_suffix in [f"__{src_code}_{tgt_code}", f"__{tgt_code}_{src_code}"]:
                for prefix in ["smolsent", "smoldoc", "gatitos"]:
                    example = f"{prefix}{pair_suffix}"
                    if example in available_configs:
                        target_examples.append(example)
            
            # Log concise error message
            log(f"Error loading SMOL dataset: BuilderConfig '{dataset_name}' not found")
            log(f"Available configs: {len(available_configs)} total ({type_counts['smolsent']} smolsent, {type_counts['smoldoc']} smoldoc, {type_counts['gatitos']} gatitos)")
            
            if target_examples:
                log(f"Similar datasets found: {', '.join(target_examples)}")
            
            # Show a few examples of each type
            for ds_type in ["smolsent", "smoldoc", "gatitos"]:
                examples = [c for c in available_configs if c.startswith(f"{ds_type}__")][:3]
                if examples:
                    log(f"Sample {ds_type} configs: {', '.join(examples)}...")
        else:
            log(f"Error loading SMOL dataset: {e}")
        return None, None

def load_smol_dataset(src_code, tgt_code, dataset_type="smolsent", max_samples=None):
    return _load_smol_dataset_cached(dataset_type, src_code, tgt_code, str(max_samples))

def load_smol_dataset_with_fallback(src_code, tgt_code, max_samples=None):
    dataset_types = ["smoldoc", "smolsent", "gatitos"]
    
    for ds_type in dataset_types:
        try:
            log(f"Attempting to load {ds_type} dataset for {src_code}-{tgt_code}")
            src_texts, tgt_texts = load_smol_dataset(src_code, tgt_code, ds_type, max_samples)
            
            if src_texts and len(src_texts) > 0:
                log(f"Successfully loaded {ds_type} dataset with {len(src_texts)} records")
                return src_texts, tgt_texts, ds_type
            else:
                log(f"No records found in {ds_type} dataset for {src_code}-{tgt_code}, trying next type")
        except Exception as e:
            log(f"Error loading {ds_type} dataset for {src_code}-{tgt_code}: {e}")
    
    log(f"Failed to load data from any dataset type for {src_code}-{tgt_code}")
    return None, None, None

@lru_cache(maxsize=100)
def parse_lang_pair(lang_pair):
    if not lang_pair or '-' not in lang_pair:
        return None, None
    
    src, tgt = lang_pair.strip().lower().split('-')
    
    if src in LANG_NAMES:
        src = LANG_NAMES[src]
    if tgt in LANG_NAMES:
        tgt = LANG_NAMES[tgt]
        
    if src not in LANG_CODES and src not in LANG_CODES.values():
        log(f"Unknown source language: {src}")
        return None, None
    if tgt not in LANG_CODES and tgt not in LANG_CODES.values():
        log(f"Unknown target language: {tgt}")
        return None, None
        
    return src, tgt

async def evaluate_language_pair(src_code, tgt_code, args, dirs, dataset_type, session, semaphore):
    src_lang = LANG_CODES.get(src_code, src_code)
    tgt_lang = LANG_CODES.get(tgt_code, tgt_code)
    log(f"Evaluating translation from {src_lang} ({src_code}) to {tgt_lang} ({tgt_code})")
    
    if dataset_type == "auto":
        source_texts, references, actual_dataset_type = load_smol_dataset_with_fallback(src_code, tgt_code, args.samples)
        if actual_dataset_type:
            log(f"Auto-selected dataset type: {actual_dataset_type}")
            dataset_type = actual_dataset_type
        else:
            log(f"Failed to load dataset for language pair: {src_code}-{tgt_code}")
            return None
    else:
        source_texts, references = load_smol_dataset(src_code, tgt_code, dataset_type, args.samples)
        if not source_texts:
            log(f"Failed to load dataset for language pair: {src_code}-{tgt_code} from {dataset_type}")
            return None
    
    formatted_prompts = [format_prompt(text, src_lang, tgt_lang) for text in source_texts]
    
    data = {
        "prompts": formatted_prompts,
        "source_texts": source_texts,
        "references": references
    }
    
    start = time.time()
    pred_times = []
    eval_times = []
    
    log(f"Loaded {dataset_type} dataset with {len(data['prompts'])} prompts")
    log(f"Starting model evaluation for {src_code}-{tgt_code} pair...")

    tasks = [
        query_ollama_async(prompt, args.model, args.url, session, semaphore)
        for prompt in data["prompts"]
    ]
    results = await asyncio.gather(*tasks)
    preds = []
    
    for i, (pred, t) in enumerate(results):
        pred_times.append(t)
        preds.append(pred)
        log(f"Source text: {data['source_texts'][i]}")
        log(f"Prompt used: {data['prompts'][i]}")
        log(f"Prediction: {pred}")
        log(f"Reference: {data['references'][i][0]}")
        log("---------------------------")
    
    eval_data = {
        "predictions": preds,
        "references": data["references"]
    }
    
    log("Computing evaluation metrics...")
    metrics_results = {}
    
    try:
        t_start = time.time()
        rouge = load("rouge")
        rouge_res = rouge.compute(
            predictions=eval_data["predictions"],
            references=eval_data["references"],
            rouge_types=["rouge1", "rouge2", "rougeL", "rougeLsum"],
            use_stemmer=True
        )
        t_compute = time.time() - t_start
        eval_times.append(t_compute)
        metrics_results["rouge"] = {k: float(v) for k, v in rouge_res.items()}
        log(f"ROUGE computed in {t_compute:.2f}s")
    except Exception as e:
        log(f"Error computing ROUGE: {e}")
    
    try:
        t_start = time.time()
        bleu = load("bleu")
        bleu_res = bleu.compute(
            predictions=eval_data["predictions"],
            references=eval_data["references"],
            max_order=4,
            smooth=True
        )
        t_compute = time.time() - t_start
        eval_times.append(t_compute)
        metrics_results["bleu"] = {
            k: ([float(p) for p in v] if k == "precisions" else float(v)) 
            for k, v in bleu_res.items()
        }
        log(f"BLEU computed in {t_compute:.2f}s")
    except Exception as e:
        log(f"Error computing BLEU: {e}")
    
    log("=== Evaluation Results ===")
    if "rouge" in metrics_results:
        log("ROUGE Scores:")
        for k, v in metrics_results["rouge"].items():
            log(f"{k}: {v:.4f}")
    
    if "bleu" in metrics_results:
        log("BLEU Scores:")
        for k, v in metrics_results["bleu"].items():
            if k == "precisions":
                log(f"{k}: {[round(p, 4) for p in v]}")
            else:
                log(f"{k}: {v:.4f}")
    
    telemetry = report_telemetry(start, eval_times, pred_times)
    
    results = {
        **metrics_results,
        "metadata": {
            "model": args.model,
            "run_id": RUN_ID,
            "dataset_type": dataset_type,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "source_language": src_lang,
            "source_code": src_code,
            "target_language": tgt_lang,
            "target_code": tgt_code,
            "source_texts": data["source_texts"],
            "prompts": data["prompts"],
            "references": data["references"],
            "predictions": preds,
            "samples": len(preds)
        },
        "telemetry": telemetry
    }
    
    out_file = os.path.join(dirs["results"], f"{dataset_type}_{src_code}_{tgt_code}_{RUN_ID}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
        log(f"Results saved to {out_file}")
    
    latest = os.path.join(dirs["results"], f"latest_{dataset_type}_{src_code}_{tgt_code}_results.json")
    try:
        if os.path.exists(latest):
            os.remove(latest)
        with open(latest, 'w') as f:
            json.dump(results, f, indent=4) 
        log(f"Latest results also available at {latest}")
    except Exception as e:
        log(f"Warning: Could not update latest results link: {e}")
    
    log(f"Evaluation for {src_lang}-{tgt_lang} using {dataset_type} completed successfully!")
    return results

async def main_async():
    p = argparse.ArgumentParser(description="Evaluate GGUF model via Ollama on SMOL dataset")
    p.add_argument("--model", default="hf.co/Tonic/GemmaX2-28-2B-gguf:BF16", help="Model to use for evaluation")
    p.add_argument("--output", default=os.getcwd(), help="Output directory for evaluation results")
    p.add_argument("--url", default=DEFAULT_URL, help="Ollama API URL")
    p.add_argument("--lang-pair", default=None, help="Language pair to evaluate (e.g., 'en-es' or 'english-spanish')")
    p.add_argument("--dataset-type", default="auto", choices=DATASET_TYPES + ["auto"], 
                   help="SMOL dataset type to use (auto, smolsent, smoldoc, or gatitos)")
    p.add_argument("--samples", type=int, default=10, help="Number of samples to evaluate")
    p.add_argument("--all", action="store_true", help="Evaluate all available language pairs")
    p.add_argument("--workers", type=int, default=MAX_WORKERS, help="Maximum number of concurrent API requests")
    args = p.parse_args()
    
    dirs = setup_dirs(args.output)
    setup_loggers(dirs["logs_dir"])
    
    log(f"Starting evaluation with run ID: {RUN_ID}")
    log(f"Model: {args.model}")
    log(f"Ollama API URL: {args.url}")
    log(f"Output directory: {dirs['base']}")
    log(f"Using max {args.workers} concurrent workers")
    
    semaphore = asyncio.Semaphore(args.workers)
    
    async with aiohttp.ClientSession() as session:
        if args.lang_pair is None and not args.all:
            args.all = True
            log("No language pair specified, defaulting to evaluating all pairs")
        
        dataset_type_for_discovery = "smolsent" if args.dataset_type == "auto" else args.dataset_type
        
        if args.all:
            log(f"Evaluating all available language pairs")
            log(f"Using dataset type: {args.dataset_type}")
            
            if args.dataset_type == "auto":
                log(f"Auto mode: Will try SmolDoc, SmolSent, then GATITOS in that order for each language pair")
                log(f"Using {dataset_type_for_discovery} for language pair discovery")
                
            language_pairs = get_available_language_pairs(dataset_type_for_discovery)
            
            if not language_pairs:
                log(f"No language pairs found for dataset type: {dataset_type_for_discovery}")
                return
            
            log(f"Found {len(language_pairs)} language pairs to evaluate")
            
            summary = {
                "model": args.model,
                "dataset_type": args.dataset_type,
                "run_id": RUN_ID,
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "language_pairs": {},
                "samples_per_pair": args.samples,
                "workers": args.workers
            }
            
            tasks = []
            for idx, (src, tgt) in enumerate(language_pairs):
                log(f"Queueing pair {idx+1}/{len(language_pairs)}: {src}-{tgt}")
                task = evaluate_language_pair(src, tgt, args, dirs, args.dataset_type, session, semaphore)
                tasks.append((src, tgt, task))
            
            for idx, (src, tgt, task) in enumerate(tasks):
                try:
                    log(f"Evaluating pair {idx+1}/{len(language_pairs)}: {src}-{tgt}")
                    results = await task
                    if results:
                        pair_key = f"{src}_{tgt}"
                        summary["language_pairs"][pair_key] = {
                            "source": src,
                            "target": tgt,
                            "source_name": LANG_CODES.get(src, src),
                            "target_name": LANG_CODES.get(tgt, tgt),
                            "bleu": results.get("bleu", {}).get("bleu", 0),
                            "rouge1": results.get("rouge", {}).get("rouge1", 0),
                            "rougeL": results.get("rouge", {}).get("rougeL", 0),
                        }
                except Exception as e:
                    log(f"Error evaluating {src}-{tgt}: {e}")
            
            summary_file = os.path.join(dirs["results"], f"summary_{args.dataset_type}_{RUN_ID}.json")
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=4)
            log(f"Summary results saved to {summary_file}")
            
        else:
            src_code, tgt_code = parse_lang_pair(args.lang_pair)
            if not src_code or not tgt_code:
                log(f"Invalid language pair: {args.lang_pair}")
                log(f"Format should be 'en-es' or 'english-spanish'.")
                return
            
            await evaluate_language_pair(src_code, tgt_code, args, dirs, args.dataset_type, session, semaphore)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()