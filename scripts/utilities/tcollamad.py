# scripts\utilities\tcollamad.py

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import requests
from pydantic import Field, BaseModel, PrivateAttr
from testcontainers.ollama import OllamaContainer
from typing_extensions import TypedDict
from dataclasses import dataclass
import torch
from distilabel.llms.base import LLM, AsyncLLM


@dataclass
class ContainerConfig:
    """Configuration for each Ollama container instance"""
    port: int  # Unique port for each container
    gpu_id: int
    num_ctx: int = 8192
    num_batch: int = 512
    num_thread: int = 4
    model_name: str = "yi:6b-q4_K_M"  # Using same quantized model for all instances

class OptimizedTestContainerOllamaLLM(AsyncLLM):
    """
    Optimized TestContainers Ollama implementation for running multiple instances
    of the same quantized model on a single GPU.
    """
    model: str = Field(default="yi:6b-q4_K_M")
    num_instances: int = Field(default=4, description="Number of model instances")
    base_port: int = Field(default=11434, description="Base port for containers")
    
    _containers: List[OllamaContainer] = PrivateAttr(default_factory=list)
    _endpoints: List[str] = PrivateAttr(default_factory=list)
    _current_instance: int = PrivateAttr(default=0)
    _lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)
    _logger: logging.Logger = PrivateAttr()


    @property
    def model_name(self) -> str:
        """
        Implementation of the abstract model_name property required by AsyncLLM
        Returns the model name being used by this LLM instance
        """
        return self.model

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.INFO)

    def _create_container_configs(self) -> List[ContainerConfig]:
        """Create configurations for each container instance"""
        configs = []
        gpu_memory = torch.cuda.get_device_properties(0).total_memory
        memory_per_instance = gpu_memory // self.num_instances
        
        for i in range(self.num_instances):
            configs.append(ContainerConfig(
                port=self.base_port + i,
                gpu_id=0,  # Same GPU for all instances
                num_ctx=8192,
                num_batch=512,
                num_thread=4,
                model_name=self.model
            ))
        return configs

    async def load(self) -> None:
        """Initialize multiple instances of the same quantized model"""
        super().load()
        
        configs = self._create_container_configs()
        
        try:
            for i, config in enumerate(configs):
                self._logger.info(f"Starting container instance {i+1}/{self.num_instances}")
                
                container = OllamaContainer(
                    ollama_home=Path.home() / f".ollama_instance_{i}",
                    environment={
                        "CUDA_VISIBLE_DEVICES": "0",
                        "OLLAMA_HOST": f"0.0.0.0:{config.port}",
                        "OLLAMA_MODELS": str(Path.home() / f".ollama_instance_{i}/models")
                    }
                )
                
                # Configure container
                container.with_exposed_ports(config.port)
                container.start()
                
                endpoint = f"http://localhost:{container.get_exposed_port(config.port)}"
                self._containers.append(container)
                self._endpoints.append(endpoint)
                
                # Pull model for this instance
                await self._pull_model(container, config)
                
                self._logger.info(f"Container instance {i+1} initialized at {endpoint}")
                
        except Exception as e:
            self._logger.error(f"Failed to initialize containers: {e}")
            await self.cleanup()
            raise RuntimeError(f"Container initialization failed: {e}")

    async def _pull_model(self, container: OllamaContainer, config: ContainerConfig):
        """Pull the quantized model for each instance"""
        try:
            response = requests.post(
                f"{container.get_endpoint()}/api/pull",
                json={
                    "name": config.model_name,
                    "insecure": True,
                    "stream": False
                },
                timeout=600  # Increased timeout for model pulling
            )
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to pull model {config.model_name}: {e}")

    async def agenerate(
        self,
        input: Any,
        format: str = "",
        options: Optional[Dict[str, Any]] = None,
        keep_alive: Optional[bool] = None,
    ) -> List[str]:
        """Generate response using round-robin instance selection"""
        async with self._lock:
            instance_idx = self._current_instance
            self._current_instance = (self._current_instance + 1) % len(self._containers)

        if not self._endpoints:
            raise RuntimeError("Containers not initialized")

        try:
            endpoint = self._endpoints[instance_idx]
            response = requests.post(
                f"{endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": input,
                    "options": {
                        "num_ctx": 8192,
                        "num_batch": 512,
                        "temperature": 0.7,
                        **(options or {})
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return [result["response"]]
        except Exception as e:
            self._logger.error(f"Generation error (instance {instance_idx}): {e}")
            return [""]

    async def cleanup(self):
        """Cleanup all container instances"""
        for i, container in enumerate(self._containers):
            try:
                self._logger.info(f"Stopping container instance {i+1}")
                container.stop()
            except Exception as e:
                self._logger.error(f"Failed to stop container {i+1}: {e}")

    def __del__(self):
        """Ensure cleanup on deletion"""
        asyncio.run(self.cleanup())