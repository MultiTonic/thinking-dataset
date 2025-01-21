# @file thinking_dataset/providers/ollama_provider.py
# @description Ollama provider class
# @version 1.1.5
# @license MIT

import ollama
from typing import Dict, Any, Callable
from .provider import Provider
from tenacity import retry, wait_fixed, stop_after_attempt


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
    async def process_request_async(self, prompt: str,
                                    validator: Callable[[str], Any]) -> Any:
        client = ollama.AsyncClient()
        response = await client.generate(model=self.model,
                                         prompt=prompt,
                                         format=self.format,
                                         options=self.options)

        response = validator(response['response'])
        return response
