"""Template validation functionality.

Provides validation capabilities for template files, ensuring they contain
required sections and proper XML formatting. Works in conjunction with
TemplateExtractor for processing template content.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from xml.etree import ElementTree as ET

from thinking_dataset.templates.template_extractor import TemplateExtractor
from thinking_dataset.templates.response_validator import ResponseValidator


class TemplateValidator:
    """Validates template content against required criteria."""

    @staticmethod
    def _validate_template(content: str) -> None:
        """Validate that content contains required OUTPUT TEMPLATE section.

        Args:
            content: Raw template content to validate.

        Raises:
            ValueError: When template is missing
                required OUTPUT TEMPLATE section.
        """
        template_pattern = r'-->\s*\*\*EXAMPLE OUTPUT TEMPLATE:\*\*'
        if not re.search(template_pattern, content):
            raise ValueError(
                "Template missing required OUTPUT TEMPLATE section")

    @staticmethod
    def validate(content: str) -> bool:
        """Validate template content for required sections and XML structure.

        Performs complete validation including:
        - Checking for required OUTPUT TEMPLATE section
        - Extracting and validating XML schema
        - Parsing XML structure

        Args:
            content: Raw template content to validate.

        Returns:
            True if template is valid.

        Raises:
            ValueError: When template is missing sections or has invalid XML.
        """
        # Check for OUTPUT TEMPLATE section
        TemplateValidator._validate_template(content)

        # Extract XML template structure
        xml_template = TemplateExtractor.extract_xml_schema(content)
        if not xml_template:
            raise ValueError("Template missing valid XML structure")

        # Validate XML structure
        try:
            ET.fromstring(xml_template)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML template structure: {str(e)}")

        return True

    @staticmethod
    def validate_xml_response(xml_str: str, template: str | None) -> bool:
        """Validate an XML response against a template structure.

        Args:
            xml_str: XML response string to validate.
            template: Optional template containing expected structure.

        Returns:
            True if response is valid according to template or basic XML rules.
        """
        required_elements = TemplateExtractor.extract_required_elements(
            template) if template else None
        return ResponseValidator.validate_xml_response(xml_str,
                                                       required_elements)
