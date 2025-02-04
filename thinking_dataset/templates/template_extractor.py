"""Template extraction functionality.

Provides extraction capabilities for template files, handling the parsing
and extraction of XML schemas and content sections.
"""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from xml.etree import ElementTree as ET


class TemplateExtractor:
    """Extracts and processes XML content from templates."""

    @staticmethod
    def extract_xml_schema(content: str) -> str | None:
        """Extract XML schema between root-level output tags.

        Searches for and extracts the XML schema section from template content,
        only matching output tags that are not nested within other elements.

        Args:
            content: Raw template content containing XML schema.

        Returns:
            Complete XML schema if found, None otherwise.
        """
        pattern = r'<output>(?:(?!</output>).)*?</output>'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0).strip() if match else None

    @staticmethod
    def extract_required_elements(template: str | None) -> set[str] | None:
        """Extract required elements from template XML structure.

        Args:
            template: Template containing XML structure, or None.

        Returns:
            Set of required element tag names if template provided,
                None otherwise.
        """
        if not template:
            return None

        try:
            pattern = r'<output>(?:(?!</output>).)*?</output>'
            match = re.search(pattern, template, re.DOTALL)

            if not match:
                return None

            root = ET.fromstring(match.group(0))
            return {child.tag for child in root}

        except (ET.ParseError, AttributeError):
            return None
