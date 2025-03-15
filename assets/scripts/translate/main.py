import argparse
import asyncio
import json
import os
import re
import time
from typing import Dict, List, Tuple

import pandas as pd
import nltk
from datasets import load_dataset
from nltk.tokenize import sent_tokenize
from ollama import AsyncClient
from pydantic import BaseModel
from tqdm.asyncio import tqdm

nltk.download('punkt')

try:
    from runpodapi import RunPodClient
except ImportError:
    print("Warning: runpodapi not found. RunPod functionality disabled.")
    RunPodClient = None

# Markdown patterns
SPECIAL_PATTERNS = {
    r"\*\*\*(.*?)\*\*\*": ("<BOLD_ITALIC>$1</BOLD_ITALIC>", "**$1**"),  # Bold and italic
    r"\*\*(.*?)\*\*": ("<BOLD>$1</BOLD>", "**$1**"),                   # Bold
    r"\*(.*?)\*": ("<ITALIC>$1</ITALIC>", "*$1*"),                     # Italic
    r"`([^`]+?)`": ("<CODE>$1</CODE>", "`$1`"),                        # Inline code
    r"```([\s\S]*?)```": ("<PRE>$1</PRE>", "```$1```"),                # Code block
    r"#{6}\s+(.+?)(?:\n|$)": ("<H6>$1</H6>", "###### $1"),             # H6 header
    r"#{5}\s+(.+?)(?:\n|$)": ("<H5>$1</H5>", "##### $1"),              # H5 header
    r"#{4}\s+(.+?)(?:\n|$)": ("<H4>$1</H4>", "#### $1"),              # H4 header
    r"#{3}\s+(.+?)(?:\n|$)": ("<H3>$1</H3>", "### $1"),               # H3 header
    r"#{2}\s+(.+?)(?:\n|$)": ("<H2>$1</H2>", "## $1"),                # H2 header
    r"#\s+(.+?)(?:\n|$)": ("<H1>$1</H1>", "# $1"),                    # H1 header
    r"^\s*[-*+]\s+(.+?)(?=\n|$)": ("<LI>$1</LI>", "- $1"),            # Unordered list item
    r"^\s*\d+\.\s+(.+?)(?=\n|$)": ("<LI>$1</LI>", "1. $1"),           # Ordered list item
    r"\[(.+?)\]\((.+?)\)": ("<LINK text='$1' url='$2'>", "[$1]($2)"), # Links
    r"!\[(.+?)\]\((.+?)\)": ("<IMG alt='$1' src='$2'>", "![$1]($2)"), # Images
    r">\s+(.+?)(?=\n|$)": ("<QUOTE>$1</QUOTE>", "> $1"),              # Blockquote
    r"\n\n": ("<PARA>", "\n\n"),                                       # Paragraph break
    r"\n": ("<NL>", "\n"),                                             # Single newline
}

def preprocess_text(text: str) -> Tuple[str, Dict[str, str], List[Tuple[str, str]]]:
    """
    Preprocess Markdown text: replace special patterns with tags, split into sentences.
    Returns processed text, tag map, and sentence structure.
    """
    if not isinstance(text, str) or not text.strip():
        return text, {}, []

    tag_map = {}
    counter = 0
    structure = []  # List of (type, content) tuples: type can be 'text', 'tag', etc.

    # Process Markdown patterns
    for pattern, tag_template in SPECIAL_PATTERNS.items():
        def replace_match(match):
            nonlocal counter
            unique_tag = f"<TAG{counter}>"
            content = match.group(1) if "$1" in tag_template else match.group(0)
            tag_map[unique_tag] = tag_template.replace("$1", content) if "$1" in tag_template else tag_template
            counter += 1
            return unique_tag
        
        text = re.sub(pattern, replace_match, text, flags=re.DOTALL)

    # Split into sentences while preserving tags
    sentences = []
    current_sentence = ""
    for char in text:
        if char in "<>":
            if current_sentence:
                sentences.extend(sent_tokenize(current_sentence))
                current_sentence = ""
            structure.append(("tag", char))
        else:
            current_sentence += char
            structure.append(("text", char))
    if current_sentence:
        sentences.extend(sent_tokenize(current_sentence))

    return " ".join(sentences), tag_map, structure

def postprocess_text(translated_sentences: List[str], placeholder_map: Dict[str, str], structure: List[Tuple[str, str]]) -> str:
    """
    Reconstruct Markdown text from translated sentences, restoring placeholders and original patterns.
    """
    if not translated_sentences or not structure:
        return ""

    result = ""
    sentence_idx = 0
    char_idx = 0
    current_sentence = translated_sentences[sentence_idx] if translated_sentences else ""

    for item_type, content in structure:
        if item_type == "placeholder":
            # Replace placeholder with original Markdown
            tag_content = placeholder_map.get(content, content)
            for _, (tag, original_pattern) in SPECIAL_PATTERNS.items():
                if tag in tag_content:
                    if "<LINK" in tag_content or "<IMG" in tag_content:
                        # Extract text and url/src from the placeholder
                        text_match = re.search(r"text='([^']+)'", tag_content)
                        url_match = re.search(r"(url|src)='([^']+)'", tag_content)
                        text = text_match.group(1) if text_match else ""
                        url = url_match.group(2) if url_match else ""
                        result += original_pattern.replace("$1", text).replace("$2", url)
                    else:
                        content_match = re.search(r">(.+?)<", tag_content)
                        content_text = content_match.group(1) if content_match else ""
                        result += original_pattern.replace("$1", content_text)
                    break
            else:
                result += tag_content  # Fallback if no pattern matches
        elif item_type == "text":
            if sentence_idx < len(translated_sentences) and char_idx < len(current_sentence):
                result += current_sentence[char_idx]
                char_idx += 1
            if char_idx >= len(current_sentence) and sentence_idx < len(translated_sentences) - 1:
                sentence_idx += 1
                char_idx = 0
                current_sentence = translated_sentences[sentence_idx]

    return result.strip()

class RunPodEndpoint:
    def __init__(self, endpoint: str, language: str, model: str = "gemmax2-custom", is_pod_id: bool = True):
        self.endpoint = f"https://{endpoint}-11434.proxy.runpod.net" if is_pod_id else endpoint
        self.model = model
        self.language = language
        self.client = AsyncClient(host=self.endpoint)

    async def translate_text(self, text: str, src_lang: str, tgt_lang: str, retries: int = 3) -> str:
        processed_text, tag_map, structure = preprocess_text(text)
        if not processed_text:
            return ""

        # Split into sentences and translate individually
        sentences = sent_tokenize(processed_text)
        translated_sentences = []
        prompt_template = f"Translate this sentence from {src_lang} to {tgt_lang}:\n{src_lang}: {{sentence}}\n{tgt_lang}:"

        for sentence in sentences:
            prompt = prompt_template.format(sentence=sentence)
            for attempt in range(retries):
                try:
                    response = await self.client.generate(model=self.model, prompt=prompt)
                    if response and "response" in response:
                        translated = response["response"].split(f"{tgt_lang}:")[-1].strip()
                        translated_sentences.append(translated)
                        break
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Retry {attempt + 1}/{retries} failed: {e}")
                    if attempt == retries - 1:
                        translated_sentences.append("")
                        break

        return postprocess_text(translated_sentences, tag_map, structure)

class Feature(BaseModel):
    id: int
    thinking: str = ""
    response: str = ""
    thinking_translated: str = ""
    response_translated: str = ""
    query: str = ""
    source_data: str = ""
    category: str = ""
    endpoint: str = ""
    source: str = ""

LANGUAGES = [
    "Arabic", "Bengali", "Czech", "German", "English", "Spanish", "Persian", "French",
    "Hebrew", "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean", "Lao",
    "Malay", "Burmese", "Dutch", "Polish", "Portuguese", "Russian", "Thai", "Tagalog",
    "Turkish", "Urdu", "Vietnamese", "Chinese"
]

# Configuration
DATASET_NAME = "DataTonic/dark_thoughts_case_study_merged"
OUTPUT_DIR = "translated_dataset"
STATE_FILE = "translation_state.json"
BATCH_SIZE = 5
NUM_RUNPODS = 60
OFFLOAD_INTERVAL = 20
POD_STARTUP_DELAY = 120
MAX_POD_RETRIES = 6

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"completed": {}, "pending": {}, "last_batch": {}}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def offload_to_disk(df: pd.DataFrame, split_name: str, tgt_lang: str, batch_start: int, batch_end: int, state: Dict):
    output_split_dir = os.path.join(OUTPUT_DIR, f"data/{split_name}-translated")
    os.makedirs(output_split_dir, exist_ok=True)
    temp_path = os.path.join(output_split_dir, f"{tgt_lang}_batch_{batch_start}-{batch_end}.parquet")
    df.iloc[batch_start:batch_end].to_parquet(temp_path)
    state["pending"][f"{split_name}_{tgt_lang}"] = {
        "last_batch_start": batch_start,
        "last_batch_end": batch_end,
        "temp_file": temp_path
    }
    save_state(state)
    print(f"Offloaded batch {batch_start}-{batch_end} to {temp_path}")

def launch_runpods(api_key: str, num_pods: int = NUM_RUNPODS, hf_token: str = None):
    if not RunPodClient:
        print("RunPodClient not available. Running locally.")
        return []

    client = RunPodClient(api_key=api_key)
    pod_ids = []

    try:
        print("Fetching available templates...")
        templates = client.get_templates()
        ollama_template_id = None
        for template in templates:
            if "ollama/ollama" in template.get("imageName", ""):
                ollama_template_id = template["id"]
                print(f"Found existing Ollama template: {template['name']} (ID: {ollama_template_id})")
                break

        if not ollama_template_id:
            print("No Ollama template found, creating a new one...")
            template_config = {
                "name": "A40 Ollama Template",
                "imageName": "ollama/ollama",
                "containerDiskInGb": 50,
                "env": [{"key": "OLLAMA_HOST", "value": "0.0.0.0"}],
                "ports": ["11434/http"],
                "isServerless": False,
                "isPublic": True,
                "dockerStartCmd": ["/bin/bash", "-c", "apt update && apt install -y lshw && ollama serve &"]
            }
            new_template = client.create_template(template_config)
            ollama_template_id = new_template["id"]
            print(f"Created new Ollama template: {new_template['name']} (ID: {ollama_template_id})")

        pod_config = {
            "gpuCount": 1,
            "gpuTypeIds": ["NVIDIA A40"],
            "containerDiskInGb": 100,
            "volumeInGb": 120,
            "ports": ["11434/http"],
            "supportPublicIp": True,
            "imageName": "tonic01/ollama-gemmax2-28:latest",
            "env": {"OLLAMA_HOST": "0.0.0.0"},
            "dockerStartCmd": [
                "/bin/bash", "-c",
                "ollama serve & sleep 5 && "
                "echo 'FROM hf.co/mradermacher/GemmaX2-28-2B-v0.1-GGUF:Q8_0\n"
                "PARAMETER num_ctx 32768\n"
                "PARAMETER num_predict 32000\n"
                "PARAMETER num_gpu 99\n"
                "' > /tmp/Modelfile && "
                "ollama create gemmax2-custom -f /tmp/Modelfile && "
                "ollama run gemmax2-custom"
            ]
        }

        print(f"Launching {num_pods} pods with A40 GPUs and Ollama setup...")
        for i in range(num_pods):
            pod_name = f"Translation-Pod-{i+1}"
            print(f"Creating {pod_name}...")
            pod = client.create_pod_from_template(
                template_id=ollama_template_id,
                name=pod_name,
                additional_config=pod_config
            )
            pod_id = pod["id"]
            pod_ids.append((pod_id, pod_id))
            print(f"Created {pod_name} with ID: {pod_id}")
            client.start_pod(pod_id)
            print(f"Started {pod_name}")

        print(f"Waiting {POD_STARTUP_DELAY // 60} minutes before checking pod status...")
        time.sleep(POD_STARTUP_DELAY)

        running_pods = {}
        for attempt in range(1, MAX_POD_RETRIES + 1):
            print(f"\nStatus check attempt {attempt}/{MAX_POD_RETRIES} after {POD_STARTUP_DELAY // 60} minutes")
            all_running = True
            for pod_id, _ in pod_ids:
                if pod_id in running_pods:
                    continue
                pod_details = client.get_pod(pod_id, include_details=True)
                status = pod_details.get("desiredStatus", "UNKNOWN")
                print(f"Pod {pod_id}: Status - {status}")
                if status == "RUNNING":
                    running_pods[pod_id] = pod_id
                else:
                    all_running = False
            if all_running:
                print(f"All {num_pods} pods are running!")
                break
            if attempt < MAX_POD_RETRIES:
                print(f"Retrying in {POD_STARTUP_DELAY // 60} minutes...")
                time.sleep(POD_STARTUP_DELAY)
            else:
                print(f"Maximum retries reached. Proceeding with {len(running_pods)}/{num_pods} pods.")

        return list(running_pods.items())

    except Exception as e:
        print(f"Error launching pods: {str(e)}")
        return []

def terminate_runpods(runpod_info: List[Tuple[str, str]], api_key: str):
    if not RunPodClient or not runpod_info:
        return
    client = RunPodClient(api_key=api_key)
    for pod_id, _ in runpod_info:
        try:
            client.stop_pod(pod_id)
            print(f"Stopped pod {pod_id}")
            time.sleep(2)
            client.delete_pod(pod_id)
            print(f"Deleted pod {pod_id}")
        except Exception as e:
            print(f"Failed to clean up pod {pod_id}: {str(e)}")

def parse_thinking_and_response(response_text: str) -> Tuple[str, str]:
    if not response_text or not isinstance(response_text, str):
        return "", ""
    if "</think>" in response_text:
        parts = response_text.split("</think>", 1)
        thinking = parts[0].strip()
        if thinking.startswith("<think>"):
            thinking = thinking[len("<think>"):].strip()
        response = parts[1].strip() if len(parts) > 1 else ""
        return thinking, response
    return "", response_text.strip()

async def process_split(split_name: str, src_lang: str, initial_tgt_lang: str, endpoints: List[RunPodEndpoint], state: Dict, hf_token: str):
    dataset = load_dataset(DATASET_NAME, token=hf_token)
    data = dataset[split_name]
    df = pd.DataFrame({
        "id": list(range(len(data))),
        "response": data["response"],
        "query": data["query"],
        "source_data": data["source_data"],
        "category": data["category"],
        "endpoint": data["endpoint"],
        "source": data["source"]
    })

    df["thinking"], df["response"] = zip(*df["response"].apply(parse_thinking_and_response))
    df["thinking_translated"] = ["" for _ in range(len(df))]
    df["response_translated"] = ["" for _ in range(len(df))]

    output_split_dir = os.path.join(OUTPUT_DIR, f"data/{split_name}-translated")
    os.makedirs(output_split_dir, exist_ok=True)

    endpoint_idx = 0

    # Step 1: Translate to initial target language
    if f"{split_name}_{initial_tgt_lang}" not in state["completed"]:
        print(f"Translating {split_name} split to {initial_tgt_lang}...")
        last_batch_start = state.get("pending", {}).get(f"{split_name}_{initial_tgt_lang}", {}).get("last_batch_start", 0)

        for i in tqdm(range(last_batch_start, len(df), BATCH_SIZE), desc=f"{split_name} -> {initial_tgt_lang}"):
            batch_end = min(i + BATCH_SIZE, len(df))
            batch_thinking = df["thinking"][i:batch_end].tolist()
            batch_response = df["response"][i:batch_end].tolist()

            endpoint = endpoints[endpoint_idx % len(endpoints)]
            endpoint_idx += 1

            translated_thinking = await asyncio.gather(*[endpoint.translate_text(text, src_lang, initial_tgt_lang) for text in batch_thinking])
            translated_response = await asyncio.gather(*[endpoint.translate_text(text, src_lang, initial_tgt_lang) for text in batch_response])

            df.loc[i:batch_end - 1, "thinking_translated"] = translated_thinking[:batch_end - i]
            df.loc[i:batch_end - 1, "response_translated"] = translated_response[:batch_end - i]

            if (i // BATCH_SIZE) % OFFLOAD_INTERVAL == 0 and i > 0:
                offload_to_disk(df, split_name, initial_tgt_lang, 0, batch_end, state)

        initial_output_path = os.path.join(output_split_dir, f"{initial_tgt_lang}.parquet")
        df.to_parquet(initial_output_path)
        state["completed"][f"{split_name}_{initial_tgt_lang}"] = True
        if f"{split_name}_{initial_tgt_lang}" in state["pending"]:
            del state["pending"][f"{split_name}_{initial_tgt_lang}"]
        save_state(state)
        print(f"Saved initial translation to {initial_output_path}")

    # Step 2: Translate to all other languages
    for tgt_lang in LANGUAGES:
        if tgt_lang == initial_tgt_lang or tgt_lang == src_lang or f"{split_name}_{tgt_lang}" in state["completed"]:
            continue

        print(f"Translating {split_name} split to {tgt_lang}...")
        last_batch_start = state.get("pending", {}).get(f"{split_name}_{tgt_lang}", {}).get("last_batch_start", 0)
        translated_thinking = []
        translated_response = []

        for i in tqdm(range(last_batch_start, len(df), BATCH_SIZE), desc=f"{split_name} -> {tgt_lang}"):
            batch_end = min(i + BATCH_SIZE, len(df))
            batch_thinking = df["thinking_translated"][i:batch_end].tolist()
            batch_response = df["response_translated"][i:batch_end].tolist()

            endpoint = endpoints[endpoint_idx % len(endpoints)]
            endpoint_idx += 1

            translated_thinking_batch = await asyncio.gather(*[endpoint.translate_text(text, initial_tgt_lang, tgt_lang) for text in batch_thinking])
            translated_response_batch = await asyncio.gather(*[endpoint.translate_text(text, initial_tgt_lang, tgt_lang) for text in batch_response])

            translated_thinking.extend(translated_thinking_batch[:batch_end - i])
            translated_response.extend(translated_response_batch[:batch_end - i])

            if (i // BATCH_SIZE) % OFFLOAD_INTERVAL == 0 and i > 0:
                temp_df = pd.DataFrame({
                    "id": df["id"][:batch_end],
                    "thinking": df["thinking"][:batch_end],
                    "response": df["response"][:batch_end],
                    "thinking_translated": translated_thinking[:batch_end],
                    "response_translated": translated_response[:batch_end],
                    "query": df["query"][:batch_end],
                    "source_data": df["source_data"][:batch_end],
                    "category": df["category"][:batch_end],
                    "endpoint": df["endpoint"][:batch_end],
                    "source": df["source"][:batch_end]
                })
                offload_to_disk(temp_df, split_name, tgt_lang, 0, batch_end, state)

        out_df = pd.DataFrame({
            "id": df["id"],
            "thinking": df["thinking"],
            "response": df["response"],
            "thinking_translated": translated_thinking,
            "response_translated": translated_response,
            "query": df["query"],
            "source_data": df["source_data"],
            "category": df["category"],
            "endpoint": df["endpoint"],
            "source": df["source"]
        })

        output_path = os.path.join(output_split_dir, f"{tgt_lang}.parquet")
        out_df.to_parquet(output_path)
        state["completed"][f"{split_name}_{tgt_lang}"] = True
        if f"{split_name}_{tgt_lang}" in state["pending"]:
            del state["pending"][f"{split_name}_{tgt_lang}"]
        save_state(state)
        print(f"Saved {tgt_lang} translation to {output_path}")

async def main():
    api_key = os.getenv("RUNPOD_API_KEY", "")
    if not api_key:
        print("Error: RUNPOD_API_KEY not set in environment")
        return

    hf_token = os.getenv("HF_TOKEN", "")
    if not hf_token:
        print("Error: HF_TOKEN not set in environment. Please set it to access the Hugging Face dataset.")
        return

    state = load_state()
    runpod_info = launch_runpods(api_key, hf_token=hf_token)

    try:
        if not runpod_info:
            print("No pods launched or all pods failed to provide valid endpoints. Falling back to local endpoint.")
            endpoints = [RunPodEndpoint("http://localhost:11434", "English", is_pod_id=False)]
        else:
            endpoints = [
                RunPodEndpoint(pod_id, "English" if i % 2 == 0 else "Chinese", is_pod_id=True)
                for i, (pod_id, _) in enumerate(runpod_info) if pod_id
            ]
            if not endpoints:
                print("No valid endpoints created. Falling back to local endpoint.")
                endpoints = [RunPodEndpoint("http://localhost:11434", "English", is_pod_id=False)]
            print(f"Initialized {len(endpoints)} endpoints: {[e.endpoint for e in endpoints]}")

        tasks = [
            process_split("english", "English", "Chinese", endpoints, state, hf_token),
            process_split("chinese", "Chinese", "English", endpoints, state, hf_token)
        ]
        await asyncio.gather(*tasks)
        print("Translation process completed!")
    finally:
        terminate_runpods(runpod_info, api_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate dataset across multiple languages.")
    args = parser.parse_args()
    asyncio.run(main())