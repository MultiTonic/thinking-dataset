# @file thinking_dataset/providers/provider.py
# @description Base class for providers
# @version 1.1.1
# @license MIT

from typing import Dict, Any
from abc import ABC, abstractmethod


class Provider(ABC):

    @classmethod
    @abstractmethod
    def initialize(cls, config: Dict[str, Any]) -> 'Provider':
        pass

    @abstractmethod
    async def process_async_request(self, prompt: str) -> Any:
        pass
