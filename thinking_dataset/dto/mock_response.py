# @file thinking_dataset/dto/mock_response_dto.py
# @description Data Transfer Object for mock responses.
# @version 1.0.0
# @license MIT

from dataclasses import dataclass


@dataclass
class MockResponse:
    """
    Mock response object to match Ollama's response structure.

    Attributes:
        response (str): The mock response text.
    """
    response: str
