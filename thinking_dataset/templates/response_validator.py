"""Response validation functionality.

Provides validation capabilities for XML responses and content structure.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from xml.etree import ElementTree as ET

from thinking_dataset.utils.exceptions import XMLExtractionError


class ResponseValidator:
    """Validates XML response content."""

    @staticmethod
    def validate_xml_response(xml_str: str,
                              required_elements: set[str] | None) -> bool:
        """Validate an XML response against required elements.

        Args:
            xml_str: XML response string to validate.
            required_elements: Set of required element tags or None.

        Returns:
            True if response is valid according to requirements
                or if no requirements.
        """
        try:
            # Basic XML validation
            root = ET.fromstring(xml_str)
            if required_elements is None:
                return True

            # Check if at least one required element exists
            found_elements = {child.tag for child in root}
            return bool(required_elements & found_elements)

        except ET.ParseError:
            return False

    @staticmethod
    def extract_xml_content(text: str,
                            required_elements: set[str] | None = None) -> str:
        """Extract and validate XML content from response text.

        Args:
            text: Raw response text containing XML.
            required_elements: Optional set of required element tags.

        Returns:
            Extracted and validated inner XML content.

        Raises:
            XMLExtractionError: When XML content extraction
                or validation fails.
        """
        pattern = r'<output>(.*?)</output>'
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            raise XMLExtractionError(
                f"Failed to extract XML from '<output/>': {text[:100]}...")

        content = match.group(1).strip() if match.group(1) else match.group(0)

        # Validate if required elements provided
        if required_elements:
            xml_str = f"<output>{content}</output>"
            if not ResponseValidator.validate_xml_response(
                    xml_str, required_elements):
                raise XMLExtractionError(
                    f"Response missing required elements: {text[:100]}...")

        return content
