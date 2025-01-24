# @file thinking_dataset/utils/text_utils.py
# @description Utility functions for text processing in the thinking-dataset.
# @version 1.1.3
# @license MIT

import re
from typing import Optional
from lorem_text import lorem


class TextUtils:
    """
    Utility functions for text processing in the thinking-dataset.

    This class:
    1. Provides methods for text truncation, size formatting, and normalization
    2. Handles text cleaning, contraction expansion, and special char removal
    3. Generates lorem ipsum text for testing purposes

    Methods:
        truncate_text(text, max_length): Truncate text to a maximum length.
        human_readable_size(size, decimal_places): Convert size to readable.
        expand_contractions(text, contractions): Expand contractions in text.
        remove_special_characters(text): Remove special characters from text.
        remove_separators(text): Remove separators from text.
        remove_whitespace(text): Remove extra whitespace from text.
        normalize_numbers(text): Normalize numbers in text.
        normalize_spaced_characters(text): Normalize spaced characters in text.
        remove_partial_extract_intro(text): Remove partials from text.
        remove_section_headers(text): Remove section headers from text.
        remove_signoff(text): Remove signoff from text.
        remove_initial_pattern(text): Remove initial pattern from text.
        remove_period_patterns(text): Remove period patterns from text.
        remove_header(text): Remove header from text.
        expand_terms(text, terms): Expand terms in text.
        remove_tiny_parentheses_content(text): Remove tiny parentheses content.
        remove_weird_ids(text): Remove weird IDs from text.
        remove_weird_dates(text): Remove weird dates from text.
        shorten_path(path, max_length): Shorten a path to a maximum length.
        generate_lorem_ipsum(paragraphs, char_limit): Generate random text.
    """

    @staticmethod
    def truncate_text(text, max_length=240):
        """
        Truncate text to a maximum length.

        Args:
            text (str): The text to truncate.
            max_length (int): The maximum length of the truncated text.

        Returns:
            str: The truncated text.
        """
        if max_length < 4:
            return "..."[:max_length]
        return text if len(text) <= max_length else text[:max_length -
                                                         3] + '...'

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        """
        Convert size to human-readable format.

        Args:
            size (float): The size in bytes.
            decimal_places (int): The number of decimal places to include.

        Returns:
            str: The human-readable size.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0

    @staticmethod
    def expand_contractions(text, contractions):
        """
        Expand contractions in text.

        Args:
            text (str): The text with contractions.
            contractions (dict): A dictionary of contractions and expansions.

        Returns:
            str: The text with expanded contractions.
        """
        for contraction, full_form in contractions.items():
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', full_form,
                          text)
        return text

    @staticmethod
    def remove_special_characters(text):
        """
        Remove special characters from text.

        Args:
            text (str): The text with special characters.

        Returns:
            str: The text without special characters.
        """
        return re.sub(r'[^ -~]', '', text)

    @staticmethod
    def remove_separators(text):
        """
        Remove separators from text.

        Args:
            text (str): The text with separators.

        Returns:
            str: The text without separators.
        """
        text = re.sub(r'-{4,}', '', text)
        text = re.sub(r'--+', '', text)
        return text

    @staticmethod
    def remove_whitespace(text):
        """
        Remove extra whitespace from text.

        Args:
            text (str): The text with extra whitespace.

        Returns:
            str: The text without extra whitespace.
        """
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def normalize_numbers(text):
        """
        Normalize numbers in text.

        Args:
            text (str): The text with numbers.

        Returns:
            str: The text with normalized numbers.
        """
        return re.sub(r'(\D)(\d)', r'\1 \2', text)

    @staticmethod
    def normalize_spaced_characters(text):
        """
        Normalize spaced characters in text.

        Args:
            text (str): The text with spaced characters.

        Returns:
            str: The text with normalized spaced characters.
        """
        return re.sub(r'(\b\w\s(?:\w\s)*\w\b)',
                      lambda m: m.group(0).replace(' ', ''), text)

    @staticmethod
    def remove_partial_extract_intro(text):
        """
        Remove partial extract intro from text.

        Args:
            text (str): The text with partial extract intro.

        Returns:
            str: The text without partial extract intro.
        """
        return re.sub(
            r'^this record is a partial extract of the original cable\.\s*'
            r'the full text of the original cable is not available\.\s*',
            '',
            text,
            flags=re.IGNORECASE)

    @staticmethod
    def remove_section_headers(text):
        """
        Remove section headers from text.

        Args:
            text (str): The text with section headers.

        Returns:
            str: The text without section headers.
        """
        return re.sub(r'\d+\.\s*\([a-z]\)\s*', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_signoff(text):
        """
        Remove signoff from text.

        Args:
            text (str): The text with signoff.

        Returns:
            str: The text without signoff.
        """
        return re.sub(r'\.\s*\w*$', '.', text).strip()

    @staticmethod
    def remove_initial_pattern(text):
        """
        Remove initial pattern from text.

        Args:
            text (str): The text with initial pattern.

        Returns:
            str: The text without initial pattern.
        """
        return re.sub(r'^r\s\d+z\s\w+\s\d{2}\s', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_period_patterns(text):
        """
        Remove period patterns from text.

        Args:
            text (str): The text with period patterns.

        Returns:
            str: The text without period patterns.
        """
        return re.sub(r'(\.\s)+', '', text)

    @staticmethod
    def remove_header(text):
        """
        Remove header from text.

        Args:
            text (str): The text with header.

        Returns:
            str: The text without header.
        """
        return re.sub(r'^.*?(subject:)', r'\1', text,
                      flags=re.IGNORECASE).strip()

    @staticmethod
    def expand_terms(text, terms):
        """
        Expand terms in text.

        Args:
            text (str): The text with terms.
            terms (dict): A dictionary of terms and their expansions.

        Returns:
            str: The text with expanded terms.
        """
        for abbr, full in terms.items():
            pattern = re.compile(r'(?<!\w)' + re.escape(abbr) + r'(?!\w)',
                                 re.IGNORECASE)
            text = pattern.sub(' ' + full + ' ', text)
        return text

    @staticmethod
    def remove_tiny_parentheses_content(text):
        """
        Remove tiny parentheses content from text.

        Args:
            text (str): The text with tiny parentheses content.

        Returns:
            str: The text without tiny parentheses content.
        """
        return re.sub(r'\(\w{1,5}\)', '', text)

    @staticmethod
    def remove_weird_ids(text):
        """
        Remove weird IDs from text.

        Args:
            text (str): The text with weird IDs.

        Returns:
            str: The text without weird IDs.
        """
        return re.sub(r'\b\d{3,6}[a-z]+\b', '', text)

    @staticmethod
    def remove_weird_dates(text):
        """
        Remove weird dates from text.

        Args:
            text (str): The text with weird dates.

        Returns:
            str: The text without weird dates.
        """
        return re.sub(r'\b\d{2}/\s?\d{2}/\s?\d{2}\b', '', text)

    @staticmethod
    def shorten_path(path: str, max_length: int) -> str:
        """
        Shorten a file path to a maximum length.

        Args:
            path (str): The file path to shorten.
            max_length (int): The maximum length of the shortened path.

        Returns:
            str: The shortened file path.
        """
        if len(path) <= max_length:
            return path

        file_name = path.split('/')[-1]
        file_name_length = len(file_name)

        if file_name_length >= max_length:
            return f"...{file_name[-(max_length - 3):]}"

        remaining_length = max_length - file_name_length - 3
        return f"...{path[:remaining_length]}...{file_name}"

    @staticmethod
    def generate_lorem_ipsum(paragraphs: int = 1,
                             char_limit: Optional[int] = None) -> str:
        """
        Generate lorem ipsum text.

        Args:
            paragraphs (int): Number of paragraphs to generate.
            char_limit (Optional[int]): Optional character limit
                for the generated text.

        Returns:
            str: Generated lorem ipsum text.
        """
        text = '\n\n'.join([lorem.paragraph() for _ in range(paragraphs)])
        if char_limit:
            text = TextUtils.truncate_text(text, char_limit)
        return text
