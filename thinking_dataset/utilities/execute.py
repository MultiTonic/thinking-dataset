"""
@file thinking_dataset/utilities/execute.py
@description Defines a decorator for executing database operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from functools import wraps


def execute(operation_class):
    """
    A decorator to execute a database operation.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Assuming the first argument is `self` for instance methods
            instance = args[0]
            query = func(*args, **kwargs)
            operation = operation_class(instance, query)
            operation.execute()

        return wrapper

    return decorator
