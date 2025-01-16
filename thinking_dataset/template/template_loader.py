# @file thinking_dataset/template/template_loader.py
# @description Template loader class.
# @version 1.0.2
# @license MIT

import json
from .template_validator import TemplateValidator


class TemplateLoader:

    def __init__(self, template_path, schema):
        self.template_path = template_path
        self.validator = TemplateValidator(schema)

    def load(self):
        with open(self.template_path, 'r') as file:
            template = json.load(file)

        if self.validator.validate(template):
            return json.dumps(template)
        else:
            raise ValueError("Invalid template format")
