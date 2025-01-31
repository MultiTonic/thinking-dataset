"""Template validation functionality.

This module provides validation capabilities for template files,
ensuring they contain required sections and formatting.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from xml.etree import ElementTree as ET

from thinking_dataset.utils.exceptions import XMLExtractionError
from thinking_dataset.utils.exceptions import XMLValidationError


class TemplateValidator:
    """Validates template content against required criteria."""

    @staticmethod
    def validate(content: str) -> bool:
        """Validate template content for required sections and XML structure.

        Args:
            content (str): Template content to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If template is missing required sections or
                has invalid XML
        """
        # Check for OUTPUT TEMPLATE section
        template_pattern = r'-->\s*\*\*OUTPUT TEMPLATE:\*\*'
        if not re.search(template_pattern, content):
            raise ValueError(
                "Template missing required OUTPUT TEMPLATE section")

        # Extract XML template structure
        xml_template = TemplateValidator._extract_xml_template(content)
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
            xml_str (str): The XML response to validate.
            template (str | None): Template to validate against.
                If None, only basic XML validation is performed.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            # Basic XML validation
            root = ET.fromstring(xml_str)
            if template is None:
                return True

            # More lenient validation for partial responses
            # TODO do this dynamically based on template structure
            required_elements = {
                'initial-thought',
                'unique-thoughts',
                'final-synthesis',  # hardcoded for now
            }
            found_elements = {child.tag for child in root}

            # Check if at least one required element exists and is valid
            return bool(required_elements & found_elements)

        except ET.ParseError:
            return False

    @staticmethod
    def _extract_xml_template(content: str) -> str | None:
        """Extract XML template between <output> tags.

        Args:
            content (str): Template content

        Returns:
            str | None: Extracted XML template or None if not found
        """
        # Find OUTPUT TEMPLATE section
        template_start = re.search(r'-->\s*\*\*OUTPUT TEMPLATE:\*\*', content)
        if not template_start:
            return None

        # Find XML structure between <output> tags
        template_text = content[template_start.end():]
        pattern = r'<output>(.*?)</output>.*?---'
        match = re.search(pattern, template_text, re.DOTALL)

        if not match:
            return None

        return f"<output>{match.group(1)}</output>"

    @staticmethod
    def _extract_xml_content(text: str, template: str | None = None) -> str:
        """Extract and validate XML content.

        Args:
            text (str): Raw response text containing XML
            template (str | None): Template for validation, if any

        Returns:
            str: Extracted and validated inner content

        Raises:
            XMLExtractionError: If content extraction fails
            XMLValidationError: If validation fails
        """
        # First find any XML-like content
        pattern = r'<output>(.*?)</output>'
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            # Try to find partial XML if complete XML not found
            pattern = \
                r'<(initial-thought|unique-thoughts|final-synthesis)>.*?</\1>'
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                raise XMLExtractionError(
                    f"Failed to extract XML: {text[:100]}...")

        # Extract inner content only
        content = match.group(1).strip() if match.group(1) else match.group(0)

        # Validate complete structure (temporarily wrapped for validation)
        validation_xml = f"<output>{content}</output>"
        if not TemplateValidator.validate_xml_response(validation_xml,
                                                       template):
            raise XMLValidationError(
                f"Failed to validate XML: {text[:100]}...")

        # Return only inner content
        return content
