# @file thinking_dataset/templates/template_validator.py
# @description Template validation class.
# @version 1.0.0
# @license MIT

import jsonschema


class TemplateValidator:

    def __init__(self, schema):
        self.schema = schema

    def validate(self, template):
        try:
            jsonschema.validate(instance=template, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as err:
            print(f"Template validation error: {err}")
            return False
