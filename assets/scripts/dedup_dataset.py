import os
import logging
from datasets import load_dataset, DatasetDict, Dataset, Features, Value
from huggingface_hub import login
import json
from tqdm.auto import tqdm
from rapidfuzz import fuzz
import heapq
import shutil
import re

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def sort_batch(batch):
    """Sort a batch by the first 'case_study' item."""
    return sorted(batch, key=lambda x: x.get("case_study", [])[0] if x.get("case_study", []) else "")

def write_sorted_batch(batch, batch_index, cache_dir):
    """Write a sorted batch to a temporary file with error handling."""
    sorted_batch = sort_batch(batch)
    temp_file = os.path.join(cache_dir, f"sorted_batch_{batch_index}.jsonl")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            for sample in sorted_batch:
                f.write(json.dumps(sample) + "\n")
        logging.debug(f"Wrote {len(sorted_batch)} samples to {temp_file}")
    except IOError as e:
        logging.error(f"Failed to write to {temp_file}: {e}")
        raise
    return temp_file

def merge_sorted_files(temp_files, output_file):
    """Merge sorted temporary files into a single sorted file."""
    logging.info("Merging sorted batches...")
    file_handles = [open(tf, "r", encoding="utf-8") for tf in temp_files]
    lines = heapq.merge(*[iter(fh) for fh in file_handles], 
                       key=lambda x: json.loads(x)["case_study"][0] if json.loads(x)["case_study"] else "")
    
    with open(output_file, "w", encoding="utf-8") as out_f:
        for line in tqdm(lines, desc="Merging sorted files", unit="lines"):
            out_f.write(line)
    
    for fh in file_handles:
        fh.close()
    return output_file

def deduplicate_sorted_file(sorted_file, output_file, similarity_threshold=0.80, batch_size=1000):
    """Deduplicate a sorted file using fuzzy matching on the first case_study item."""
    seen_texts = []
    max_seen_texts = 2000  # Limit memory usage
    deduplicated_samples = []

    def process_sample(sample):
        case_study = sample.get("case_study", [])
        if not case_study or not isinstance(case_study, list):
            logging.warning(f"Skipping sample with invalid 'case_study': {sample}")
            return None
        
        first_case = case_study[0].strip()
        if not first_case:
            logging.warning(f"Skipping sample with empty first case_study: {sample}")
            return None

        for seen_text in seen_texts[-max_seen_texts:]:
            score = fuzz.token_sort_ratio(first_case, seen_text) / 100.0
            if score >= similarity_threshold:
                logging.debug(f"Similar entry found: {first_case} ~ {seen_text} (score: {score*100:.1f}%)")
                return None

        seen_texts.append(first_case)
        return sample

    logging.info("Deduplicating sorted file with fuzzy matching...")
    with open(sorted_file, "r", encoding="utf-8") as f:
        batch = []
        for line in tqdm(f, desc="Reading sorted file", unit="lines"):
            sample = json.loads(line)
            batch.append(sample)
            if len(batch) >= batch_size:
                for sample in batch:
                    result = process_sample(sample)
                    if result:
                        deduplicated_samples.append(result)
                batch = []

        for sample in batch:
            result = process_sample(sample)
            if result:
                deduplicated_samples.append(result)

    if not deduplicated_samples:
        logging.error("No deduplicated samples found.")
        return None

    with open(output_file, "w", encoding="utf-8") as f:
        for sample in tqdm(deduplicated_samples, desc="Writing deduplicated data", unit="samples"):
            f.write(json.dumps(sample) + "\n")
    
    return output_file

def extract_think_content(text):
    """Extract content between <think> and </think> tags."""
    pattern = r"<think>(.*?)</think>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0].strip() if matches else ""

def reformat_dataset(deduplicated_file, cache_dir, split_name):
    """Reformat the deduplicated dataset into individual case_study rows with prompts and think content."""
    reformatted_samples = []
    prompt_template_en = """{case_study_info}
Stakeholder: {stakeholder} {motivation}
"""
    prompt_template_cn = """{case_study_info}
利益相关者: {stakeholder} {motivation}
"""

    with open(deduplicated_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc=f"Reformatting {split_name} dataset", unit="lines"):
            sample = json.loads(line)
            case_study_list = sample.get("case_study", [])
            original_info = sample.get("original_info", "")
            stakeholders = sample.get("stakeholders", {})
            endpoint = sample.get("endpoint", "")
            
            if not case_study_list or not stakeholders:
                logging.warning(f"Skipping sample with missing case_study or stakeholders: {sample}")
                continue

            stakeholders_extracted = stakeholders.get("extracted", [])
            motivations = stakeholders.get("motivation", [])
            stakeholder_names = stakeholders.get("stakeholder", [])

            min_length = min(len(stakeholders_extracted), len(motivations), len(stakeholder_names))
            stakeholders_extracted = stakeholders_extracted[:min_length]
            motivations = motivations[:min_length]
            stakeholder_names = stakeholder_names[:min_length]

            for case_study_info in case_study_list:
                if not case_study_info.strip():
                    continue
                
                think_content = extract_think_content(case_study_info)
                clean_case_study_info = re.sub(r"<think>.*?</think>", "", case_study_info, flags=re.DOTALL).strip()

                for i in range(min_length):
                    if stakeholders_extracted[i].lower() == "yes":
                        prompt = prompt_template_en if split_name == "english" else prompt_template_cn
                        formatted_prompt = prompt.format(
                            case_study_info=clean_case_study_info,
                            stakeholder=stakeholder_names[i],
                            motivation=motivations[i]
                        )
                        reformatted_samples.append({
                            "case_study_info": clean_case_study_info,
                            "think_content": think_content,
                            "prompt": formatted_prompt.strip(),
                            "original_info": original_info,
                            "endpoint": endpoint
                        })

    if not reformatted_samples:
        logging.error(f"No reformatted samples generated for split {split_name}.")
        return None

    output_file = os.path.join(cache_dir, f"reformatted_{split_name}.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in tqdm(reformatted_samples, desc=f"Writing reformatted {split_name} data", unit="samples"):
            f.write(json.dumps(sample) + "\n")

    features = Features({
        "case_study_info": Value("string"),
        "think_content": Value("string"),
        "prompt": Value("string"),
        "original_info": Value("string"),
        "endpoint": Value("string")
    })
    return Dataset.from_json(output_file, features=features)

def process_split(dataset, split_name, batch_size=10000, cache_dir="cache", similarity_threshold=0.80):
    """Process a single dataset split: filter short case_study_info, sort, deduplicate, and reformat."""
    split_cache_dir = os.path.join(cache_dir, split_name)
    os.makedirs(split_cache_dir, exist_ok=True)

    # Filter out rows where case_study_info[0] is less than 7 characters
    logging.info(f"Filtering {split_name} dataset for case_study_info >= 7 characters...")
    filtered_data = []
    for sample in tqdm(dataset, desc=f"Filtering {split_name} dataset", unit="samples"):
        case_study = sample.get("case_study", [])
        if case_study and isinstance(case_study, list) and len(case_study[0].strip()) >= 7:
            filtered_data.append(sample)
        else:
            logging.debug(f"Filtered out sample with short case_study_info: {sample}")

    if not filtered_data:
        logging.error(f"No samples remain after filtering for split {split_name}.")
        return None

    # Convert filtered data back to a Dataset object if needed, or process as list
    temp_files = []
    batch_count = 0
    for i in tqdm(range(0, len(filtered_data), batch_size), desc=f"Processing {split_name} batches", unit="batch"):
        batch = filtered_data[i:i + batch_size]
        temp_file = write_sorted_batch(batch, batch_count, split_cache_dir)
        temp_files.append(temp_file)
        batch_count += 1

    sorted_file = os.path.join(split_cache_dir, f"sorted_{split_name}.jsonl")
    merge_sorted_files(temp_files, sorted_file)

    deduplicated_file = os.path.join(split_cache_dir, f"deduplicated_{split_name}.jsonl")
    deduplicated_file = deduplicate_sorted_file(sorted_file, deduplicated_file, similarity_threshold, batch_size)

    if not deduplicated_file or not os.path.exists(deduplicated_file):
        logging.error(f"Deduplication failed for split {split_name}.")
        return None

    reformatted_dataset = reformat_dataset(deduplicated_file, split_cache_dir, split_name)
    if reformatted_dataset is None:
        logging.error(f"Reformatting failed for split {split_name}.")
        return None

    shutil.rmtree(split_cache_dir)
    logging.info(f"Processed {split_name} split with {len(reformatted_dataset)} unique samples.")
    return reformatted_dataset

def push_to_hub(dataset_dict, repo_name, hf_token):
    """Push the processed dataset to Hugging Face Hub."""
    login(token=hf_token)
    dataset_dict.push_to_hub(repo_name, token=hf_token)
    logging.info(f"Dataset pushed to Hugging Face Hub: {repo_name}")

def main():
    setup_logging()
    logging.info("Loading dataset...")
    dataset_splits = load_dataset("Tonic/scaleway_r1_dark_thoughts_casestudies")
    processed_datasets = {}

    for split_name in ["english", "chinese"]:
        if split_name not in dataset_splits:
            logging.warning(f"Split {split_name} not found in dataset. Skipping.")
            continue
        
        logging.info(f"Processing split: {split_name}")
        dataset = dataset_splits[split_name]
        processed_dataset = process_split(dataset, split_name, batch_size=10000, similarity_threshold=0.80)
        
        if processed_dataset is None:
            logging.error(f"Failed to process split {split_name}")
            continue
        
        processed_datasets[split_name] = processed_dataset
        output_path = f"processed_dataset_{split_name}"
        processed_dataset.save_to_disk(output_path)
        logging.info(f"Processed dataset for split {split_name} saved to {output_path}")

    if not processed_datasets:
        logging.error("No processed datasets to push.")
        return

    processed_dataset_dict = DatasetDict(processed_datasets)
    push_to_hub(processed_dataset_dict, 
                "scaleway_r1_dark_thoughts_casestudies_processed_fuzzy_think_splits", 
                "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")

if __name__ == "__main__":
    main()