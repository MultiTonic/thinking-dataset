"""Template extraction functionality.

Provides extraction capabilities for template files, handling the parsing
and extraction of XML schemas and content sections.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from xml.etree import ElementTree as ET


class TemplateExtractor:
    """Extracts and processes XML content from templates."""

    @staticmethod
    def find_template_start(content: str) -> re.Match[str] | None:
        """Find the start position of the OUTPUT TEMPLATE section.

        Args:
            content: Raw template content to search.

        Returns:
            Match object if template section found, None otherwise.
        """
        return re.search(r'-->\s*\*\*EXAMPLE OUTPUT TEMPLATE:\*\*', content)

    @staticmethod
    def extract_xml_schema(content: str) -> str | None:
        """Extract XML schema between <output> tags.

        Searches for and extracts the XML schema section from template content,
        including the enclosing output tags.

        Args:
            content: Raw template content containing XML schema.

        Returns:
            Complete XML schema if found, None otherwise.
        """
        template_start = TemplateExtractor.find_template_start(content)
        if not template_start:
            return None

        template_text = content[template_start.end():]
        pattern = r'<output>(.*?)</output>.*?---'
        match = re.search(pattern, template_text, re.DOTALL)

        if not match:
            return None

        return f"<output>{match.group(1)}</output>"

    @staticmethod
    def extract_required_elements(template: str | None) -> set[str] | None:
        """Extract required elements from template XML structure.

        Args:
            template: Template containing XML structure, or None.

        Returns:
            Set of required element tag names if template
                provided, None otherwise.
        """
        if not template:
            return None

        try:
            template_start = TemplateExtractor.find_template_start(template)
            if not template_start:
                return None

            template_text = template[template_start.end():]
            pattern = r'<output>(.*?)</output>'
            match = re.search(pattern, template_text, re.DOTALL)

            if not match:
                return None

            xml_str = f"<output>{match.group(1)}</output>"
            root = ET.fromstring(xml_str)
            return {child.tag for child in root}

        except (ET.ParseError, AttributeError):
            return None
