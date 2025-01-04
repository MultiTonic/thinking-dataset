"""
@file thinking_dataset/utilities/exceptions.py
@description Defines a decorator for handling exceptions and logging.
@version 1.0.0
@license MIT
"""

import sys
from functools import wraps
from ..utilities.log import Log


def exceptions(func):
    """
    A decorator to handle exceptions and logging for a function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        log = kwargs.get('log', Log.setup(func.__name__))
        error_occurred = False
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            Log.error(log, f"Validation error: {e}", exc_info=True)
            error_occurred = True
        except FileNotFoundError as e:
            Log.error(log, f"File not found error: {e}", exc_info=True)
            error_occurred = True
        except RuntimeError as e:
            Log.error(log, f"Runtime error: {e}", exc_info=True)
            error_occurred = True
        except Exception as e:
            Log.error(log, f"An unexpected error occurred: {e}", exc_info=True)
            error_occurred = True
        finally:
            if error_occurred:
                Log.error(log, f"{func.__name__} command did not complete.")
                sys.exit(1)

    return wrapper