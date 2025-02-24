# Standard library imports
import os
import re
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Third-party imports
from datasets import load_dataset, Dataset
from huggingface_hub import login
from ollama import AsyncClient

# Configuration and constants
BASE_DIR = Path(os.getcwd())
DATA_DIR = BASE_DIR / "data" / "case_studies"
TEMP_DIR = BASE_DIR / "data" / "temp"
LOG_DIR = BASE_DIR / "logs"
HF_TOKEN = "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"

# Initialize directories and logging
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_DIR / 'case_studies.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Authentication
login(token=HF_TOKEN)

# Endpoint configuration
RUNPOD_ENDPOINTS = [
    ("http://localhost:11434", "en"),
]


class RunPodEndpoint:
    """Base class for managing individual endpoints."""

    def __init__(self, endpoint: str, language: str):
        self.endpoint = endpoint
        self.language = language
        self.client = AsyncClient(host=f"{endpoint}")
        self.is_active = True

    def __str__(self):
        return (f"RunPodEndpoint(endpoint={self.endpoint}, "
                f"language={self.language})")


class RunPodClientManager:
    """Manages multiple RunPod endpoints for a specific language."""

    def __init__(self, endpoints: List[tuple[str, str]], target_language: str):
        self.endpoints = [
            RunPodEndpoint(endpoint, lang) for endpoint, lang in endpoints
            if lang == target_language
        ]
        self.current_idx = 0

    # Endpoint management
    def get_next_endpoint(self) -> RunPodEndpoint:
        """Get next available endpoint using round-robin with health check."""
        for _ in range(len(self.endpoints)):
            endpoint = self.endpoints[self.current_idx]
            if endpoint.is_active:
                self.current_idx = (self.current_idx + 1) % len(self.endpoints)
                return endpoint
            self.current_idx = (self.current_idx + 1) % len(self.endpoints)
        raise RuntimeError("No active endpoints available")

    async def test_connections(self) -> bool:
        """Test connection to all endpoints."""
        tasks = [self.test_endpoint(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks)

        if any(results):
            logger.info("Sufficient endpoints available")
            return True
        logger.error("No active endpoints")
        return False


class CaseStudyGenerator:
    """Handles the generation of case studies using RunPod endpoints."""

    def __init__(self,
                 language: str,
                 model_name: str = "deepseek-r1:8b",
                 batch_size: int = 10,
                 save_interval: int = 10,
                 temperature: float = 1):
        # Initialize configuration
        self.language = language
        self.model_name = model_name
        self.batch_size = batch_size
        self.save_interval = save_interval
        self.temperature = temperature
        self.client_manager = RunPodClientManager(RUNPOD_ENDPOINTS, language)
        self.response_counter = 0

        # Templates
        self._init_templates()

    def _init_templates(self):
        """Initialize prompt templates."""
        self.prompt_template_en = """
        {case_study_info}
        Stakeholder: {stakeholder} {motivation}
        """
        self.prompt_template_cn = """{case_study_info}
        利益相关者: {stakeholder} {motivation}
        """
        self.fallback_prompt_en = """{case_study_info}"""
        self.fallback_prompt_cn = """{case_study_info}"""

    # Text processing methods
    def clean_text(self, text: str) -> str:
        """Clean and prepare text content."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def prepare_prompts(self, row: Dict[str, Any]) -> List[str]:
        """Prepare prompts for each stakeholder."""
        try:
            # Extract data
            case_study_info = row.get('case_study_info', '')
            stakeholders = row.get('stakeholders', {})
            stakeholder_list = stakeholders.get('stakeholder', [])
            motivation_list = stakeholders.get('motivation', [])

            # Select templates
            template = (self.prompt_template_en
                        if self.language == 'en' else self.prompt_template_cn)
            fallback = (self.fallback_prompt_en
                        if self.language == 'en' else self.fallback_prompt_cn)

            # Generate prompts
            if (stakeholder_list and motivation_list
                    and len(stakeholder_list) == len(motivation_list)):
                return [
                    template.format(case_study_info=case_study_info,
                                    stakeholder=s,
                                    motivation=m)
                    for s, m in zip(stakeholder_list, motivation_list)
                ]
            return [fallback.format(case_study_info=case_study_info)]
        except Exception as e:
            logger.error(f"Error preparing prompts: {str(e)}")
            return ['']

    # Generation methods
    async def generate_case_study(self, prompt: str) -> str:
        """Generate a case study section with retries across endpoints."""
        max_attempts = 4
        attempt = 0

        while attempt < max_attempts:
            try:
                if not prompt:
                    raise ValueError("Empty prompt")

                endpoint = self.client_manager.get_next_endpoint()
                logger.info(
                    f"Using endpoint {endpoint.endpoint} for generation")

                response = await endpoint.client.chat(model=self.model_name,
                                                      messages=[{
                                                          "role":
                                                          "user",
                                                          "content":
                                                          prompt
                                                      }],
                                                      options={
                                                          "temperature":
                                                          self.temperature,
                                                          "top_p": 0.95,
                                                      })

                return response['message']['content'].strip()

            except Exception as e:
                logger.warning(
                    f"Error on attempt {attempt + 1}/{max_attempts}: {str(e)}")
                attempt += 1
                await asyncio.sleep(1)

        logger.error(
            f"Failed to generate case study after {max_attempts} attempts")
        return ""

    def save_response(self, response: str, metadata: Dict[str, Any]) -> Path:
        """Save individual response to temp directory with sequential naming."""
        filename = f"{self.response_counter:06d}_{self.language}.txt"
        filepath = TEMP_DIR / filename

        # Save response with metadata
        content = (f"Original Info: {metadata.get('original_info', '')}\n"
                   f"Stakeholder: {metadata.get('stakeholder', '')}\n"
                   f"Motivation: {metadata.get('motivation', '')}\n"
                   f"Response:\n{response}\n")

        filepath.write_text(content, encoding='utf-8')
        self.response_counter += 1
        return filepath

    async def process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single row, generating case studies."""
        prompts = self.prepare_prompts(row)
        outputs = []
        saved_paths = []

        for prompt in prompts:
            result = await self.generate_case_study(prompt)
            if result:
                outputs.append(result)
                # Save individual response with metadata
                metadata = {
                    'original_info':
                    row.get('case_study_info', ''),
                    'stakeholder':
                    row.get('stakeholders', {}).get('stakeholder', [''])[0],
                    'motivation':
                    row.get('stakeholders', {}).get('motivation', [''])[0]
                }
                saved_path = self.save_response(result, metadata)
                saved_paths.append(saved_path)
                logger.info(f"Saved individual response to {saved_path}")

        return {
            'case_study': outputs,
            'original_info': row.get('case_study_info', ''),
            'stakeholders': row.get('stakeholders', {}),
            'endpoint': 'runpod',
            'temp_files': saved_paths
        }

    async def process_batch(
            self, batch: List[Dict[str, Any]]) -> List[Dict[str, List[str]]]:
        """Process a batch of rows in parallel."""
        tasks = [self.process_row(row) for row in batch]
        return await asyncio.gather(*tasks)


async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Generate case studies for a specific language')
    parser.add_argument('--language',
                        type=str,
                        choices=['en', 'cn'],
                        required=True,
                        help='Language to generate case studies for (en/cn)')
    args = parser.parse_args()

    try:
        # Initialize
        logger.info(f"Starting case study generation for {args.language}")
        dataset = load_dataset("DataTonic/dark_thoughts_stakeholders_80",
                               split="english")
        total_items = len(dataset)
        logger.info(f"Loaded {total_items} items from dataset")

        # Setup generator
        generator = CaseStudyGenerator(language=args.language,
                                       model_name="deepseek-r1:8b",
                                       batch_size=10,
                                       save_interval=10,
                                       temperature=1)

        # Validate connections
        if not await generator.client_manager.test_connections():
            raise RuntimeError("No active endpoints available")

        # Process data
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
                interim_dataset = Dataset.from_list(all_case_studies)
                save_path = (DATA_DIR /
                             f"interim_batch_{args.language}_{batch_idx}")
                interim_dataset.save_to_disk(str(save_path))
                logger.info(f"Saved interim results to {save_path} - "
                            f"Processed {processed_count}/{total_items}")

        final_dataset = Dataset.from_list(all_case_studies)
        final_save_path = DATA_DIR / f"final_dataset_{args.language}"
        final_dataset.save_to_disk(str(final_save_path))
        logger.info(f"Saved final dataset to {final_save_path}")

        hub_name = f"runpod_yi34b_dark_thoughts_casestudies_{args.language}"
        final_dataset.push_to_hub(hub_name, private=True, token=HF_TOKEN)
        logger.info(f"Successfully pushed dataset with {len(final_dataset)} "
                    "case studies to Hugging Face Hub")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        logger.info(f"Script execution completed. "
                    f"Total processed: {processed_count}/{total_items}")


if __name__ == "__main__":
    asyncio.run(main())
