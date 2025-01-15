# @file thinking_dataset/config/config_attr.py
# @description Defines ConfigAttr class for attribute initialization.
# @version 1.0.0
# @license MIT


class ConfigAttr:

    @staticmethod
    def initialize_attributes(config, obj):
        obj.dataset_name = config.get('dataset', {}).get('name')
        obj.dataset_type = config.get('dataset', {}).get('type', 'parquet')
        obj.database_url = config.get('database', {}).get('url')
        obj.database_type = config.get('database', {}).get('type', 'sqlite')
        obj.pool_size = config.get('database', {}).get('config',
                                                       {}).get('pool_size', 5)
        obj.max_overflow = config.get('database',
                                      {}).get('config',
                                              {}).get('max_overflow', 10)
        obj.connect_timeout = config.get('database', {}).get('config', {}).get(
            'connect_timeout', 30)
        obj.read_timeout = config.get('database',
                                      {}).get('config',
                                              {}).get('read_timeout', 30)
        obj.log_queries = config.get('database',
                                     {}).get('config',
                                             {}).get('log_queries', True)
        obj.environment = config.get('database', {}).get('env', 'development')
        obj.database_name = config.get('database', {}).get('name')
        obj.root = config.get('paths', {}).get('root', '.')
        obj.templates = config.get('paths', {}).get('templates',
                                                    './assets/templates')
        obj.data = config.get('paths', {}).get('data', './data')
        obj.raw = config.get('paths', {}).get('raw', './data/raw')
        obj.process = config.get('paths', {}).get('process', './data/process')
        obj.export = config.get('paths', {}).get('export', './data/export')
        obj.database = config.get('paths', {}).get('database', './data/db')
        obj.include_files = config.get('files', {}).get('include', [])
        obj.exclude_files = config.get('files', {}).get('exclude', [])
        obj.load_patterns = config.get('files', {}).get(
            'load', ['{file_root}_prepare{file_ext}'])
        obj.pipelines = config.get('pipelines', [])
