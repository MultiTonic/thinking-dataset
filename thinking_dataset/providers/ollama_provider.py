# @file thinking_dataset/providers/ollama_provider.py
# @description Ollama provider class
# @version 1.1.14
# @license MIT

from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed
from .provider import Provider


class OllamaProvider(Provider):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Extract model name from nested config
        self.model = self.config.get('config', {}).get('model')
        if not self.model:
            raise ValueError("Model name not found in provider config")
        self.url = self.config.get('url', 'http://localhost:11434')
        self.client = None
        self._setup_client()

    def _setup_client(self):
        from ollama import AsyncClient
        self.client = AsyncClient(host=self.url)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def process_request_async(self, prompt: str) -> str:
        if not self.client:
            self._setup_client()
        response = await self.client.generate(model=self.model,
                                              prompt=prompt,
                                              stream=False)
        return response.response
