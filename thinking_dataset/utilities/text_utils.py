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
        if max_length < 4:
            return "..."[:max_length]
        return text if len(text) <= max_length else text[:max_length -
                                                         3] + '...'

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0

    @staticmethod
    def expand_contractions(text, contractions):
        for contraction, full_form in contractions.items():
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', full_form,
                          text)
        return text

    @staticmethod
    def remove_special_characters(text):
        return re.sub(r'[^ -~]', '', text)

    @staticmethod
    def remove_separators(text):
        text = re.sub(r'-{4,}', '', text)
        text = re.sub(r'--+', '', text)
        return text

    @staticmethod
    def remove_whitespace(text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def normalize_numbers(text):
        return re.sub(r'(\D)(\d)', r'\1 \2', text)

    @staticmethod
    def normalize_spaced_characters(text):
        return re.sub(r'(\b\w\s(?:\w\s)*\w\b)',
                      lambda m: m.group(0).replace(' ', ''), text)

    @staticmethod
    def remove_partial_extract_intro(text):
        return re.sub(
            r'^this record is a partial extract of the original cable\.\s*'
            r'the full text of the original cable is not available\.\s*',
            '',
            text,
            flags=re.IGNORECASE)

    @staticmethod
    def remove_section_headers(text):
        return re.sub(r'\d+\.\s*\([a-z]\)\s*', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_signoff(text):
        return re.sub(r'\.\s*\w*$', '.', text).strip()

    @staticmethod
    def remove_initial_pattern(text):
        return re.sub(r'^r\s\d+z\s\w+\s\d{2}\s', '', text, flags=re.IGNORECASE)

    @staticmethod
    def remove_period_patterns(text):
        return re.sub(r'(\.\s)+', '', text)

    @staticmethod
    def remove_header(text):
        return re.sub(r'^.*?(subject:)', r'\1', text,
                      flags=re.IGNORECASE).strip()

    @staticmethod
    def expand_terms(text, terms):
        for abbr, full in terms.items():
            pattern = re.compile(r'(?<!\w)' + re.escape(abbr) + r'(?!\w)',
                                 re.IGNORECASE)
            text = pattern.sub(' ' + full + ' ', text)
        return text

    @staticmethod
    def remove_tiny_parentheses_content(text):
        return re.sub(r'\(\w{1,5}\)', '', text)

    @staticmethod
    def remove_weird_ids(text):
        return re.sub(r'\b\d{3,6}[a-z]+\b', '', text)

    @staticmethod
    def remove_weird_dates(text):
        return re.sub(r'\b\d{2}/\s?\d{2}/\s?\d{2}\b', '', text)
