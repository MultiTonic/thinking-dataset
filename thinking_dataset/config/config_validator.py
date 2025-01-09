# @file thinking_dataset/config/config_validator.py
# @description Defines class for validating dataset configuration.
# @version 1.0.1
# @license MIT

from thinking_dataset.utils.log import Log


class ConfigValidator:
    """
    Class for validating dataset configuration.
    """

    @staticmethod
    def validate(config):
        missing = []

        if not config.dataset_name:
            missing.append("dataset_name")
        if not config.dataset_type:
            missing.append("dataset_type")
        if not config.database_url:
            missing.append("database_url")
        if not config.root:
            missing.append("root")
        if not config.data:
            missing.append("data")
        if not config.raw:
            missing.append("raw")
        if not config.process:
            missing.append("process")
        if not config.export:
            missing.append("export")
        if not config.database:
            missing.append("database")
        if not config.include_files:
            missing.append("include_files")
        if not config.exclude_files:
            missing.append("exclude_files")
        if not config.load_patterns:
            missing.append("load_patterns")
        if not config.pipelines:
            missing.append("pipelines")

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}")

        if config.database_type not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError(
                "Database type must be 'sqlite', 'postgresql', or 'mysql'.")
        if not isinstance(config.pool_size, int) or config.pool_size < 0:
            raise ValueError("Pool size must be a non-negative integer.")
        if not isinstance(config.max_overflow, int) or config.max_overflow < 0:
            raise ValueError("Max overflow must be a non-negative integer.")
        if not isinstance(config.connect_timeout,
                          int) or config.connect_timeout < 0:
            raise ValueError("Connect timeout must be a non-negative integer.")
        if not isinstance(config.read_timeout, int) or config.read_timeout < 0:
            raise ValueError("Read timeout must be a non-negative integer.")
        if not isinstance(config.log_queries, bool):
            raise ValueError("Log queries must be a boolean.")
        if config.environment not in ['development', 'testing', 'production']:
            raise ValueError(
                "Environment must be 'development', 'testing', or 'production'"
            )

        Log.info("Configuration validated successfully.")
