"""
@file project_root/thinking_dataset/db/database.py
@description Implementation of the Database class.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from sqlalchemy import create_engine
from contextlib import contextmanager
from .session.session import Session
from ..utilities.log import Log
from ..utilities.execute import execute
from .operations.query import Query
from .operations.fetch import Fetch
from .database_config import DatabaseConfig


class Database:

    def __init__(self, config_path: str):
        self.config = DatabaseConfig(config_path)
        self.engine = create_engine(
            self.config.database_url,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            connect_args={'connect_timeout': self.config.connect_timeout},
            echo=self.config.log_queries)
        self.session = Session(self.engine)
        self.logger = Log.setup(__name__)

    @contextmanager
    def get_session(self):
        session = self.session.get()
        yield session

    @execute(Query)
    def query(self, query: str):
        return query

    @execute(Fetch)
    def fetch(self, query: str):
        return query
