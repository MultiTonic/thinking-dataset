# @file thinking_dataset/templates/template_loader.py
# @description Template loader class for Markdown Prompt templates.
# @version 1.0.6
# @license MIT

from functools import lru_cache


class TemplateLoader:

    @staticmethod
    @lru_cache(maxsize=None)
    def load(path: str) -> str:
        try:
            with open(path, 'r') as file:
                template = file.read()
            return template
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {path}")
        except IOError as e:
            raise IOError(f"Error reading template file: {e}")
