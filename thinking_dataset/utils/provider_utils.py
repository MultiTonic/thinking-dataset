# @file thinking_dataset/utils/provider_utils.py
# @description Utility functions for provider configuration.
# @version 1.0.1
# @license MIT

import thinking_dataset.config as conf
from .log import Log
from typing import Dict, Any
from thinking_dataset.config.config_keys import ConfigKeys

CK = ConfigKeys


class ProviderUtils:

    @staticmethod
    def get_provider_config(config: Dict[str, Any],
                            provider_name: str) -> Dict[str, Any]:
        Log.info(f"Looking up configuration for provider: {provider_name}")

        # Get providers from global config
        instance = conf.initialize()
        providers = instance.get_value(CK.PROVIDERS)
        Log.info(f"Found {len(providers)} providers in global config")

        # Search through provider array for matching name
        provider_config = next(
            (provider['provider'] for provider in providers
             if provider.get('provider', {}).get('name') == provider_name),
            None)

        if not provider_config:
            Log.error(
                f"Provider '{provider_name}' not found in providers: "
                f"{[p.get('provider', {}).get('name') for p in providers]}")
            raise ValueError(
                f"Provider '{provider_name}' not found in configuration.")

        Log.info(f"Found provider config: {provider_config}")
        Log.info(f"Provider type: {provider_config.get('type')}")
        Log.info(f"Provider URL: {provider_config.get('url')}")

        return provider_config
