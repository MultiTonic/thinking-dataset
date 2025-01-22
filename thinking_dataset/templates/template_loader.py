# @file thinking_dataset/templates/template_loader.py
# @description Template loader class for Markdown Prompt templates.
# @version 1.0.4
# @license MIT


class TemplateLoader:

    def __init__(self, template_path: str):
        self.template_path = template_path

    def load(self) -> str:
        with open(self.template_path, 'r') as file:
            template = file.read()
        return template
