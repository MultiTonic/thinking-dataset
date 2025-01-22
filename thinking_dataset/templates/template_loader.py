# @file thinking_dataset/templates/template_loader.py
# @description Template loader class for Markdown Prompt templates.
# @version 1.0.5
# @license MIT

from functools import lru_cache


class TemplateLoader:

    def __init__(self, path: str):
        self.path = path

    @lru_cache(maxsize=None)
    def load(self) -> str:
        try:
            with open(self.path, 'r') as file:
                template = file.read()
            return template
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.path}")
        except IOError as e:
            raise IOError(f"Error reading template file: {e}")
