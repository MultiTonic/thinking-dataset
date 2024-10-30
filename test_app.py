import os
import random
import sys
import logging
import locale
import codecs
import io
import asyncio
import time
import docker
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import Field, BaseModel
import requests
import numpy as np
import warnings
from datasets import Dataset, load_dataset
from dotenv import load_dotenv
from distilabel.llms.base import LLM, AsyncLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import Step, GeneratorStep
from distilabel.steps.tasks import ChatGeneration
from distilabel.steps.typing import StepOutput
from distilabel.steps.base import StepInput
from distilabel.distiset import Distiset
from distilabel.llms import OllamaLLM
import subprocess
import torch
from pydantic import Field, BaseModel



# Load environment variables
load_dotenv()

# Suppress numpy-related warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numpy')

# Version check for numpy
if np.__version__.startswith('2'):
    print("Detected NumPy 2.x. Downgrading to compatible version...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0", "--force-reinstall"])
    print("NumPy downgrade complete. Please restart the application.")
    sys.exit(0)

# Windows-specific encoding setup
if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Logging setup
class UTF8Formatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, bytes):
            record.msg = record.msg.decode('utf-8', errors='replace')
        return super().format(record)

formatter = UTF8Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    force=True
)

# Model schemas
class CableContent(BaseModel):
    cables: str

class PreparedContent(BaseModel):
    prepared_content: str

class Message(BaseModel):
    messages: List[Dict[str, str]]

class ComparisonPrompt(BaseModel):
    comparison_prompt: str

# Prompts
SITREPPROMPT = """You are an AI trained to create business case studies. Create detailed, fictional business case studies using the provided text as inspiration. Do not reference or duplicate the original content directly."""

COMPARISON_PROMPT = """{cable_1}

{cable_2}

{cable_3}

Use the inspiration above to create a fictional case study using free text, detailed, long descriptive form:"""

# Utility functions
def clean_content(text: str) -> str:
    """Clean and normalize text content."""
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^ -~]', '', text)
    return text.strip()

# Container configuration
class ContainerConfig:
    def __init__(
        self,
        model: str,
        container_port: int = 11434,
        host_port: int = 11434,
        environment: Optional[Dict[str, str]] = None,
        command: Optional[str] = None
    ):
        self.image = "ollama/ollama:0.1.44"
        self.model = model
        self.container_port = container_port
        self.host_port = host_port
        self.environment = environment or {}
        self.command = command or "ollama serve"
        
    def get_container_config(self) -> Dict[str, Any]:
        return {
            "image": self.image,
            "ports": {f"{self.container_port}/tcp": self.host_port},
            "environment": self.environment,
            "command": self.command,
            "detach": True,
            "privileged": True,  # Required for some Ollama operations
            "remove": True,      # Automatically remove container when stopped
            "platform": "linux/amd64",  # Ensure consistent platform
            "volumes": {         # Persist Ollama data
                "ollama-data": {"bind": "/root/.ollama", "mode": "rw"}
            }
        }

class OptimizedTestContainerOllamaLLM(OllamaLLM):
    num_instances: int = Field(default=1, description="Number of Ollama instances to run")
    base_port: int = Field(default=11434, description="Base port for Ollama instances")
    container_environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables for containers")
    containers: List[Any] = Field(default_factory=list, description="List of running containers")
    container_configs: List[ContainerConfig] = Field(default_factory=list, description="List of container configurations")
    docker_client: Any = Field(default_factory=lambda: docker.from_env(), description="Docker client instance")

    def __init__(
        self,
        model: str,
        num_instances: int = 1,
        base_port: int = 11434,
        environment: Optional[Dict[str, str]] = None
    ):
        super().__init__(model=model)
        self.num_instances = num_instances
        self.base_port = base_port
        self.container_environment = environment
        
        # Initialize container configs
        self.container_configs = [
            ContainerConfig(
                model=model,
                container_port=11434,
                host_port=base_port + i,
                environment=environment
            )
            for i in range(num_instances)
        ]
        
        # Initialize empty containers list
        self.containers = []

    async def load(self):
        try:
            for i, config in enumerate(self.container_configs, 1):
                logging.info(f"Starting container instance {i}/{self.num_instances}")
                container = self.docker_client.containers.run(**config.get_container_config())
                self.containers.append(container)
                
                await self._wait_for_ollama(f"http://localhost:{config.host_port}")
                await self._pull_model(config.host_port)
                
        except Exception as e:
            logging.error(f"Failed to initialize containers: {e}")
            self.cleanup()
            raise

    async def _wait_for_ollama(self, url: str, timeout: int = 120):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/api/version") as response:
                        if response.status == 200:
                            return
            except Exception:
                await asyncio.sleep(1)
        raise TimeoutError(f"Ollama service not ready after {timeout} seconds")

    async def _pull_model(self, port: int):
        url = f"http://localhost:{port}/api/pull"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"name": self.model}) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to pull model: {response.status}")

    def cleanup(self):
        for container in self.containers:
            try:
                container.stop()
                container.remove()
            except Exception as e:
                logging.error(f"Error cleaning up container: {e}")
        
        # Clean up the Docker client
        try:
            self.docker_client.close()
        except Exception as e:
            logging.error(f"Error closing Docker client: {e}")

# Pipeline steps
class LoadLocalDataset(GeneratorStep):
    file_path: str = Field(description="Path to the local parquet file")
    batch_size: int = Field(default=32, description="Number of items to process in each batch")

    @property
    def inputs(self) -> List[str]:
        return []

    @property
    def outputs(self) -> List[str]:
        return ["cables"]

    def process(self, offset: Optional[int] = None) -> StepOutput:
        dataset = load_dataset("parquet", data_files={"train": self.file_path})["train"]
        start = offset or 0
        end = min(start + self.batch_size, len(dataset))

        while start < len(dataset):
            batch = []
            for i in range(start, end):
                cable_row = dataset[i]
                if "cleaned_content" in cable_row:
                    cable_content = clean_content(cable_row["cleaned_content"])
                    if cable_content:
                        batch.append({"cables": cable_content})

            yield batch, end >= len(dataset)
            start = end
            end = min(start + self.batch_size, len(dataset))

class PrepareContentStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["cables"]

    @property
    def outputs(self) -> List[str]:
        return ["prepared_content"]
    
    def process(self, inputs: StepInput) -> StepOutput:
        prepared_batch = [{"prepared_content": item["cables"]} for item in inputs if "cables" in item]
        if prepared_batch:
            yield prepared_batch
        else:
            logging.warning("No 'prepared_content' generated in PrepareContentStep.")

class PrepareMessagesStep(Step):
    @property
    def inputs(self) -> List[str]:
        return ["comparison_prompt"]

    @property
    def outputs(self) -> List[str]:
        return ["messages"]
    
    def process(self, inputs: StepInput) -> StepOutput:
        output_batch = []
        for item in inputs:
            if "comparison_prompt" in item:
                messages = [
                    {"role": "system", "content": SITREPPROMPT},
                    {"role": "user", "content": item["comparison_prompt"]}
                ]
                output_batch.append({"messages": messages})
        
        if output_batch:
            yield output_batch
        else:
            logging.error("No valid messages generated in PrepareMessagesStep.")

class RandomSampleForComparison(Step):
    num_comparisons: int = Field(default=2000, description="Number of comparisons to generate")
    sample_size: int = Field(default=200, description="Size of the sample to draw from")

    @property
    def inputs(self) -> List[str]:
        return ["prepared_content"]

    @property
    def outputs(self) -> List[str]:
        return ["comparison_prompt"]

    def process(self, inputs: StepInput) -> StepOutput:
        cable_sample = [item for item in inputs if "prepared_content" in item]
        available_comparisons = len(cable_sample) // 3
        total_comparisons = min(self.num_comparisons, available_comparisons)

        if total_comparisons == 0:
            logging.warning("Not enough prepared_content items to generate comparisons.")
            return

        for _ in range(total_comparisons):
            sampled = random.sample(cable_sample, 3)
            comparison_prompt = COMPARISON_PROMPT.format(
                cable_1=sampled[0]["prepared_content"],
                cable_2=sampled[1]["prepared_content"],
                cable_3=sampled[2]["prepared_content"]
            )
            yield [{"comparison_prompt": comparison_prompt}]

# Pipeline creation and execution
def create_pipeline(use_gpu: bool = False):
    with Pipeline(
        name="openai-casestudy-pipeline",
        description="A pipeline to summarize and compare diplomatic cables"
    ) as pipeline:
        load_dataset_step = LoadLocalDataset(
            name="load_cablegate_dataset",
            file_path=os.path.join("scripts", "cables", "cleaned_data.parquet"),
            batch_size=32
        )

        prepare_content_step = PrepareContentStep(
            name="prepare_content"
        )

        sample_for_comparison_step = RandomSampleForComparison(
            name="sample_for_comparison",
            num_comparisons=2000,
            sample_size=200
        )

        prepare_messages_comparison_step = PrepareMessagesStep(
            name="prepare_messages_comparison"
        )

        # Configure environment for GPU if requested
        env = {"CUDA_VISIBLE_DEVICES": "0"} if use_gpu else {}
        
        ollama_llm = OptimizedTestContainerOllamaLLM(
            model="yi:6b-q4_K_M",
            num_instances=4,
            base_port=11434,
            environment=env
        )
        
        # Initialize LLM
        asyncio.run(ollama_llm.load())

        compare_cables_step = ChatGeneration(
            name="compare_cables",
            llm=ollama_llm,
            input_batch_size=32,
            input_mappings={"messages": "messages"},
            output_mappings={"generation": "generation"}
        )

        # Define pipeline flow
        load_dataset_step >> prepare_content_step >> sample_for_comparison_step >> prepare_messages_comparison_step >> compare_cables_step

    return pipeline

def process_dataset(pipeline: Pipeline, parameters: Dict[str, Any]) -> Distiset:
    try:
        return pipeline.run(parameters=parameters, use_cache=False)
    except Exception as e:
        logging.error(f"Error running the pipeline: {e}")
        raise

def test_pipeline_dry_run(use_gpu: bool = False):
    """Test the pipeline using distilabel's dry_run functionality"""
    logging.info("Starting pipeline dry run test...")

    try:
        pipeline = create_pipeline(use_gpu=use_gpu)
        dry_run_params = {
            "load_cablegate_dataset": {
                "file_path": os.path.join("scripts", "cables", "cleaned_data.parquet"),
            },
            "sample_for_comparison": {
                "num_comparisons": 3,
                "sample_size": 3,
            }
        }

        pipeline.dry_run(parameters=dry_run_params)
        logging.info("Dry run completed successfully")
        return True

    except Exception as e:
        logging.error(f"Pipeline dry run failed: {e}")
        return False

if __name__ == "__main__":
    try:
        # Run with GPU if available
        use_gpu = torch.cuda.is_available()
        success = test_pipeline_dry_run(use_gpu=use_gpu)
        
        if success:
            pipeline = create_pipeline(use_gpu=use_gpu)
            comparison_distiset = process_dataset(pipeline, {
                "load_cablegate_dataset": {
                    "batch_size": 32
                },
                "sample_for_comparison": {
                    "num_comparisons": 2000,
                    "sample_size": 200
                }
            })
            
            # Process results
            compare_cables_output = comparison_distiset.get("compare_cables", {})
            generation_data = compare_cables_output.get("generation", [])

            if isinstance(generation_data, list) and generation_data:
                dataset_dict = {}
                for entry in generation_data:
                    for key, value in entry.items():
                        dataset_dict.setdefault(key, []).append(value)
                
                comparison_dataset = Dataset.from_dict(dataset_dict)
                
                if len(comparison_dataset) > 0:
                    try:
                        comparison_dataset.push_to_hub(
                            "DataTonic/BusinessCaseStudies",
                            private=True,
                            token=os.getenv("HUGGINGFACE_TOKEN")
                        )
                        logging.info("Dataset successfully pushed to the Hub")
                    except Exception as e:
                        logging.error(f"Failed to push dataset to the Hub: {e}")
                else:
                    logging.warning("Comparison dataset is empty")
        else:
            logging.error("Pipeline dry run validation failed")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure proper cleanup
        logging.shutdown()