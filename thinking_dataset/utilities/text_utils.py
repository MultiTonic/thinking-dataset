"""
@file thinking_dataset/utilities/text_utils.py
@description Utility functions for text processing in the thinking-dataset.
@version 1.0.0
@license MIT
"""


class TextUtils:

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
