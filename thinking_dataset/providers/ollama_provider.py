# @file ollama_provider.py
# @description Ollama provider class
# @version 1.1.0
# @license MIT

from typing import Dict, Any
from .provider import Provider
import asyncio
import ollama
from tenacity import retry, wait_fixed, stop_after_attempt
from thinking_dataset.dto.generate_cable_dto import GenerateCableSchema


class OllamaProvider(Provider):

    def __init__(self, config: Dict[str, Any]):
        self.url = config.get("url")
        self.model = config.get("model")
        self.format = config.get("format")
        self.options = config.get("options", {})

    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'OllamaProvider':
        return cls(config)

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def process_async_request(self, prompt: str) -> Any:
        client = ollama.AsyncClient()
        response = await client.generate(model=self.model,
                                         prompt=prompt,
                                         format=self.format,
                                         options=self.options)

        validated_response = GenerateCableSchema.model_validate_json(
            response['response'])
        return validated_response

    def run(self, prompt: str) -> Any:
        return asyncio.run(self.process_async_request(prompt))
