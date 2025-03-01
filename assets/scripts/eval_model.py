import argparse
import json
import logging
import os
import time
import requests
from datetime import datetime
from evaluate import load
from datasets import load_dataset

RUN_ID = f"{int(time.time())}"
DEFAULT_URL = "http://localhost:11434/api/generate"
c_log = logging.getLogger("console")
f_log = logging.getLogger("file")

# Supported languages in SMOL dataset
LANGUAGES = [
    "Arabic", "Bengali", "Czech", "German", "English", "Spanish", "Persian", "French",
    "Hebrew", "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean", "Lao",
    "Malay", "Burmese", "Dutch", "Polish", "Portuguese", "Russian", "Thai", "Tagalog",
    "Turkish", "Urdu", "Vietnamese", "Chinese"
]

# Language code to name mapping
LANG_CODES = {
    "ar": "Arabic", "bn": "Bengali", "cs": "Czech", "de": "German", 
    "en": "English", "es": "Spanish", "fa": "Persian", "fr": "French",
    "he": "Hebrew", "hi": "Hindi", "id": "Indonesian", "it": "Italian", 
    "ja": "Japanese", "km": "Khmer", "ko": "Korean", "lo": "Lao",
    "ms": "Malay", "my": "Burmese", "nl": "Dutch", "pl": "Polish", 
    "pt": "Portuguese", "ru": "Russian", "th": "Thai", "tl": "Tagalog",
    "tr": "Turkish", "ur": "Urdu", "vi": "Vietnamese", "zh": "Chinese"
}

# Name to code mapping
LANG_NAMES = {v.lower(): k for k, v in LANG_CODES.items()}

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
    
    if c_log.handlers:
        c_log.handlers.clear()
    if f_log.handlers:
        f_log.handlers.clear()
    
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

def query_ollama(prompt, model="hf.co/Tonic/GemmaX2-28-2B-gguf:BF16", api_url=DEFAULT_URL):
    start = time.time()
    log(f"Querying model '{model}' with prompt: {prompt[:50]}...")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        resp = requests.post(api_url, json=payload)
        resp.raise_for_status()
        result = resp.json()
        text = result["response"].strip()
        
        elapsed = time.time() - start
        log(f"Response received in {elapsed:.2f}s ({len(text)} chars)")
        
        return text, elapsed
    except requests.RequestException as e:
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

def format_prompt(text, src_lang, tgt_lang):
    return f"Translate this from {src_lang} to {tgt_lang}:\n{src_lang}: {text}\n{tgt_lang}:"

def load_smol_dataset(src_code, tgt_code, max_samples=None):
    """Load translation data from Google SMOL dataset"""
    try:
        dataset_name = f"smolsent__{src_code}_{tgt_code}"
        log(f"Loading dataset: google/smol, subset: {dataset_name}")
        
        dataset = load_dataset("google/smol", dataset_name, split="train")
        
        if max_samples and max_samples > 0 and max_samples < len(dataset):
            log(f"Taking {max_samples} samples from dataset (total: {len(dataset)})")
            dataset = dataset.select(range(max_samples))
        
        src_texts = dataset["src"]  # Source texts
        tgt_texts = [[trg] for trg in dataset["trg"]]  # Target texts wrapped as list of lists for evaluation
        
        log(f"Loaded {len(src_texts)} translation pairs from {dataset_name}")
        return src_texts, tgt_texts
    except Exception as e:
        log(f"Error loading SMOL dataset: {e}")
        return None, None

def parse_lang_pair(lang_pair):
    """Parse a language pair string like 'en-es' or 'english-spanish'"""
    if not lang_pair or '-' not in lang_pair:
        return None, None
    
    src, tgt = lang_pair.strip().lower().split('-')
    
    # Handle both code and name formats
    if src in LANG_NAMES:
        src = LANG_NAMES[src]
    if tgt in LANG_NAMES:
        tgt = LANG_NAMES[tgt]
        
    # Validate codes
    if src not in LANG_CODES and src not in LANG_CODES.values():
        log(f"Unknown source language: {src}")
        return None, None
    if tgt not in LANG_CODES and tgt not in LANG_CODES.values():
        log(f"Unknown target language: {tgt}")
        return None, None
        
    return src, tgt

def main():
    p = argparse.ArgumentParser(description="Evaluate GGUF model via Ollama")
    p.add_argument("--model", default="hf.co/Tonic/GemmaX2-28-2B-gguf:BF16", help="Model to use for evaluation")
    p.add_argument("--output", default=os.getcwd(), help="Output directory for evaluation results")
    p.add_argument("--url", default=DEFAULT_URL, help="Ollama API URL")
    p.add_argument("--lang-pair", default="en-es", help="Language pair to evaluate (e.g., 'en-es' or 'english-spanish')")
    p.add_argument("--samples", type=int, default=10, help="Number of samples to evaluate")
    args = p.parse_args()
    
    dirs = setup_dirs(args.output)
    setup_loggers(dirs["logs_dir"])
    
    log(f"Starting evaluation with run ID: {RUN_ID}")
    log(f"Model: {args.model}")
    log(f"Ollama API URL: {args.url}")
    log(f"Output directory: {dirs['base']}")
    
    # Parse language pair
    src_code, tgt_code = parse_lang_pair(args.lang_pair)
    if not src_code or not tgt_code:
        log(f"Invalid language pair: {args.lang_pair}")
        log(f"Format should be 'en-es' or 'english-spanish'. Supported languages: {', '.join(LANG_CODES.keys())}")
        return
    
    src_lang = LANG_CODES.get(src_code, src_code)
    tgt_lang = LANG_CODES.get(tgt_code, tgt_code)
    log(f"Translation direction: {src_lang} → {tgt_lang}")
    
    # Load translation dataset
    source_texts, references = load_smol_dataset(src_code, tgt_code, args.samples)
    if not source_texts:
        log(f"Failed to load dataset for language pair: {args.lang_pair}")
        return
    
    # Format prompts using the specified template
    formatted_prompts = [
        format_prompt(text, src_lang, tgt_lang) 
        for text in source_texts
    ]
    
    data = {
        "prompts": formatted_prompts,
        "source_texts": source_texts,
        "references": references
    }
    
    start = time.time()
    pred_times = []
    eval_times = []
    
    log(f"Loaded SMOL dataset with {len(data['prompts'])} prompts")
    log("Starting model evaluation...")

    preds = []
    for i, prompt in enumerate(data["prompts"]):
        log(f"Processing prompt {i+1}/{len(data['prompts'])}")
        pred, t = query_ollama(prompt, args.model, args.url)
        pred_times.append(t)
        preds.append(pred)
        log(f"Source text: {data['source_texts'][i]}")
        log(f"Prompt used: {prompt}")
        log(f"Prediction: {pred}")
        log(f"Reference: {data['references'][i][0]}")
        log("---------------------------")
    
    eval_data = {
        "predictions": preds,
        "references": data["references"]
    }
    
    log("Loading ROUGE metric...")
    t_start = time.time()
    rouge = load("rouge")
    t_load = time.time() - t_start
    log(f"ROUGE metric loaded in {t_load:.2f}s")
    
    log("Computing ROUGE scores...")
    t_start = time.time()
    rouge_res = rouge.compute(
        predictions=eval_data["predictions"],
        references=eval_data["references"],
        rouge_types=["rouge1", "rouge2", "rougeL", "rougeLsum"],
        use_stemmer=True
    )
    t_compute = time.time() - t_start
    eval_times.append(t_compute)
    log(f"ROUGE scores computed in {t_compute:.2f}s")
    
    log("Loading BLEU metric...")
    t_start = time.time()
    bleu = load("bleu")
    t_load = time.time() - t_start
    log(f"BLEU metric loaded in {t_load:.2f}s")
    
    log("Computing BLEU scores...")
    t_start = time.time()
    bleu_res = bleu.compute(
        predictions=eval_data["predictions"],
        references=eval_data["references"],
        max_order=4,
        smooth=True
    )
    t_compute = time.time() - t_start
    eval_times.append(t_compute)
    log(f"BLEU scores computed in {t_compute:.2f}s")
    
    log("=== Evaluation Results ===")
    log("ROUGE Scores:")
    for k, v in rouge_res.items():
        log(f"{k}: {v:.4f}")
    
    log("BLEU Scores:")
    for k, v in bleu_res.items():
        if k == "precisions":
            log(f"{k}: {[round(p, 4) for p in v]}")
        else:
            log(f"{k}: {v:.4f}")
    
    telemetry = report_telemetry(start, eval_times, pred_times)
    
    results = {
        "rouge": {k: float(v) for k, v in rouge_res.items()},
        "bleu": {
            k: ([float(p) for p in v] if k == "precisions" else float(v)) 
            for k, v in bleu_res.items()
        },
        "metadata": {
            "model": args.model,
            "run_id": RUN_ID,
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
    
    # Save timestamped results directly to results directory
    out_file = os.path.join(dirs["results"], f"results_{src_code}_{tgt_code}_{RUN_ID}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
        log(f"Results saved to {out_file}")
    
    # Save latest results directly to results directory
    latest = os.path.join(dirs["results"], f"latest_{src_code}_{tgt_code}_results.json")
    try:
        if os.path.exists(latest):
            os.remove(latest)
        with open(latest, 'w') as f:
            json.dump(results, f, indent=4) 
        log(f"Latest results also available at {latest}")
    except Exception as e:
        log(f"Warning: Could not update latest results link: {e}")
    
    log(f"Evaluation for {src_lang}-{tgt_lang} completed successfully!")

if __name__ == "__main__":
    main()