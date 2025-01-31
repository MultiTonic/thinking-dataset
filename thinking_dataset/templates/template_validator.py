"""Template validation functionality.

This module provides validation capabilities for template files,
ensuring they contain required sections and formatting.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re


class TemplateValidator:
    """Validates template content against required criteria."""

    @staticmethod
    def validate(content: str) -> bool:
        """Validate template content for required output template section.

        Args:
            content (str): Template content to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If template is missing required output template section
        """
        pattern = r'-->\s*\*\*OUTPUT TEMPLATE:\*\*'

        if not re.search(pattern, content):
            raise ValueError(
                "Template missing required OUTPUT TEMPLATE section")

        return True
