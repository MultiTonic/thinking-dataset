"""
@file tests/thinking_dataset/utilities/test_text_utils.py
@description Unit tests for text utility functions in the thinking-dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from thinking_dataset.utils.text_utils import TextUtils


def test_truncate_text_simple():
    """
    Simple test for truncate_text function.
    """
    # Case: Text shorter than max_length
    short_text = "This is a short text."
    assert TextUtils.truncate_text(short_text) == short_text

    # Case: Text exactly max_length
    exact_length_text = "a" * 240
    assert TextUtils.truncate_text(exact_length_text) == exact_length_text

    # Case: Text longer than max_length
    long_text = "a" * 241
    truncated_text = TextUtils.truncate_text(long_text)
    assert truncated_text.endswith('...')
    assert len(truncated_text) <= 240


def test_truncate_text_negative():
    """
    Negative tests for truncate_text function.
    """
    # Case: None input
    with pytest.raises(TypeError):
        TextUtils.truncate_text(None)

    # Case: Empty string
    assert TextUtils.truncate_text("") == ""

    # Case: max_length set to 1
    assert TextUtils.truncate_text("a long text", max_length=1) == "."

    # Case: max_length set to 2
    assert TextUtils.truncate_text("a long text", max_length=2) == ".."

    # Case: max_length set to 3
    assert TextUtils.truncate_text("a long text", max_length=3) == "..."

    # Case: max_length set to 4
    assert TextUtils.truncate_text("a long text", max_length=4) == "a..."


if __name__ == "__main__":
    pytest.main()
