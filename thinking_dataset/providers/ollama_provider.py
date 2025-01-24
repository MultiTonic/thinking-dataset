# @file thinking_dataset/providers/ollama_provider.py
# @description Ollama provider class
# @version 1.1.16
# @license MIT

from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed
from .provider import Provider
from .ollama_provider_mock import OllamaProviderMock
from ollama import AsyncClient


class OllamaProvider(Provider):
    """
    Ollama provider class.

    This class:
    1. Initializes the Ollama provider with configuration settings
    2. Provides methods for processing requests asynchronously

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        mock (Optional[bool]): Flag to use mock provider
        model (str): Model name for the provider
        url (str): URL for the provider
        client (Any): Client instance for the provider
    """

    def __init__(self, config: Dict[str, Any], mock: Optional[bool] = False):
        """
        Initialize the Ollama provider with configuration settings.

        Args:
            config (Dict[str, Any]): Configuration dictionary
            mock (Optional[bool]): Flag to use mock provider
        """
        super().__init__(config)
        self.mock = mock

        # Extract model name from nested config
        self.model = self.config.get('config', {}).get('model')
        if not self.model:
            raise ValueError("Model name not found in provider config")
        self.url = self.config.get('url', 'http://localhost:11434')

        if self.mock:
            self.client = OllamaProviderMock(config)
        else:
            self.client = AsyncClient(host=self.url)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def process_request_async(self, prompt: str) -> str:
        """
        Process a request asynchronously and return the response.

        Args:
            prompt (str): The input prompt for the request

        Returns:
            str: The response from the provider
        """
        if self.mock:
            response = await self.client.process_request_async(prompt)
        else:
            response = await self.client.generate(model=self.model,
                                                  prompt=prompt,
                                                  stream=False)
        return response.response
