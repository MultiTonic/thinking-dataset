# @file thinking_dataset/utils/provider_utils.py
# @description Utility functions for provider configuration.
# @version 1.0.0
# @license MIT

from typing import Dict, Any


class ProviderUtils:

    @staticmethod
    def get_provider_config(config: Dict[str, Any],
                            provider_name: str) -> Dict[str, Any]:
        provider_config = next((provider
                                for provider in config.get("providers", [])
                                if provider["name"] == provider_name), None)

        if not provider_config:
            raise ValueError(
                f"Provider '{provider_name}' not found in configuration.")

        return provider_config
