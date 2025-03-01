import argparse
import json
import logging
import os
import time
import requests
from datetime import datetime
from evaluate import load

RUN_ID = f"{int(time.time())}"
DEFAULT_URL = "http://localhost:11434/api/generate"
c_log = logging.getLogger("console")
f_log = logging.getLogger("file")

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

def main():
    p = argparse.ArgumentParser(description="Evaluate GGUF model via Ollama")
    p.add_argument("--model", default="hf.co/Tonic/GemmaX2-28-2B-gguf:BF16", help="Model to use for evaluation")
    p.add_argument("--output", default=os.getcwd(), help="Output directory for evaluation results")
    p.add_argument("--url", default=DEFAULT_URL, help="Ollama API URL")
    args = p.parse_args()
    
    dirs = setup_dirs(args.output)
    setup_loggers(dirs["logs_dir"])
    
    log(f"Starting evaluation with run ID: {RUN_ID}")
    log(f"Model: {args.model}")
    log(f"Ollama API URL: {args.url}")
    log(f"Output directory: {dirs['base']}")
    
    start = time.time()
    pred_times = []
    eval_times = []
    data = {
        "prompts": [
            "Translate: The quick brown fox jumps over the lazy dog.",
            "Translate: She sells seashells by the seashore."
        ],
        "references": [
            ["The quick brown fox jumps over the lazy dog."],
            ["She sells seashells by the seashore."]
        ]
    }
    
    log(f"Loaded sample dataset with {len(data['prompts'])} prompts")
    log("Starting model evaluation...")

    preds = []
    for i, prompt in enumerate(data["prompts"]):
        log(f"Processing prompt {i+1}/{len(data['prompts'])}")
        pred, t = query_ollama(prompt, args.model, args.url)
        pred_times.append(t)
        preds.append(pred)
        log(f"Prompt: {prompt}")
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
            "prompts": data["prompts"],
            "references": data["references"],
            "predictions": preds,
        },
        "telemetry": telemetry
    }
    
    # Save timestamped results directly to results directory
    out_file = os.path.join(dirs["results"], f"results_{RUN_ID}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
        log(f"Results saved to {out_file}")
    
    # Save latest results directly to results directory
    latest = os.path.join(dirs["results"], "latest_results.json")
    try:
        if os.path.exists(latest):
            os.remove(latest)
        with open(latest, 'w') as f:
            json.dump(results, f, indent=4) 
        log(f"Latest results also available at {latest}")
    except Exception as e:
        log(f"Warning: Could not update latest results link: {e}")
    
    log("Evaluation completed successfully!")

if __name__ == "__main__":
    main()