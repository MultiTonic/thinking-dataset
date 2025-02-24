# flake8: noqa
import asyncio
import os
from datasets import load_dataset, DatasetDict, Dataset
from typing import List, Dict, Any
import logging
from pathlib import Path
from huggingface_hub import login
from ollama import AsyncClient
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

# Create base directories
BASE_DIR = Path(os.getcwd())
DATA_DIR = BASE_DIR / "data" / "case_studies"
LOG_DIR = BASE_DIR / "logs"

# Create necessary directories with parents
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Update logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_DIR / 'case_studies.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Hugging Face authentication
HF_TOKEN = "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"
login(token=HF_TOKEN)

# RunPod endpoints: 4 per language (replace with actual endpoints)
RUNPOD_ENDPOINTS = [
    # English endpoints
    # ("https://endpoint-en-1.runpod.net", "en"),
    # ("https://endpoint-en-2.runpod.net", "en"),
    # ("https://endpoint-en-3.runpod.net", "en"),
    # ("https://endpoint-en-4.runpod.net", "en"),
    ("http://localhost:11434", "en"),  # dev
    # Chinese endpoints
    # ("https://endpoint-cn-1.runpod.net", "cn"),
    # ("https://endpoint-cn-2.runpod.net", "cn"),
    # ("https://endpoint-cn-3.runpod.net", "cn"),
    # ("https://endpoint-cn-4.runpod.net", "cn"),
    ("http://localhost:11434", "cn"),  # dev
]


class RunPodEndpoint:

    def __init__(self, endpoint: str, language: str):
        self.endpoint = endpoint
        self.language = language
        self.client = AsyncClient(host=f"{endpoint}")
        self.is_active = True
        self.last_used = 0

    def __str__(self):
        return f"RunPodEndpoint(endpoint={self.endpoint}, language={self.language})"


class RunPodClientManager:

    def __init__(self, endpoints: List[tuple[str, str]]):
        self.endpoints = [
            RunPodEndpoint(endpoint, lang) for endpoint, lang in endpoints
        ]
        self.en_endpoints = [
            ep for ep in self.endpoints if ep.language == 'en'
        ]
        self.cn_endpoints = [
            ep for ep in self.endpoints if ep.language == 'cn'
        ]
        self.current_en_idx = 0
        self.current_cn_idx = 0

    def get_next_endpoint(self, language: str) -> RunPodEndpoint:
        """Get next available endpoint using round-robin with health check."""
        endpoints = self.en_endpoints if language == 'en' else self.cn_endpoints
        current_idx = self.current_en_idx if language == 'en' else self.current_cn_idx

        for _ in range(len(endpoints)):
            endpoint = endpoints[current_idx]
            if endpoint.is_active:
                if language == 'en':
                    self.current_en_idx = (current_idx + 1) % len(
                        self.en_endpoints)
                else:
                    self.current_cn_idx = (current_idx + 1) % len(
                        self.cn_endpoints)
                return endpoint
            current_idx = (current_idx + 1) % len(endpoints)

        raise RuntimeError(
            f"No active endpoints available for language: {language}")

    async def test_endpoint(self, endpoint: RunPodEndpoint) -> bool:
        """Test single endpoint connection."""
        try:
            message = {'role': 'user', 'content': 'Test connection'}
            await endpoint.client.chat(
                model=
                "p3nGu1nZz/tonic-casestudy-en-8b",  # Adjust model name as needed
                messages=[message])
            return True
        except Exception as e:
            logger.error(f"Endpoint {endpoint} test failed: {str(e)}")
            endpoint.is_active = False
            return False

    async def test_connections(self) -> bool:
        """Test connection to all endpoints."""
        tasks = [self.test_endpoint(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks)

        active_en = any(ep.is_active for ep in self.en_endpoints)
        active_cn = any(ep.is_active for ep in self.cn_endpoints)

        if active_en and active_cn:
            logger.info("Sufficient endpoints available for both languages")
            return True
        else:
            logger.error("Insufficient active endpoints")
            return False


class CaseStudyGenerator:

    def __init__(
            self,
            model_name:
        str = "p3nGu1nZz/tonic-casestudy-en-8b",  # Adjust model name as needed
            batch_size: int = 1,
            save_interval: int = 10,
            temperature: float = 1,
            max_tokens: int = 16384):
        self.model_name = model_name
        self.batch_size = batch_size
        self.save_interval = save_interval
        self.client_manager = RunPodClientManager(RUNPOD_ENDPOINTS)
        self.temperature = temperature
        self.max_tokens = max_tokens

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

    def clean_text(self, text: str) -> str:
        """Clean and prepare text content, preserving UTF-8 for Chinese."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def prepare_prompts(self, row: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare prompts for each stakeholder or fallback if no stakeholders."""
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
                        self.prompt_template_en.format(
                            case_study_info=case_study_info,
                            stakeholder=stakeholder,
                            motivation=motivation),
                        'cn':
                        self.prompt_template_cn.format(
                            case_study_info=case_study_info,
                            stakeholder=stakeholder,
                            motivation=motivation)
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

    async def generate_case_study(self, prompt: Dict[str, str],
                                  language: str) -> str:
        """Generate a case study section with retries across endpoints."""
        max_attempts = 4  # Number of endpoints per language
        attempt = 0

        while attempt < max_attempts:
            try:
                prompt_text = prompt['en'] if language == 'en' else prompt['cn']
                if not prompt_text:
                    raise ValueError(f"Empty prompt for {language}")

                endpoint = self.client_manager.get_next_endpoint(language)
                logger.info(
                    f"Using endpoint {endpoint.endpoint} for {language} generation"
                )

                response = await endpoint.client.chat(
                    model=self.model_name,
                    messages=[{
                        "role": "user",
                        "content": prompt_text
                    }],
                    options={
                        "temperature": self.temperature,
                        #"max_tokens":
                        #self.max_tokens,
                        "top_p": 0.95,
                        #"presence_penalty": 0
                    })

                return response['message']['content'].strip()

            except Exception as e:
                logger.warning(
                    f"Error on attempt {attempt + 1}/{max_attempts} for {language}: {str(e)}"
                )
                attempt += 1
                await asyncio.sleep(1)  # Brief delay before retry
        logger.error(
            f"Failed to generate {language} case study after {max_attempts} attempts"
        )
        return ""

    async def process_row(self, row: Dict[str, Any]) -> Dict[str, List[str]]:
        """Process a single row, generating case studies for all prompts."""
        prompts = self.prepare_prompts(row)
        en_outputs = []
        cn_outputs = []

        for prompt in prompts:
            en_task = self.generate_case_study(prompt, 'en')
            cn_task = self.generate_case_study(prompt, 'cn')
            en_result, cn_result = await asyncio.gather(en_task, cn_task)
            if en_result:
                en_outputs.append(en_result)
            if cn_result:
                cn_outputs.append(cn_result)

        return {
            'case_study_en': en_outputs,
            'case_study_cn': cn_outputs,
            'original_info': row.get('case_study_info', ''),
            'stakeholders': row.get('stakeholders', {}),
            'endpoint': 'runpod'
        }

    async def process_batch(
            self, batch: List[Dict[str, Any]]) -> List[Dict[str, List[str]]]:
        """Process a batch of rows in parallel."""
        tasks = [self.process_row(row) for row in batch]
        return await asyncio.gather(*tasks)


async def main():
    try:
        logger.info(
            "Starting enhanced case study generation process with RunPod...")

        dataset = load_dataset("DataTonic/dark_thoughts_stakeholders_80",
                               split="english")
        total_items = len(dataset)
        logger.info(f"Loaded {total_items} items from dataset")

        generator = CaseStudyGenerator(
            model_name=
            "p3nGu1nZz/tonic-casestudy-en-8b",  # Adjust model name as needed
            batch_size=1,
            save_interval=10,
            temperature=1,
            max_tokens=16384)

        # Test connections
        if not await generator.client_manager.test_connections():
            raise RuntimeError("Insufficient active endpoints to proceed")

        content_items = [dict(row) for row in dataset]
        batches = [
            content_items[i:i + generator.batch_size]
            for i in range(0, len(content_items), generator.batch_size)
        ]

        all_case_studies = []
        processed_count = 0

        for batch_idx, batch in enumerate(batches):
            logger.info(f"Processing batch {batch_idx + 1}/{len(batches)}")
            case_study_batch = await generator.process_batch(batch)
            all_case_studies.extend(case_study_batch)
            processed_count += len(case_study_batch)

            if len(all_case_studies) >= generator.save_interval:
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

                interim_dataset = DatasetDict({
                    'english':
                    Dataset.from_list(en_data),
                    'chinese':
                    Dataset.from_list(cn_data)
                })
                save_path = DATA_DIR / f"interim_batch_{batch_idx}"
                interim_dataset.save_to_disk(str(save_path))
                logger.info(
                    f"Saved interim results to {save_path} - Processed {processed_count}/{total_items}"
                )

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
        logger.info(f"Saved final dataset to {final_save_path}")

        final_dataset.push_to_hub("runpod_yi34b_dark_thoughts_casestudies",
                                  private=True,
                                  token=HF_TOKEN)
        logger.info(
            f"Successfully pushed dataset with {len(final_dataset['english'])} English and {len(final_dataset['chinese'])} Chinese case studies to Hugging Face Hub"
        )

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        logger.info(
            f"Script execution completed. Total processed: {processed_count}/{total_items}"
        )


if __name__ == "__main__":
    asyncio.run(main())
