"""Logging Utility Module.

This module provides a unified logging class for the project, managing log
levels, formatting, and specialized logging configurations.

Functions:
    None

Classes:
    Log: Provides unified logging functionality across the project.
"""

import functools
import inspect
import logging
import sys
from typing import Any, Callable, Optional, TypeVar

LF = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
T = TypeVar("T")


class Log:
    """Unified logging class for the project.

    This class:
    1. Manages a singleton logging instance for consistent logging.
    2. Provides methods for different log levels (debug, info, warn, error).
    3. Handles logging configuration and level management.
    4. Offers specialized logging setup for external libraries.

    Methods:
        Core Setup:
            _get_name(): Gets the calling module and class name.
            _setup(): Initializes the logging system.
            get(): Returns the logger instance.
            get_handler(): Returns stdout stream handler.

        Level Management:
            set_level(level): Sets the global logging level.
            level(level): Decorator for temporary level changes.

        Logging Methods:
            debug(message): Logs debug messages.
            info(message): Logs informational messages.
            warn(message): Logs warning messages.
            error(message, exc_info): Logs error messages with optional trace.

        Configuration:
            configure_sqlalchemy_logging(): Configures SQLAlchemy logging
                levels.
    """

    _instance = None
    _level = logging.INFO

    # Logging levels
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    # Core setup methods
    @staticmethod
    def _get_name() -> str:
        """Get the calling module and class name for logging context."""
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        module_name = module.__name__ if module else "thinking-dataset"
        class_name = frame[3]
        return f"{module_name}.{class_name}"

    @staticmethod
    def _setup() -> None:
        """Initialize logging system with basic configuration."""
        logging.basicConfig(level=Log._level,
                            format=LF,
                            datefmt="%Y.%m.%d:%H:%M:%S",
                            handlers=[logging.StreamHandler(sys.stdout)])
        Log._instance = logging.getLogger("thinking-dataset")
        Log._instance.setLevel(Log._level)

    @staticmethod
    def get() -> logging.Logger:
        """Get or create the singleton logger instance."""
        if Log._instance is None:
            Log._setup()
        return Log._instance

    @staticmethod
    def get_handler() -> logging.StreamHandler:
        """Get a stdout stream handler for logging configuration."""
        return logging.StreamHandler(sys.stdout)

    # Level management
    @staticmethod
    def set_level(level: int) -> None:
        """Set the global logging level for all loggers.

        Args:
            level (int): Logging level to set
        """
        Log._level = level
        if Log._instance:
            Log._instance.setLevel(Log._level)
            logger = logging.getLogger("thinking-dataset")
            logger.setLevel(Log._level)

    @staticmethod
    def level(level: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator to temporarily change log level during method execution.

        Args:
            level (int): Logging level to set temporarily

        Returns:
            Callable: Decorator function
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                prev_level = Log._level
                Log.set_level(level)
                try:
                    return func(*args, **kwargs)
                finally:
                    Log.set_level(prev_level)

            return wrapper

        return decorator

    # Logging methods
    @staticmethod
    def debug(message: str) -> None:
        """Log a debug level message with calling context.

        Args:
            message (str): Message to log
        """
        if Log._level <= logging.DEBUG:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.debug(message)

    @staticmethod
    def info(message: str) -> None:
        """Log an info level message with calling context.

        Args:
            message (str): Message to log
        """
        if Log._level <= logging.INFO:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.info(message)

    @staticmethod
    def warn(message: str) -> None:
        """Log a warning level message with calling context.

        Args:
            message (str): Message to log
        """
        if Log._level <= logging.WARNING:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.warning(message)

    @staticmethod
    def error(message: str, exc_info: Optional[bool] = None) -> None:
        """Log an error level message with call context and optional trace.

        Args:
            message (str): Message to log
            exc_info (Optional[bool]): Include exception info if True
        """
        if Log._level <= logging.ERROR:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.error(message, exc_info=exc_info)

    # Configuration methods
    @staticmethod
    def configure_sqlalchemy_logging() -> None:
        """Configure SQLAlchemy logging levels to suppress verbose output."""
        logging_modules = [
            "sqlalchemy.engine.Engine.database", "sqlalchemy.pool",
            "sqlalchemy.dialects"
        ]
        for module in logging_modules:
            logging.getLogger(module).setLevel(logging.CRITICAL)
        Log.info("SQLAlchemy logging configured successfully.")
