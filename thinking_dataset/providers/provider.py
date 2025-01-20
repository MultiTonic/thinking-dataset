# @file provider.py
# @description Base class for providers
# @version 1.1.0
# @license MIT

from abc import ABC, abstractmethod
from typing import Dict, Any


class Provider(ABC):

    @classmethod
    @abstractmethod
    def initialize(cls, config: Dict[str, Any]) -> 'Provider':
        pass

    @abstractmethod
    async def process_async_request(self, prompt: str) -> Any:
        pass
