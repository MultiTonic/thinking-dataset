# @file thinking_dataset/db/database.py
# @description Implementation of the Database class.
# @version 1.1.7
# @license MIT

import os
import pandas as pd
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as keys
from sqlalchemy import create_engine, exc
from contextlib import contextmanager
from thinking_dataset.utils.execute import execute
from .operations.query import Query
from .operations.fetch import Fetch
from .database_session import DatabaseSession as Session
from thinking_dataset.utils.log import Log
import logging

CK = keys.ConfigKeys


class Database:

    def __init__(self):
        try:
            conf.initialize()
            database_url = conf.get_value(
                CK.DATABASE_URL).format(name=conf.get_value(CK.DATABASE_NAME))
            self._set_database_url(database_url)

            self._create_database_path()
            self._initialize_engine()
            self._initialize_session()
        except exc.SQLAlchemyError as e:
            raise e

    def _set_database_url(self, url: str):
        self.url = url

    def _create_database_path(self):
        database_path = os.path.dirname(self.url.split("///")[-1])
        os.makedirs(database_path, exist_ok=True)
        Log.info(f"Database path {database_path} created successfully.")

    def _initialize_engine(self):
        self.engine = create_engine(
            self.url,
            pool_size=conf.get_value(CK.POOL_SIZE),
            max_overflow=conf.get_value(CK.MAX_OVERFLOW),
            connect_args={'timeout': conf.get_value(CK.CONNECT_TIMEOUT)},
            echo=False,
            logging_name="database")

        logging.getLogger("sqlalchemy.engine.Engine.database").setLevel(
            logging.CRITICAL)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.dialects").setLevel(logging.CRITICAL)

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
            raise e

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
            raise e
