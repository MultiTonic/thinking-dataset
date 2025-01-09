"""
@file tests/thinking_dataset/utilities/test_execute.py
@description Unit tests for the execute decorator.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from thinking_dataset.utils.execute import execute


class MockOperation:
    """
    Mock operation class for testing.
    """

    def __init__(self, instance, query):
        self.instance = instance
        self.query = query

    def execute(self):
        self.instance.executed_query = self.query


class ExampleClass:  # Renamed to avoid PytestCollectionWarning
    """
    A class to use the execute decorator for testing.
    """

    def __init__(self):
        self.executed_query = None

    @execute(MockOperation)
    def sample_method(self, query):
        return query


@pytest.fixture
def example_instance():
    return ExampleClass()


def test_execute_decorator(example_instance):
    """
    Test if the execute decorator correctly executes the operation.
    """
    example_instance.sample_method("SELECT * FROM test_table")
    assert example_instance.executed_query == "SELECT * FROM test_table"


def test_execute_decorator_multiple_calls(example_instance):
    """
    Test if the execute decorator correctly handles multiple calls.
    """
    queries = ["SELECT * FROM test_table1", "SELECT * FROM test_table2"]
    for query in queries:
        example_instance.sample_method(query)
        assert example_instance.executed_query == query


if __name__ == "__main__":
    pytest.main()
