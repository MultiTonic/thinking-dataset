"""Exception handling decorator for Thinking Dataset.

This module provides a decorator for handling exceptions and logging errors
using the Log Singleton.

Functions:
    exceptions: Decorator to handle exceptions and log errors.
"""

import sys
import subprocess
from functools import wraps
from typing import Callable, Any

from thinking_dataset.utils.log import Log

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class XMLExtractionError(Exception):
    """Exception raised when XML extraction fails in response processing."""
    pass


class XMLValidationError(Exception):
    """Exception raised when XML validation fails in response processing."""
    pass


def exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions and log errors.

    Args:
        func (Callable): The function to wrap.

    Returns:
        Callable: The wrapped function with exception handling.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        error_occurred = False
        try:
            return func(
                *args, **{
                    key: val
                    for key, val in kwargs.items() if key != 'log'
                })
        except XMLValidationError as e:
            Log.error(f"XML validation error: {e}", exc_info=True)
            error_occurred = True
        except ValueError as e:
            Log.error(f"Validation error: {e}", exc_info=True)
            error_occurred = True
        except FileNotFoundError as e:
            Log.error(f"File not found error: {e}", exc_info=True)
            error_occurred = True
        except RuntimeError as e:
            Log.error(f"Runtime error: {e}", exc_info=True)
            error_occurred = True
        except subprocess.CalledProcessError as e:
            Log.error(f"Subprocess error: {e.stderr}", exc_info=True)
            error_occurred = True
        except Exception as e:
            Log.error(f"An unexpected error occurred: {e}", exc_info=True)
            error_occurred = True
        finally:
            if error_occurred:
                Log.error(f"{func.__name__} command did not complete.")
                sys.exit(1)

    return wrapper
