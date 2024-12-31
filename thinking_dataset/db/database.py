"""
@file thinking_dataset/db/database.py
@description Implementation of the Database class.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys
from sqlalchemy import create_engine, exc
from contextlib import contextmanager
from ..utilities.log import Log
from ..utilities.execute import execute
from .operations.query import Query
from .operations.fetch import Fetch
from ..config.database_config import DatabaseConfig
from .database_session import DatabaseSession as Session


class Database:

    def __init__(self, url: str, config_path: str = None):
        self.log = Log.setup(__name__)
        try:
            self._load_config(config_path)
            self._set_database_url(url)
            self._create_database_path()
            self._initialize_engine()
            self._initialize_session()
            Log.info(self.log, "Database initialized successfully.")
        except exc.SQLAlchemyError as e:
            Log.error(self.log, f"Error initializing the Database class: {e}")
            sys.exit(1)

    def _load_config(self, config_path: str):
        if config_path:
            self.config = DatabaseConfig(config_path)
            self.config.validate()
            Log.info(self.log, "Database configuration loaded successfully.")
        else:
            self.config = None

    def _set_database_url(self, url: str):
        self.url = url

    def _create_database_path(self):
        database_path = os.path.dirname(self.url.split("///")[-1])
        os.makedirs(database_path, exist_ok=True)
        Log.info(self.log,
                 f"Database path {database_path} created successfully.")

    def _initialize_engine(self):
        self.engine = create_engine(
            self.url,
            pool_size=self.config.pool_size if self.config else 5,
            max_overflow=self.config.max_overflow if self.config else 10,
            connect_args={
                'timeout': self.config.connect_timeout if self.config else 30
            },
            echo=self.config.log_queries if self.config else False)
        Log.info(self.log, "Database engine created successfully.")

    def _initialize_session(self):
        self.session = Session(self.engine)
        Log.info(self.log, "Session initialized successfully.")

    @contextmanager
    def get_session(self):
        try:
            with self.session.get() as session:
                yield session
                Log.info(self.log, "Session retrieved successfully.")
        except exc.SQLAlchemyError as e:
            Log.error(self.log, f"Error retrieving the session: {e}")

    @execute(Query)
    def query(self, query: str):
        Log.info(self.log, f"Executing query: {query}")
        return query

    @execute(Fetch)
    def fetch(self, query: str):
        Log.info(self.log, f"Fetching data with query: {query}")
        return query
