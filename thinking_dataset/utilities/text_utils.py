"""
@file thinking_dataset/utilities/text_utils.py
@description Utility functions for text processing in the thinking-dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
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
