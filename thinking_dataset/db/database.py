# @file thinking_dataset/db/database.py
# @description Implementation of the Database class.
# @version 1.1.3
# @license MIT

import os
import sys
import pandas as pd
import thinking_dataset.config as conf
from sqlalchemy import create_engine, exc
from contextlib import contextmanager
from thinking_dataset.utils.execute import execute
from .operations.query import Query
from .operations.fetch import Fetch
from .database_session import DatabaseSession as Session
from thinking_dataset.utils.log import Log


class Database:

    def __init__(self):
        config_instance = conf.initialize()
        self.config = config_instance
        try:
            database_url = self.config.database_url.format(
                name=self.config.database_name)
            self._set_database_url(database_url)
            Log.info(f"Database URL: {self.url}")

            self._create_database_path()
            self._initialize_engine()
            self._initialize_session()
            Log.info("Database initialized successfully.")
        except exc.SQLAlchemyError as e:
            Log.error(f"Error initializing the Database class: {e}",
                      exc_info=True)
            sys.exit(1)

    def _set_database_url(self, url: str):
        self.url = url

    def _create_database_path(self):
        database_path = os.path.dirname(self.url.split("///")[-1])
        os.makedirs(database_path, exist_ok=True)
        Log.info(f"Database path {database_path} created successfully.")

    def _initialize_engine(self):
        self.engine = create_engine(
            self.url,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            connect_args={'timeout': self.config.connect_timeout},
            echo=self.config.log_queries)

        Log.info("Database engine created successfully.")

    def _initialize_session(self):
        self.session = Session(self.engine)
        Log.info("Session initialized successfully.")

    @contextmanager
    def get_session(self):
        try:
            with self.session.get() as session:
                yield session
                Log.info("Session retrieved successfully.")
        except exc.SQLAlchemyError as e:
            Log.error(f"Error retrieving the session: {e}", exc_info=True)

    @execute(Query)
    def query(self, query: str):
        Log.info(f"Executing query: {query}")
        return query

    @execute(Fetch)
    def fetch(self, query: str):
        Log.info(f"Fetching data with query: {query}")
        return query

    def fetch_data(self, table_name: str) -> pd.DataFrame:
        """
        Fetch data from the database and return it as a DataFrame.
        """
        try:
            df = pd.read_sql_table(table_name, self.engine)
            Log.info(f"Data fetched from table: {table_name}")
            return df
        except exc.SQLAlchemyError as e:
            Log.error(f"Error fetching data from table {table_name}: {e}",
                      exc_info=True)
            raise
