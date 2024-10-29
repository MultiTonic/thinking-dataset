import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Sequence, Union
import io
import requests
from pydantic import Field, BaseModel, PrivateAttr
from testcontainers.ollama import OllamaContainer
from typing_extensions import TypedDict

from distilabel.llms.base import AsyncLLM
from distilabel.llms.typing import GenerateOutput
from distilabel.mixins.runtime_parameters import RuntimeParameter

from distilabel.steps.tasks.typing import InstructorStructuredOutputType, StandardInput
import os
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Sequence, Union
import io
import asyncio
import concurrent.futures
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import requests
from pydantic import Field, BaseModel, PrivateAttr
from testcontainers.ollama import OllamaContainer
from typing_extensions import TypedDict

import torch


@dataclass
class ContainerConfig:
    model_name: str
    quantization: str
    gpu_id: int
    num_ctx: int = 8192
    num_batch: int = 512
    num_gpu: int = 1
    num_thread: int = 8

class OptimizedTestContainerOllamaLLM(AsyncLLM):
    """
    Optimized TestContainers Ollama implementation for RunPod with multi-GPU support.
    """
    model: str
    num_containers: int = Field(default=4, description="Number of parallel containers")
    container_configs: List[ContainerConfig] = Field(
        default_factory=list,
        description="Configuration for each container"
    )
    batch_size: int = Field(default=32, description="Batch size for processing")
    
    _containers: List[OllamaContainer] = PrivateAttr(default_factory=list)
    _endpoints: List[str] = PrivateAttr(default_factory=list)
    _current_container: int = PrivateAttr(default=0)
    _lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    async def load(self) -> None:
        """Initialize multiple Ollama containers with optimized settings."""
        super().load()
        
        # Detect available GPUs
        num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 1
        
        # Default container configurations for Yi model with different quantizations
        if not self.container_configs:
            self.container_configs = [
                ContainerConfig(
                    model_name="yi:6b-q4_K_M",  # Q4_K_M quantization
                    quantization="q4_k_m",
                    gpu_id=i % num_gpus
                ) for i in range(self.num_containers)
            ]

        try:
            for config in self.container_configs:
                container = OllamaContainer(
                    ollama_home=Path.home() / f".ollama_{config.gpu_id}",
                    environment={
                        "CUDA_VISIBLE_DEVICES": str(config.gpu_id),
                        "NUM_THREADS": str(config.num_thread)
                    }
                )
                
                # Start container with optimized settings
                container.with_env("OLLAMA_MODEL", config.model_name)
                container.with_env("OLLAMA_NUM_CTX", str(config.num_ctx))
                container.with_env("OLLAMA_NUM_BATCH", str(config.num_batch))
                container.with_env("OLLAMA_NUM_GPU", str(config.num_gpu))
                container.start()
                
                self._containers.append(container)
                self._endpoints.append(container.get_endpoint())
                
                # Pull model with specific quantization
                await self._pull_model(container, config)
                
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize Ollama containers: {e}")

    async def _pull_model(self, container: OllamaContainer, config: ContainerConfig):
        """Pull the model with specific quantization settings."""
        try:
            response = requests.post(
                f"{container.get_endpoint()}/api/pull",
                json={
                    "name": config.model_name,
                    "insecure": True,
                    "stream": False
                }
            )
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to pull model {config.model_name}: {e}")

    async def agenerate(
        self,
        input: StandardInput,
        format: str = "",
        options: Union[Options, None] = None,
        keep_alive: Union[bool, None] = None,
    ) -> GenerateOutput:
        """
        Generates responses asynchronously using multiple containers.
        """
        async with self._lock:
            container_idx = self._current_container
            self._current_container = (self._current_container + 1) % len(self._containers)

        if not self._endpoints:
            raise RuntimeError("Containers not initialized. Call load() first.")

        try:
            endpoint = self._endpoints[container_idx]
            response = requests.post(
                f"{endpoint}/api/chat",
                json={
                    "model": self.container_configs[container_idx].model_name,
                    "messages": input,
                    "stream": False,
                    "format": format,
                    "options": {
                        **(options or {}),
                        "num_ctx": self.container_configs[container_idx].num_ctx,
                        "num_batch": self.container_configs[container_idx].num_batch,
                        "num_thread": self.container_configs[container_idx].num_thread,
                    },
                    "keep_alive": keep_alive
                }
            )
            response.raise_for_status()
            result = response.json()
            return [result["message"]["content"]]
        except Exception as e:
            self._logger.warning(
                f"⚠️ Error using Ollama client (container {container_idx}): {e}"
            )
            return [""]

    async def cleanup(self):
        """Cleanup all containers."""
        for container in self._containers:
            try:
                container.stop()
            except Exception as e:
                self._logger.warning(f"Failed to stop container: {e}")

    def __del__(self):
        """Ensure cleanup on deletion."""
        asyncio.run(self.cleanup())

class BatchProcessor:
    """Handles batch processing across multiple containers."""
    def __init__(self, llm: OptimizedTestContainerOllamaLLM, batch_size: int = 32):
        self.llm = llm
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=llm.num_containers)

    async def process_batch(self, inputs: List[StandardInput]) -> List[str]:
        """Process a batch of inputs concurrently."""
        tasks = []
        for i in range(0, len(inputs), self.batch_size):
            batch = inputs[i:i + self.batch_size]
            tasks.append(self.llm.agenerate(batch))
        
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]


# class Options(TypedDict, total=False):
#     numa: bool
#     num_ctx: int
#     num_batch: int
#     num_gqa: int
#     num_gpu: int
#     main_gpu: int
#     low_vram: bool
#     f16_kv: bool
#     logits_all: bool
#     vocab_only: bool
#     use_mmap: bool
#     use_mlock: bool
#     embedding_only: bool
#     rope_frequency_base: float
#     rope_frequency_scale: float
#     num_thread: int
#     num_keep: int
#     seed: int
#     num_predict: int
#     top_k: int
#     top_p: float
#     tfs_z: float
#     typical_p: float
#     repeat_last_n: int
#     temperature: float
#     repeat_penalty: float
#     presence_penalty: float
#     frequency_penalty: float
#     mirostat: int
#     mirostat_tau: float
#     mirostat_eta: float
#     penalize_newline: bool
#     stop: Sequence[str]

# class TestContainerOllamaLLM(AsyncLLM):
#     """
#     TestContainers Ollama implementation that follows the Distilabel AsyncLLM interface.
#     """
#     model: str
#     host: Optional[RuntimeParameter[str]] = Field(
#         default=None, description="The host of the Ollama API."
#     )
#     timeout: RuntimeParameter[int] = Field(
#         default=120, description="The timeout for the Ollama API."
#     )
#     follow_redirects: bool = True
#     structured_output: Optional[RuntimeParameter[InstructorStructuredOutputType]] = Field(
#         default=None,
#         description="The structured output format to use across all the generations.",
#     )

#     _num_generations_param_supported = False
#     _container: Optional[OllamaContainer] = PrivateAttr(default=None)
#     _endpoint: Optional[str] = PrivateAttr(default=None)

#     def load(self) -> None:
#         """Initialize the Ollama container and setup the endpoint."""
#         super().load()
        
#         try:
#             ollama_home = Path.home() / ".ollama"
#             self._container = OllamaContainer(ollama_home=ollama_home)
#             self._container.start()
            
#             # Store the endpoint
#             self._endpoint = self._container.get_endpoint()
            
#             # Check if model exists and pull if necessary
#             models = self._container.list_models()
#             if self.model not in [model["name"] for model in models]:
#                 self._container.pull_model(self.model)
                
#         except Exception as e:
#             raise RuntimeError(f"Failed to initialize Ollama container: {e}")

#     @property
#     def model_name(self) -> str:
#         """Returns the model name used for the LLM."""
#         return self.model

#     async def agenerate(
#         self,
#         input: StandardInput,
#         format: str = "",
#         options: Union[Options, None] = None,
#         keep_alive: Union[bool, None] = None,
#     ) -> GenerateOutput:
#         """
#         Generates a response asynchronously using the TestContainers Ollama implementation.

#         Args:
#             input: the input to use for the generation.
#             format: the format to use for the generation.
#             options: the options to use for the generation.
#             keep_alive: whether to keep the connection alive.

#         Returns:
#             A list of strings as completion for the given input.
#         """
#         if not self._endpoint:
#             raise RuntimeError("Container not initialized. Call load() first.")

#         try:
#             response = requests.post(
#                 f"{self._endpoint}/api/chat",
#                 json={
#                     "model": self.model,
#                     "messages": input,
#                     "stream": False,
#                     "format": format,
#                     "options": options,
#                     "keep_alive": keep_alive
#                 }
#             )
#             response.raise_for_status()
#             result = response.json()
#             return [result["message"]["content"]]
#         except Exception as e:
#             self._logger.warning(
#                 f"⚠️ Error using Ollama client (model: '{self.model_name}'): {e}"
#             )
#             return [""]

#     def __del__(self):
#         """Cleanup the container on deletion."""
#         if self._container:
#             try:
#                 self._container.stop()
#             except Exception as e:
#                 logging.warning(f"Failed to stop Ollama container: {e}")