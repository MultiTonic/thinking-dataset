# flake8: noqa

# Standard library imports
import asyncio
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any

# Third-party imports - Data & ML
from datasets import load_dataset, DatasetDict, Dataset
from huggingface_hub import login
from openai import OpenAI
import requests

# Third-party imports - Utilities
from tenacity import (retry, stop_after_attempt, wait_exponential,
                      retry_if_exception_type, before_sleep_log, after_log)

# Third-party imports - Rich console
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.panel import Panel
import logging

MODEL_NAME = "deepseek-r1-distill-llama-70b"
BATCH_SIZE = 5
SAVE_INTERVAL = 10
MAX_TOKENS = 3950
TEMPERATURE = 0.75
TOP_P = 0.95
PRESENCE_PENALTY = 0
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
CACHE_SIZE = 100

REQUEST_DELAY = 1.0
RATE_LIMIT_DELAY = 60.0
MAX_CONCURRENT_REQUESTS = 3

HF_TOKEN = "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"

SYSTEM_PROMPT_URLS = {
    'en':
    'https://gist.githubusercontent.com/p3nGu1nZz/42204d92fe5d27318b6eb8a04b220889/raw',
    'cn':
    'https://gist.githubusercontent.com/p3nGu1nZz/22ed3c43a66997cbe228529a8b86bfc1/raw'
}

SCALEWAY_CONFIGS = [{
    "api_key":
    "aedfc8cc-c3fc-408b-8724-8561b90e6c51",
    "base_url":
    "https://api.scaleway.ai/4a1f7f6d-712d-4d1b-ae6c-8a8377df9f8e/v1"
}, {
    "api_key":
    "f03456f3-3143-4f0e-a667-2cfac1c24ff1",
    "base_url":
    "https://api.scaleway.ai/76f74175-f023-4fd0-a884-63975787c13c/v1"
}, {
    "api_key":
    "f8879976-7908-40e6-a88a-5761f88aae16",
    "base_url":
    "https://api.scaleway.ai/774f5a61-5f80-4f59-90f2-da7f3f48ba30/v1"
}, {
    "api_key":
    "bd15070f-fa5e-47ef-bbed-e8a43cfdf521",
    "base_url":
    "https://api.scaleway.ai/5758a160-1e32-4bf8-9d65-8f819a9101e9/v1"
}, {
    "api_key":
    "c752b005-1f62-4112-9205-920d519216e6",
    "base_url":
    "https://api.scaleway.ai/444c4241-bfe4-42ac-b397-4b47cbb9d3c1/v1"
}, {
    "api_key":
    "9ba8e980-e480-484e-8d55-12c9172d63c2",
    "base_url":
    "https://api.scaleway.ai/1a920b0d-50a3-4cee-8b63-7177434bc0f6/v1"
}]

DATASET_NAME = "scaleway_r1_dark_thoughts_casestudies"
SOURCE_DATASET = "DataTonic/dark_thoughts_stakeholders_80"
DATASET_SPLIT = "english"
DATASET_PRIVATE = True

install_rich_traceback(show_locals=False,
                       max_frames=5,
                       word_wrap=True,
                       suppress=[])
console = Console(width=100)


def log_error(msg: str, error: Exception = None) -> None:
    console.print(f"[bold red]{msg}[/]")
    if error:
        console.print_exception(show_locals=False, max_frames=3)


install_rich_traceback(show_locals=True)
console = Console()

BASE_DIR = Path(os.getcwd())
DATA_DIR = BASE_DIR / "data" / "case_studies"
TEMP_DIR = BASE_DIR / "data" / "temp"
LOG_DIR = BASE_DIR / "logs"

for dir_path in [DATA_DIR, TEMP_DIR, LOG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(message)s",
                    datefmt="[%X]",
                    handlers=[
                        RichHandler(console=console,
                                    rich_tracebacks=True,
                                    markup=True),
                        logging.FileHandler(LOG_DIR / "process.log")
                    ])
logger = logging.getLogger(__name__)

login(token=HF_TOKEN)


@lru_cache(maxsize=CACHE_SIZE)
def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


@lru_cache(maxsize=2)
def fetch_system_prompt(lang: str) -> str:
    try:
        url = SYSTEM_PROMPT_URLS.get(lang)
        if not url:
            raise ValueError(f"No URL found for language {lang}")

        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        logger.error(f"Failed to fetch {lang} prompt: {str(e)}")
        raise


class ScalewayClientManager:

    def __init__(self, configs: List[Dict[str, str]]):
        self.configs = configs
        self.current_index = 0
        self.clients = [
            OpenAI(base_url=config["base_url"], api_key=config["api_key"])
            for config in configs
        ]
        self.last_request_time = 0

    def get_client(self) -> OpenAI:
        client = self.clients[self.current_index]
        self.rotate_key()
        return client

    def get_current_config(self) -> Dict[str, str]:
        return self.configs[self.current_index]

    def rotate_key(self):
        self.current_index = (self.current_index + 1) % len(self.configs)
        config = self.get_current_config()
        logger.info(f"Rotated to API key with base URL {config['base_url']}")


class TokenTracker:

    def __init__(self):
        self.start_time = time.time()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.requests_completed = 0
        self.total_requests = 0

    def set_total_requests(self, total: int):
        self.total_requests = total * 2

    def log_request(self, input_text: str, output_text: str):
        self.total_input_tokens += len(input_text) / 6.5
        self.total_output_tokens += len(output_text) / 6.5
        self.requests_completed += 1
        minutes = (time.time() - self.start_time) / 60
        logger.info(
            f"Request {self.requests_completed}/{self.total_requests} complete. "
            f"Tokens (in/out/per min): {self.total_input_tokens:.0f}/{self.total_output_tokens:.0f}/"
            f"{((self.total_input_tokens + self.total_output_tokens) / minutes if minutes > 0 else 0):.1f}"
        )


class CaseStudyGenerator:

    def __init__(self,
                 model_name: str = MODEL_NAME,
                 batch_size: int = BATCH_SIZE,
                 save_interval: int = SAVE_INTERVAL):
        self.model_name = model_name
        self.batch_size = batch_size
        self.save_interval = save_interval
        self.client_manager = ScalewayClientManager(SCALEWAY_CONFIGS)

        console.print("[yellow]Fetching system prompts from GitHub...[/]")
        try:
            self.system_prompt_en = fetch_system_prompt('en')
            self.system_prompt_cn = fetch_system_prompt('cn')
            console.print("[green]Successfully loaded system prompts[/]")
        except Exception:
            console.print(
                "[red]Failed to load system prompts, cannot continue[/]")
            raise

        self.prompt_template_en = """
        {case_study_info}
        Stakeholder: {stakeholder} {motivation}
        """
        self.prompt_template_cn = """{case_study_info}
        利益相关者: {stakeholder} {motivation}
        """
        self.fallback_prompt_en = """{case_study_info}
        """
        self.fallback_prompt_cn = """{case_study_info}
        """

        self.response_counter = 0
        self.token_tracker = TokenTracker()

    @lru_cache(maxsize=CACHE_SIZE)
    def prepare_prompt_template(self, case_study_info: str, stakeholder: str,
                                motivation: str, lang: str) -> str:
        template = self.prompt_template_en if lang == 'en' else self.prompt_template_cn
        return template.format(case_study_info=case_study_info,
                               stakeholder=stakeholder,
                               motivation=motivation)

    def prepare_prompts(self, row: Dict[str, Any]) -> List[Dict[str, str]]:
        try:
            case_study_info = row.get('case_study_info', '')
            stakeholders = row.get('stakeholders', {})
            stakeholder_list = stakeholders.get('stakeholder', [])
            motivation_list = stakeholders.get('motivation', [])

            prompts = []
            if stakeholder_list and motivation_list and len(
                    stakeholder_list) == len(motivation_list):
                for stakeholder, motivation in zip(stakeholder_list,
                                                   motivation_list):
                    prompts.append({
                        'en':
                        self.prepare_prompt_template(
                            case_study_info=case_study_info,
                            stakeholder=stakeholder,
                            motivation=motivation,
                            lang='en'),
                        'cn':
                        self.prepare_prompt_template(
                            case_study_info=case_study_info,
                            stakeholder=stakeholder,
                            motivation=motivation,
                            lang='cn')
                    })
            else:
                prompts.append({
                    'en':
                    self.fallback_prompt_en.format(
                        case_study_info=case_study_info),
                    'cn':
                    self.fallback_prompt_cn.format(
                        case_study_info=case_study_info)
                })
            return prompts
        except Exception as e:
            logger.error(f"Error preparing prompts: {str(e)}")
            return [{'en': '', 'cn': ''}]

    def save_response(self, response: str, metadata: Dict[str, Any],
                      lang: str) -> Path:
        filename = f"{self.response_counter:06d}_{lang}.txt"
        filepath = TEMP_DIR / filename

        content = (f"Original Info: {metadata.get('original_info', '')}\n"
                   f"Stakeholder: {metadata.get('stakeholder', '')}\n"
                   f"Motivation: {metadata.get('motivation', '')}\n"
                   f"Language: {lang}\n"
                   f"Response:\n{response}\n")

        filepath.write_text(content, encoding='utf-8')
        self.response_counter += 1
        return filepath

    @retry(retry=retry_if_exception_type((Exception)),
           stop=stop_after_attempt(MAX_RETRIES),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           before_sleep=before_sleep_log(logger, logging.WARNING),
           after=after_log(logger, logging.INFO))
    async def _make_completion_request(self, prompt_text: str,
                                       system_prompt: str) -> str:
        """Simplified completion request without status display."""
        try:
            current_time = time.time()
            if (current_time -
                    self.client_manager.last_request_time) < REQUEST_DELAY:
                await asyncio.sleep(REQUEST_DELAY -
                                    (current_time -
                                     self.client_manager.last_request_time))

            client = self.client_manager.get_client()
            config = self.client_manager.get_current_config()
            logger.info(f"Making API request to {config['base_url']}")

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": prompt_text
                }],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                presence_penalty=PRESENCE_PENALTY,
                stream=True)

            full_response = "".join(
                chunk.choices[0].delta.content for chunk in response
                if chunk.choices and chunk.choices[0].delta.content)

            self.client_manager.last_request_time = time.time()
            self.token_tracker.log_request(prompt_text, full_response)
            return full_response.strip()

        except Exception as e:
            if "429" in str(e):
                await asyncio.sleep(RATE_LIMIT_DELAY)
            log_error("API request failed", e)
            raise

    async def generate_case_study(self, prompt: Dict[str, str],
                                  language: str) -> str:
        """Remove status parameter and simplify."""
        try:
            prompt_text = prompt['en'] if language == 'en' else prompt['cn']
            system_prompt = self.system_prompt_en if language == 'en' else self.system_prompt_cn

            if not prompt_text:
                raise ValueError(f"Empty prompt for {language}")

            logger.info(f"Starting generation for {language}")
            result = await self._make_completion_request(
                prompt_text, system_prompt)
            return result

        except Exception as e:
            logger.error(f"Final generation error for {language}: {str(e)}")
            return ""

    def prepare_dataset_dict(
            self, case_studies: List[Dict[str, Any]]) -> DatasetDict:
        en_data = [{
            'case_study': item['case_study_en'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in case_studies]

        cn_data = [{
            'case_study': item['case_study_cn'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in case_studies]

        return DatasetDict({
            'english': Dataset.from_list(en_data),
            'chinese': Dataset.from_list(cn_data)
        })

    async def save_interim_results(self, case_studies: List[Dict[str, Any]],
                                   batch_idx: int) -> None:
        """Remove console.status and simplify."""
        logger.info("Saving interim results...")
        en_data = [{
            'case_study': item['case_study_en'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in case_studies if item.get('case_study_en')]

        cn_data = [{
            'case_study': item['case_study_cn'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in case_studies if item.get('case_study_cn')]

        # Save English dataset
        if en_data:
            en_dataset = Dataset.from_list(en_data)
            en_save_path = DATA_DIR / f"interim_batch_{batch_idx}_en"
            en_dataset.save_to_disk(str(en_save_path))
            logger.info(f"Saved English interim batch {batch_idx}")

        # Save Chinese dataset
        if cn_data:
            cn_dataset = Dataset.from_list(cn_data)
            cn_save_path = DATA_DIR / f"interim_batch_{batch_idx}_cn"
            cn_dataset.save_to_disk(str(cn_save_path))
            logger.info(f"Saved Chinese interim batch {batch_idx}")

        logger.info(f"Saved interim batch {batch_idx} for both languages")

    async def retry_language_generation(self,
                                        prompt: Dict[str, str],
                                        language: str,
                                        row: Dict[str, Any],
                                        max_retries: int = 3) -> str:
        """Retry individual language generation until success or max retries."""
        for attempt in range(max_retries):
            try:
                result = await self.generate_case_study(prompt, language)
                if result:  # Only return if we got a valid result
                    return result
                await asyncio.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                logger.error(
                    f"Attempt {attempt + 1} failed for {language}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)
        return None

    async def save_single_generation(self, result: str, metadata: Dict[str,
                                                                       Any],
                                     language: str) -> Path:
        """Save single generation result to temp directory."""
        filename = f"generation_{self.response_counter:06d}_{language}.json"
        filepath = TEMP_DIR / filename

        data = {
            'case_study': result,
            'original_info': metadata['original_info'],
            'stakeholders': metadata.get('stakeholders', {}),
            'endpoint': 'scaleway',
            'language': language,
            'timestamp': time.time()
        }

        interim_dataset = Dataset.from_list([data])
        interim_dataset.save_to_disk(str(filepath))
        self.response_counter += 1
        return filepath

    async def process_language_generation(
            self, prompt: Dict[str, str], language: str,
            row: Dict[str, Any]) -> Dict[str, Any]:
        """Process generation with retries for each language."""
        result = await self.retry_language_generation(prompt, language, row)
        if not result:
            return None

        metadata = {
            'original_info': row.get('case_study_info', ''),
            'stakeholder': row.get('stakeholders',
                                   {}).get('stakeholder', [''])[0],
            'motivation': row.get('stakeholders', {}).get('motivation',
                                                          [''])[0],
            'stakeholders': row.get('stakeholders', {})
        }

        # Save to temp directory
        saved_path = await self.save_single_generation(result, metadata,
                                                       language)
        logger.info(f"Saved {language} response to {saved_path}")

        return {'result': result, 'saved_path': saved_path}

    async def process_row(self, row: Dict[str, Any]) -> Dict[str, List[str]]:
        try:
            start_time = time.time()
            stakeholder = row.get('stakeholders', {}).get('stakeholder',
                                                          [''])[0]
            logger.info(f"Processing stakeholder: {stakeholder}")

            prompts = self.prepare_prompts(row)
            en_outputs = []
            cn_outputs = []
            saved_paths = []

            for prompt in prompts:
                # Process languages sequentially to ensure both succeed
                en_result = await self.process_language_generation(
                    prompt, 'en', row)
                cn_result = await self.process_language_generation(
                    prompt, 'cn', row)

                # Only proceed if both generations succeeded
                if en_result and cn_result:
                    en_outputs.append(en_result['result'])
                    cn_outputs.append(cn_result['result'])
                    saved_paths.extend(
                        [en_result['saved_path'], cn_result['saved_path']])
                else:
                    logger.error(
                        f"Failed to generate both languages for stakeholder {stakeholder}"
                    )
                    continue

            duration = time.time() - start_time
            logger.info(f"Completed processing in {duration:.2f}s")

            if not (en_outputs
                    and cn_outputs):  # Only return if we have both languages
                raise ValueError(
                    "Failed to generate complete pair of translations")

            return {
                'case_study_en': en_outputs,
                'case_study_cn': cn_outputs,
                'original_info': row.get('case_study_info', ''),
                'stakeholders': row.get('stakeholders', {}),
                'endpoint': 'scaleway',
                'temp_files': saved_paths
            }

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            raise

    async def process_batch(
            self, batch: List[Dict[str, Any]], batch_idx: int,
            all_case_studies: List[Dict[str,
                                        Any]]) -> List[Dict[str, List[str]]]:
        try:
            tasks = [self.process_row(row) for row in batch]
            results = await asyncio.gather(*tasks)

            if len(all_case_studies) + len(results) >= self.save_interval:
                await self.save_interim_results(all_case_studies + results,
                                                batch_idx)

            return results
        except Exception as e:
            log_error(f"Error processing batch {batch_idx}", e)
            return []


async def get_next_dataset_version(base_name: str) -> str:
    try:
        from huggingface_hub import HfApi
        api = HfApi()

        version = 1
        while True:
            dataset_name = f"{base_name}-{version}" if version > 1 else base_name
            try:
                api.dataset_info(dataset_name)
                version += 1
            except Exception:
                return dataset_name
    except Exception as e:
        logger.error(f"Error finding next dataset version: {str(e)}")
        return base_name


async def ensure_dataset_exists(name: str) -> str:
    try:
        from huggingface_hub import HfApi
        api = HfApi()

        dataset_name = await get_next_dataset_version(name)
        logger.info(f"Using dataset name: {dataset_name}")

        empty_dataset = DatasetDict({
            'english': Dataset.from_list([]),
            'chinese': Dataset.from_list([])
        })
        empty_dataset.push_to_hub(dataset_name,
                                  private=DATASET_PRIVATE,
                                  token=HF_TOKEN)
        logger.info(f"Created new dataset {dataset_name}")
        return dataset_name

    except Exception as e:
        logger.error(f"Error ensuring dataset exists: {str(e)}")
        raise


async def main():
    try:
        console.print("[bold green]Starting case study generation[/]")
        dataset_name = await ensure_dataset_exists(DATASET_NAME)
        dataset = load_dataset(SOURCE_DATASET, split=DATASET_SPLIT)
        total_items = len(dataset)  # Define total_items here

        generator = CaseStudyGenerator()
        generator.token_tracker.set_total_requests(total_items)

        content_items = [dict(row) for row in dataset]
        batches = [
            content_items[i:i + generator.batch_size]
            for i in range(0, len(content_items), generator.batch_size)
        ]

        all_case_studies = []
        processed_count = 0

        for batch_idx, batch in enumerate(batches):
            try:
                results = await generator.process_batch(
                    batch, batch_idx, all_case_studies)
                all_case_studies.extend(results)
                processed_count += len(results)
            except Exception as e:
                log_error(f"Batch {batch_idx} failed", e)

        en_data = [{
            'case_study': item['case_study_en'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in all_case_studies]
        cn_data = [{
            'case_study': item['case_study_cn'],
            'original_info': item['original_info'],
            'stakeholders': item['stakeholders'],
            'endpoint': item['endpoint']
        } for item in all_case_studies]

        final_dataset = DatasetDict({
            'english': Dataset.from_list(en_data),
            'chinese': Dataset.from_list(cn_data)
        })

        final_save_path = DATA_DIR / "final_dataset"
        final_dataset.save_to_disk(str(final_save_path))
        console.print("[bold green]Successfully completed processing![/]")

        final_dataset.push_to_hub(dataset_name,
                                  private=DATASET_PRIVATE,
                                  token=HF_TOKEN)
        console.print(f"Successfully pushed dataset '{dataset_name}' with "
                      f"{len(final_dataset['english'])} English and "
                      f"{len(final_dataset['chinese'])} Chinese case studies")

        stats = generator.token_tracker.get_stats()
        total_time = time.time() - generator.token_tracker.start_time
        console.print(
            Panel.fit(
                f"[bold cyan]Final Statistics[/]\n\n"
                f"Total Items Processed: {processed_count}/{total_items}\n"  # Now total_items is defined
                f"Total Input Tokens: {stats['total_input_tokens']:.0f}\n"
                f"Total Output Tokens: {stats['total_output_tokens']:.0f}\n"
                f"Average Tokens/minute: {stats['tokens_per_minute']:.1f}\n"
                f"Total Processing Time: {total_time:.1f} seconds"))

    except Exception as e:
        log_error("Fatal error occurred", e)
    finally:
        console.print("[bold]Script execution completed. Total processed: "
                      f"{processed_count}/{total_items}[/]")


if __name__ == "__main__":
    asyncio.run(main())
