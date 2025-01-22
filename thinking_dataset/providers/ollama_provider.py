# @file thinking_dataset/providers/ollama_provider.py
# @description Ollama provider class
# @version 1.1.13
# @license MIT

import ollama
from typing import Dict, Any
from .provider import Provider
from tenacity import retry, wait_fixed, stop_after_attempt


class OllamaProvider(Provider):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = self.config.get("url")
        self.model = self.config.get("model")
        self.options = self.config.get("options", {})
        self.client = ollama.AsyncClient()

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def process_request_async(self, prompt: str) -> str:
        response = await self.client.generate(model=self.model,
                                              prompt=prompt,
                                              options=self.options)
        return response['response']
