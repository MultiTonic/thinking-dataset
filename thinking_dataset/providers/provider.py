# @file thinking_dataset/providers/provider.py
# @description Base class for providers
# @version 1.1.6
# @license MIT

from typing import Dict, Any
from abc import ABC, abstractmethod
from thinking_dataset.utils.provider_utils import ProviderUtils


class Provider(ABC):

    def __init__(self, config: Dict[str, Any]):
        provider_name = config.get("provider")
        if provider_name is None:
            raise ValueError("Provider name is not set in the configuration")
        self.config = ProviderUtils.get_provider_config(config, provider_name)

    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'Provider':
        return cls(config)

    @abstractmethod
    async def process_request_async(self, prompt: str) -> str:
        pass
