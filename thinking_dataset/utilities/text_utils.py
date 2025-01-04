# @file thinking_dataset/utilities/text_utils.py
# @description Utility functions for text processing in the thinking-dataset.
# @version 1.0.0
# @license MIT

import re


class TextUtils:
    """
    Utility functions for text processing in the thinking-dataset.
    """

    @staticmethod
    def truncate_text(text, max_length=240):
        """
        Truncate text to a maximum length, appending '...' if truncated.
        """
        if max_length < 4:
            return "..."[:max_length]
        return text if len(text) <= max_length else text[:max_length -
                                                         3] + '...'

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        """
        Convert a size in bytes to a human-readable format.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0

    @staticmethod
    def expand_contractions(text, contractions):
        """
        Expand contractions in a given text using a dictionary of contractions.
        """
        for contraction, full_form in contractions.items():
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', full_form,
                          text)
        return text

    @staticmethod
    def remove_special_characters(text):
        """
        Remove special characters from the text, leaving only basic characters.
        """
        return re.sub(r'[^ -~]', '', text)

    @staticmethod
    def remove_separators(text):
        """
        Remove long and double/triple separators from the text.
        """
        text = re.sub(r'-{4,}', '', text)
        text = re.sub(r'--+', '', text)
        return text

    @staticmethod
    def remove_whitespace(text):
        """
        Remove unnecessary whitespace from the text.
        """
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def normalize_numbers(text):
        """
        Normalize numbers by adding a space between the currency and number.
        """
        return re.sub(r'(\D)(\d)', r'\1 \2', text)

    @staticmethod
    def normalize_spaced_characters(text):
        """
        Normalize space-separated characters by removing the spaces.
        """
        return re.sub(r'(\b\w\s(?:\w\s)*\w\b)',
                      lambda m: m.group(0).replace(' ', ''), text)

    @staticmethod
    def remove_partial_extract_intro(text):
        """
        Remove the introduction line about partial extracts from the text.
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
        Remove numbered section headers from the text.
        """
        return re.sub(r'\d+\.\s*\([a-z]\)\s*', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_signoff(text):
        """
        Remove the sign-off writer's last name at the end of the text.
        """
        return re.sub(r'\.\s*\w*$', '.', text).strip()

    @staticmethod
    def remove_initial_pattern(text):
        """
        Remove the initial pattern from the start of the text if present.
        """
        return re.sub(r'^r\s\d+z\s\w+\s\d{2}\s', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_period_patterns(text):
        """
        Remove patterns like `. . .`, `. .`, and similar sequences.
        """
        return re.sub(r'(\.\s)+', '', text)

    @staticmethod
    def remove_header(text):
        """
        Remove the header before the first occurrence of 'subject:'.
        """
        return re.sub(r'^.*?(subject:)', r'\1', text,
                      flags=re.IGNORECASE).strip()

    @staticmethod
    def expand_terms(text, terms):
        """
        Expand abbreviations in the text using a dictionary of terms.
        """
        for abbr, full in terms.items():
            pattern = re.compile(r'(?<!\w)' + re.escape(abbr) + r'(?!\w)',
                                 re.IGNORECASE)
            text = pattern.sub(' ' + full + ' ', text)
        return text

    @staticmethod
    def remove_tiny_parentheses_content(text):
        """
        Remove content within parentheses that is very
        short (e.g., 1 to 5 characters).
        """
        return re.sub(r'\(\w{1,5}\)', '', text)

    @staticmethod
    def remove_weird_ids(text):
        """
        Remove weird ID numbers that have nothing to do
        with text (e.g., '031050z', '111433z').
        """
        return re.sub(r'\b\d{3,6}[a-z]+\b', '', text)

    @staticmethod
    def remove_weird_dates(text):
        """
        Remove weird date formats like '04/ 13/ 10'.
        """
        return re.sub(r'\b\d{2}/\s?\d{2}/\s?\d{2}\b', '', text)
