"""
Database Module.

This module provides the implementation of the Database class for managing
database connections and operations.

Classes:
    Database: Handles the initialization and management of the database
        connection and sessions.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import os
from contextlib import contextmanager
from typing import Any

import pandas as pd
from sqlalchemy import (
    Table,
    MetaData,
    create_engine,
    exc,
    Column,
    String,
    inspect,
    text,
)

import thinking_dataset.config as conf
from thinking_dataset.config.config_keys import ConfigKeys as CK
from thinking_dataset.io.files import Files
from thinking_dataset.utils.execute import execute
from thinking_dataset.utils.log import Log
from .database_session import DatabaseSession as Session
from .operations.fetch import Fetch
from .operations.query import Query


class Database:
    """
    The Database class handles the initialization and management of the
    database connection and sessions.

    This class:
    1. Initializes the database connection and session.
    2. Creates the necessary database tables.
    3. Manages database paths and engine configurations.

    Methods:
        __init__(): Initializes the database connection and session.
        _set_database_url(url: str): Sets the database URL.
        _create_database_path(): Creates the database path if it doesn't exist.
        _initialize_engine(): Initializes the database engine.
        _initialize_session(): Initializes the database session.
        get_session(): Provides a context manager for database sessions.
        query(query: str): Executes a query.
        fetch(query: str): Fetches data based on a query.
        fetch_data(table_name: str): Fetches data from a table as a DataFrame.
        ensure_table_exists(session: Any, table_name: str): Ensures that a
            table exists, creating it if missing.
        ensure_column_exists(session: Any, table: Table, column_name: str):
            Ensures that a column exists in a table, adding it if missing.
    """

    def __init__(self) -> None:
        """Initialize database connection, engine, and session."""
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

    def _set_database_url(self, url: str) -> None:
        """
        Set the database URL for connections.

        Args:
            url (str): The database URL.
        """
        self.url = url

    def _create_database_path(self) -> None:
        """Create database directory path if it doesn't exist."""
        database_path = os.path.dirname(self.url.split("///")[-1])
        Files.make_dir(database_path)
        Log.info(f"Database path {database_path} created successfully.")

    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with configuration."""
        self.engine = create_engine(
            self.url,
            pool_size=conf.get_value(CK.POOL_SIZE),
            max_overflow=conf.get_value(CK.MAX_OVERFLOW),
            connect_args={"timeout": conf.get_value(CK.CONNECT_TIMEOUT)},
            echo=False,
            logging_name="database")

        Log.configure_sqlalchemy_logging()
        Log.info("Database engine created successfully.")

    def _initialize_session(self) -> None:
        """Initialize SQLAlchemy session factory."""
        self.session = Session(self.engine)
        Log.info("Session initialized successfully.")

    @contextmanager
    def get_session(self) -> Any:
        """
        Get a database session context manager.

        Yields:
            Any: The database session.
        """
        try:
            with self.session.get() as session:
                yield session
                Log.info("Session retrieved successfully.")
        except exc.SQLAlchemyError as e:
            raise e

    @execute(Query)
    def query(self, query: str) -> Any:
        """
        Execute a query on the database.

        Args:
            query (str): The query to execute.

        Returns:
            Any: The query results.
        """
        Log.info(f"Executing query: {query}")
        return query

    @execute(Fetch)
    def fetch(self, query: str) -> Any:
        """
        Execute a fetch query and return results.

        Args:
            query (str): The query to execute.

        Returns:
            Any: The fetched results.
        """
        Log.info(f"Fetching data with query: {query}")
        return query

    def fetch_data(self, table_name: str) -> pd.DataFrame:
        """
        Fetch all data from table as DataFrame.

        Args:
            table_name (str): The name of the table to fetch data from.

        Returns:
            pd.DataFrame: The fetched data as a DataFrame.
        """
        try:
            df = pd.read_sql_table(table_name, self.engine)
            Log.info(f"Data fetched from table: {table_name}")
            return df
        except exc.SQLAlchemyError as e:
            raise e

    async def ensure_table_exists(self, session: Any,
                                  table_name: str) -> Table:
        """
        Ensure a table exists in the database; create it if missing.

        Args:
            session (Any): The database session.
            table_name (str): The name of the table to ensure exists.

        Returns:
            Table: The SQLAlchemy table object.
        """
        inspector = inspect(session.bind)
        if not inspector.has_table(table_name):
            Log.info(f"Table '{table_name}' does not exist, creating it.")
            metadata = MetaData()
            table = Table(
                table_name,
                metadata,
                Column('id', String, primary_key=True),
            )
            metadata.create_all(session.bind)
            Log.info(f"Table '{table_name}' created successfully.")
        else:
            table = Table(table_name, MetaData(), autoload_with=session.bind)
        return table

    async def ensure_column_exists(self, session: Any, table: Table,
                                   column_name: str) -> Table:
        """
        Ensure a column exists in the specified table; add it if missing.

        Args:
            session (Any): The database session.
            table (Table): The SQLAlchemy table object.
            column_name (str): The name of the column to ensure exists.

        Returns:
            Table: The updated table with the ensured column.

        Raises:
            RuntimeError: If column creation fails.
        """
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table.name)
        column_names = [column['name'] for column in columns]
        if column_name not in column_names:
            Log.info(f"Column '{column_name}' does not exist "
                     f"in table '{table.name}', adding it.")
            alter_stmt = text(
                f"ALTER TABLE {table.name} ADD COLUMN {column_name} TEXT")
            try:
                session.execute(alter_stmt)
                session.commit()
                Log.info(
                    f"Column '{column_name}' added to table '{table.name}'.")
                table = Table(table.name,
                              MetaData(),
                              autoload_with=session.bind)
            except exc.SQLAlchemyError as e:
                Log.error(f"Failed to add column '{column_name}' "
                          f"to table '{table.name}': {e}")
                session.rollback()
                raise RuntimeError(f"Failed to add column '{column_name}' "
                                   f"to table '{table.name}': {e}") from e
        return table
