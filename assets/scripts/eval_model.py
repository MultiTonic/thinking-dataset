import requests
import json
from evaluate import load

# Ollama API endpoint (assuming it's running locally)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Function to query the GGUF model via Ollama API
def query_ollama(prompt, model="hf.co/Tonic/GemmaX2-28-2B-gguf:BF16"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result["response"].strip()
    else:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

# Sample dataset for evaluation (replace with your own dataset if needed)
# Here, we use simple translation-like examples for demonstration
sample_data = {
    "prompts": [
        "Translate: The quick brown fox jumps over the lazy dog.",
        "Translate: She sells seashells by the seashore."
    ],
    "references": [
        ["The quick brown fox jumps over the lazy dog."],  # Single reference per prediction
        ["She sells seashells by the seashore."]
    ]
}

# Generate predictions using the GGUF model
predictions = []
for prompt in sample_data["prompts"]:
    pred = query_ollama(prompt)
    predictions.append(pred)
    print(f"Prompt: {prompt}\nPrediction: {pred}\n")

# Prepare data for evaluation
eval_dataset = {
    "predictions": predictions,
    "references": sample_data["references"]
}

# Load evaluation metrics
rouge_metric = load("rouge")
bleu_metric = load("bleu")

# Compute ROUGE scores
rouge_results = rouge_metric.compute(
    predictions=eval_dataset["predictions"],
    references=eval_dataset["references"],
    rouge_types=["rouge1", "rouge2", "rougeL", "rougeLsum"],
    use_stemmer=True
)

# Compute BLEU scores
bleu_results = bleu_metric.compute(
    predictions=eval_dataset["predictions"],
    references=eval_dataset["references"],
    max_order=4,
    smooth=True
)

# Print results
print("=== Evaluation Results ===")
print("\nROUGE Scores:")
for key, value in rouge_results.items():
    print(f"{key}: {value:.4f}")

print("\nBLEU Scores:")
for key, value in bleu_results.items():
    if key == "precisions":
        print(f"{key}: {[round(p, 4) for p in value]}")
    else:
        print(f"{key}: {value:.4f}")

# Optional: Save results to a file
with open("evaluation_results.json", "w") as f:
    results = {"rouge": rouge_results, "bleu": bleu_results}
    json.dump(results, f, indent=4)
    print("\nResults saved to 'evaluation_results.json'")