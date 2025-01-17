"""
@file thinking_dataset/utils/execute.py
@description Defines a decorator for executing database operations.
@version 1.0.0
@license MIT
"""

from functools import wraps


def execute(operation_class):
    """
    A decorator to execute a database operation.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0]
            query = func(*args, **kwargs)
            operation = operation_class(instance, query)
            operation.execute()

        return wrapper

    return decorator
