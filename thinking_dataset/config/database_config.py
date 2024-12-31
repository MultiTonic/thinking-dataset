"""
@file project_root/thinking_dataset/config/database_config.py
@description Defines DatabaseConfig class for storing database configuration.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from thinking_dataset.utilities.config_loader import ConfigLoader


class DatabaseConfig:
    """
    Class for storing database configuration.

    @param config_path: Path to the configuration file.
    """

    def __init__(self, config_path: str):
        loader = ConfigLoader(config_path)
        config = loader.get('database')
        self.database_type = config.get('type', 'sqlite')
        self.pool_size = config.get('pool_size', 5)
        self.max_overflow = config.get('max_overflow', 10)
        self.connect_timeout = config.get('connect_timeout', 30)
        self.read_timeout = config.get('read_timeout', 30)
        self.log_queries = config.get('log_queries', True)
        self.environment = config.get('environment', 'development')

    def validate(self):
        """
        Validate the configuration settings.

        @raises ValueError: If any of the configuration settings are invalid.
        """
        if self.database_type not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError("Database type must be one of "
                             "'sqlite', 'postgresql', or 'mysql'.")
        if not isinstance(self.pool_size, int) or self.pool_size < 0:
            raise ValueError("Pool size must be a non-negative integer.")
        if not isinstance(self.max_overflow, int) or self.max_overflow < 0:
            raise ValueError("Max overflow must be a non-negative integer.")
        if not isinstance(self.connect_timeout,
                          int) or self.connect_timeout < 0:
            raise ValueError("Connect timeout must be a non-negative integer.")
        if not isinstance(self.read_timeout, int) or self.read_timeout < 0:
            raise ValueError("Read timeout must be a non-negative integer.")
        if not isinstance(self.log_queries, bool):
            raise ValueError("Log queries must be a boolean.")
        if self.environment not in ['development', 'testing', 'production']:
            raise ValueError("Environment must be one of "
                             "'development', 'testing', or 'production'.")
