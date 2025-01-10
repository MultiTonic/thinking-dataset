"""
@file thinking_dataset/utils/exceptions.py
@desc Decorator for handling exceptions and logging using the Log Singleton.
@version 1.0.1
@license MIT
"""

import sys
from functools import wraps
from thinking_dataset.utils.log import Log


def exceptions(func):
    """
    A decorator to handle exceptions and logging for a function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        error_occurred = False
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            Log.error(f"Validation error: {e}", exc_info=True)
            error_occurred = True
        except FileNotFoundError as e:
            Log.error(f"File not found error: {e}", exc_info=True)
            error_occurred = True
        except RuntimeError as e:
            Log.error(f"Runtime error: {e}", exc_info=True)
            error_occurred = True
        except Exception as e:
            Log.error(f"An unexpected error occurred: {e}", exc_info=True)
            error_occurred = True
        finally:
            if error_occurred:
                Log.error(f"{func.__name__} command did not complete.")
                sys.exit(1)

    return wrapper
