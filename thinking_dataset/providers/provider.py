# @file thinking_dataset/providers/provider.py
# @description Base class for providers.
# @version 1.1.6
# @license MIT

from typing import Dict, Any
from abc import ABC, abstractmethod
from thinking_dataset.utils.provider_utils import ProviderUtils


class Provider(ABC):
    """
    Base class for providers.

    This class:
    1. Initializes the provider with configuration settings.
    2. Provides an abstract method for processing requests.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration settings.

        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        provider_name = config.get("provider")
        if provider_name is None:
            raise ValueError("Provider name is not set in the configuration")
        self.config = ProviderUtils.get_provider_config(config, provider_name)

    @classmethod
    def initialize(cls,
                   config: Dict[str, Any],
                   mock: bool = False) -> 'Provider':
        """
        Initialize the provider with configuration and mock mode.

        Args:
            config (Dict[str, Any]): Configuration dictionary.
            mock (bool): Flag to use mock provider.

        Returns:
            Provider: An instance of the provider.
        """
        return cls(config, mock=mock)

    @abstractmethod
    async def process_request_async(self, prompt: str) -> str:
        """
        Process a request asynchronously and return the response.

        Args:
            prompt (str): The input prompt for the request.

        Returns:
            str: The response from the provider.
        """
        pass
