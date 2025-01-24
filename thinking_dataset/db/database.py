# @file thinking_dataset/db/database.py
# @description Implementation of the Database class.
# @version 1.2.0
# @license MIT

import logging
import os
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine, exc

import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as keys
from thinking_dataset.io.files import Files
from thinking_dataset.utils.execute import execute
from thinking_dataset.utils.log import Log
from .database_session import DatabaseSession as Session
from .models.thoughts import Thoughts
from .operations.fetch import Fetch
from .operations.query import Query

CK = keys.ConfigKeys


class Database:
    """
    The Database class handles the initialization and management of the
    database connection, sessions, and CRUD operations for the thoughts table.

    This class:
    1. Initializes the database connection and session.
    2. Creates the necessary database tables.
    3. Provides methods for adding and retrieving thoughts.
    4. Manages database paths and engine configurations.

    Methods:
        __init__(): Initializes the database connection and session.
        _set_database_url(url: str): Sets the database URL.
        _create_database_path(): Creates the database path if it doesn't exist.
        _initialize_engine(): Initializes the database engine.
        _initialize_session(): Initializes the database session.
        create_thoughts_table(): Creates the thoughts table.
        get_session(): Provides a context manager for database sessions.
        query(query: str): Executes a query.
        fetch(query: str): Fetches data based on a query.
        fetch_data(table_name: str): Fetches data from a table as a DataFrame.
        add_thought(table_id, thought_id, content, table_name, cable_id=None):
            Adds a new thought to the database.
        get_thoughts_by_cable_id(cable_id): Retrieves thoughts by cable ID.
        get_thoughts_by_table_id(table_id, table_name): Retrieves thoughts by
            table ID and table name.
    """

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

    # Public methods - CRUD operations
    def add_thought(self,
                    table_id,
                    thought_id,
                    content,
                    table_name,
                    cable_id=None):
        new_thought = Thoughts(table_id=table_id,
                               thought_id=thought_id,
                               content=content,
                               table_name=table_name,
                               cable_id=cable_id)
        with self.get_session() as session:
            session.add(new_thought)
            session.commit()
            Log.info(f"Added new thought with id {new_thought.id}")

    def create_thoughts_table(self):
        Thoughts.__table__.create(self.engine, checkfirst=True)
        Log.info("Thoughts table created successfully.")

    @execute(Fetch)
    def fetch(self, query: str):
        Log.info(f"Fetching data with query: {query}")
        return query

    def fetch_data(self, table_name: str) -> pd.DataFrame:
        try:
            df = pd.read_sql_table(table_name, self.engine)
            Log.info(f"Data fetched from table: {table_name}")
            return df
        except exc.SQLAlchemyError as e:
            raise e

    @contextmanager
    def get_session(self):
        try:
            with self.session.get() as session:
                yield session
                Log.info("Session retrieved successfully.")
        except exc.SQLAlchemyError as e:
            raise e

    def get_thoughts_by_cable_id(self, cable_id):
        with self.get_session() as session:
            thoughts = session.query(Thoughts).filter_by(
                cable_id=cable_id).all()
            return thoughts

    def get_thoughts_by_table_id(self, table_id, table_name):
        with self.get_session() as session:
            thoughts = session.query(Thoughts).filter_by(
                table_id=table_id, table_name=table_name).all()
            return thoughts

    @execute(Query)
    def query(self, query: str):
        Log.info(f"Executing query: {query}")
        return query

    # Private methods
    def _create_database_path(self):
        database_path = os.path.dirname(self.url.split("///")[-1])
        Files.make_dir(database_path)
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

    def _set_database_url(self, url: str):
        self.url = url
