"""
@file project_root/thinking_dataset/db/database_config.py
@description Defines DatabaseConfig class for storing database configuration.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from utilities.config_loader import ConfigLoader


class DatabaseConfig:

    def __init__(self, config_path: str):
        loader = ConfigLoader(config_path)
        config = loader.get('database')
        self.database_url = config.get('url')
        self.database_type = config.get('type', 'sqlite')
        self.pool_size = config.get('pool_size', 5)
        self.max_overflow = config.get('max_overflow', 10)
        self.connect_timeout = config.get('connect_timeout', 30)
        self.read_timeout = config.get('read_timeout', 30)
        self.log_queries = config.get('log_queries', True)
        self.environment = config.get('environment', 'development')
