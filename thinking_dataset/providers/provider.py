# @file thinking_dataset/providers/provider.py
# @description Base class for providers
# @version 1.1.3
# @license MIT

from typing import Dict, Any, Callable
from abc import ABC, abstractmethod


class Provider(ABC):

    @classmethod
    @abstractmethod
    def initialize(cls, config: Dict[str, Any]) -> 'Provider':
        pass

    @abstractmethod
    async def process_request_async(self, prompt: str,
                                    validator: Callable[[str], Any]) -> Any:
        pass
