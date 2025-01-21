# @file assets/scripts/generate_text.py
# @description Script to generate text using Ollama provider
# @version 1.0.4
# @license MIT

import asyncio
import argparse
import thinking_dataset.config as conf
from thinking_dataset.providers.ollama_provider import OllamaProvider


async def main(prompt: str, provider_name: str):
    instance = conf.initialize()
    provider_config = next(
        (provider['provider'] for provider in instance.get_value("providers")
         if provider['provider']['name'] == provider_name), None)

    if not provider_config:
        raise ValueError(
            f"Provider '{provider_name}' not found in configuration.")

    config = {
        "url": provider_config["url"],
        "model": provider_config["config"]["model"],
        "format": provider_config["config"]["format"],
        "options": provider_config["config"]["options"]
    }

    provider = OllamaProvider.initialize(config)
    result = await provider.process_request_async(prompt, lambda x: x)

    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate text using Ollama provider.")
    parser.add_argument("--prompt",
                        type=str,
                        required=True,
                        help="Prompt for text generation.")
    parser.add_argument("--provider",
                        type=str,
                        required=True,
                        help="Name of the provider (e.g., 'localhost').")

    args = parser.parse_args()

    asyncio.run(main(args.prompt, args.provider))
