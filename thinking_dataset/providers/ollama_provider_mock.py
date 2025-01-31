# @file thinking_dataset/providers/ollama_provider_mock.py
# @description Mock provider class for testing response generation.
# @version 1.1.16
# @license MIT

import asyncio
from typing import Dict, Any, Optional
from .provider import Provider
from thinking_dataset.utils.text_utils import TextUtils
from thinking_dataset.utils.log import Log
from thinking_dataset.dto.mock_response import MockResponse


class OllamaProviderMock(Provider):
    """
    Mock provider that returns a single predefined response for testing.

    This class:
    1. Generates a mock response with XML formatted content
    2. Returns the mock response without making actual API calls

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        char_limit (Optional[int]): Optional character limit for the response
        response (str): The generated mock response
    """

    def __init__(self,
                 config: Dict[str, Any],
                 char_limit: Optional[int] = None):
        """
        Initialize the mock provider with configuration settings.

        Args:
            config (Dict[str, Any]): Configuration dictionary
            char_limit (Optional[int]): Optional char limit for the response
        """
        super().__init__(config)
        self.char_limit = char_limit
        self.response = self._generate_mock_response()
        self.render_time = 3  # seconds to simulate rendering

    def _generate_mock_response(self) -> str:
        """
        Generate a mock response with XML formatted content.

        Returns:
            str: The generated mock response.
        """
        output_text = TextUtils.generate_lorem_ipsum(
            paragraphs=5, char_limit=self.char_limit)

        response = f"""
        <output>
        {output_text}
        </output>
        """
        response_size = len(response.encode('utf-8'))
        Log.info(f"Generated mock response ({response_size} bytes)")
        return response

    async def process_request_async(self, prompt: str) -> MockResponse:
        """
        Return a mock response without making actual API calls.

        Args:
            prompt (str): The input prompt for the request

        Returns:
            MockResponse: The mock response object
        """
        Log.info(
            f"Mocking async Ollama request (simulating {self.render_time}s)")
        await asyncio.sleep(self.render_time)
        return MockResponse(response=self.response)
