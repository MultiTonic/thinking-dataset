# @file thinking_dataset/db/database.py
# @description Implementation of the Database class.
# @version 1.2.0
# @license MIT

import os
from contextlib import contextmanager
from typing import Optional, List, Any

import pandas as pd
from sqlalchemy import (
    Table,
    MetaData,
    create_engine,
    exc,
    inspect,
    DDL,
    event,
)
from sqlalchemy.exc import NoSuchTableError

import thinking_dataset.config as conf
from thinking_dataset.config.config_keys import ConfigKeys as CK
from thinking_dataset.io.files import Files
from thinking_dataset.utils.execute import execute
from thinking_dataset.utils.log import Log
from .database_session import DatabaseSession as Session
from .models.thoughts import Thoughts
from .operations.fetch import Fetch
from .operations.query import Query


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

    def __init__(self) -> None:
        """Initialize database connection, engine and session."""
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
                    table_id: int,
                    thought_id: int,
                    content: str,
                    table_name: str,
                    cable_id: Optional[int] = None) -> None:
        """
        Add a new thought record to the database.

        Args:
            table_id (int): ID of the source table.
            thought_id (int): Unique identifier for the thought.
            content (str): The actual thought content.
            table_name (str): Name of the source table.
            cable_id (Optional[int]): Optional foreign key to cables table.
        """
        new_thought = Thoughts(table_id=table_id,
                               thought_id=thought_id,
                               content=content,
                               table_name=table_name,
                               cable_id=cable_id)
        with self.get_session() as session:
            session.add(new_thought)
            session.commit()
            Log.info(f"Added new thought with id {new_thought.id}")

    def create_thoughts_table(self) -> None:
        """Create the thoughts table if it doesn't exist."""
        Thoughts.__table__.create(self.engine, checkfirst=True)
        Log.info("Thoughts table created successfully.")

    async def _verify_table_exists(self, session: Any,
                                   table_name: str) -> bool:
        """
        Verify that a table exists in the database.

        Args:
            session (Any): The database session.
            table_name (str): The name of the table to verify.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        try:
            inspector = inspect(session.bind)
            return table_name in inspector.get_table_names()
        except Exception as e:
            Log.error(f"Error verifying table '{table_name}': {str(e)}")
            return False

    async def _ensure_table_exists(self, session: Any,
                                   table_name: str) -> None:
        """
        Ensure the specified table exists, create if missing.

        Args:
            session (Any): The database session.
            table_name (str): The name of the table to ensure.
        """
        try:
            if not await self._verify_table_exists(session, table_name):
                Log.info(f"Table '{table_name}' does not exist, creating it.")

                if table_name == "thoughts":
                    # Verify cables table exists first
                    if not await self._verify_table_exists(session, "cables"):
                        raise RuntimeError("Cannot create thoughts table - "
                                           "cables table missing")

                    self.create_thoughts_table()
                    if not await self._verify_table_exists(
                            session, table_name):
                        raise RuntimeError(
                            f"Failed to create table '{table_name}'")
                    Log.info("Thoughts table created successfully")
                else:
                    # For other tables
                    metadata = MetaData()
                    _ = Table(table_name, metadata, extend_existing=True)
                    await session.run_sync(metadata.create_all,
                                           checkfirst=True)
                    Log.info(f"Created table '{table_name}'")

                # Verify creation
                if not await self._verify_table_exists(session, table_name):
                    raise RuntimeError(
                        f"Table '{table_name}' creation failed verification")

        except NoSuchTableError as e:
            Log.error(
                f"Table '{table_name}' does not exist and could not be created"
            )
            raise RuntimeError(f"Failed to create table: {str(e)}") from e
        except Exception as e:
            Log.error(f"Error ensuring table '{table_name}' exists: {str(e)}")
            raise RuntimeError(f"Table operation failed: {str(e)}") from e

    async def _ensure_column_exists(self, session: Any, table: Table,
                                    column_name: str) -> Table:
        """
        Ensure column exists in table, add if missing.

        Args:
            session (Any): The database session.
            table (Table): The table to check.
            column_name (str): The name of the column to ensure.

        Returns:
            Table: The updated table with the ensured column.
        """
        if column_name not in table.columns:
            Log.info(f"Column '{column_name}' does not exist "
                     f"in table '{table.name}', adding it.")
            ddl = DDL(
                f"ALTER TABLE {table.name} ADD COLUMN {column_name} TEXT")
            event.listen(table, "after_create",
                         ddl.execute_if(dialect="sqlite"))
            session.execute(ddl)
            table = Table(table.name, MetaData(), autoload_with=session.bind)
        return table

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

    def get_thoughts_by_cable_id(self, cable_id: int) -> List[Thoughts]:
        """
        Retrieve all thoughts associated with a cable ID.

        Args:
            cable_id (int): The cable ID to filter thoughts by.

        Returns:
            List[Thoughts]: The list of thoughts associated with the cable ID.
        """
        with self.get_session() as session:
            thoughts = session.query(Thoughts).filter_by(
                cable_id=cable_id).all()
            return thoughts

    def get_thoughts_by_table_id(self, table_id: int,
                                 table_name: str) -> List[Thoughts]:
        """
        Retrieve all thoughts for a specific table ID and name.

        Args:
            table_id (int): The table ID to filter thoughts by.
            table_name (str): The name of the table to filter thoughts by.

        Returns:
            List[Thoughts]: The list of thoughts associated with the
                table ID and name.
        """
        with self.get_session() as session:
            thoughts = session.query(Thoughts).filter_by(
                table_id=table_id, table_name=table_name).all()
            return thoughts

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

    async def ensure_tables_exist(self, session: Any,
                                  table_names: list[str]) -> None:
        """
        Ensure tables exist in correct dependency order.

        Creates tables in the correct order respecting foreign key
        dependencies. Currently handles the cables->thoughts dependency chain.

        Args:
            session (Any): The database session.
            table_names (list[str]): The list of table names to ensure.
        """
        try:
            # Handle known dependencies first
            if "thoughts" in table_names and "cables" in table_names:
                # Always create cables first since thoughts depends on it
                await self._ensure_table_exists(session, "cables")
                if not await self._verify_table_exists(session, "cables"):
                    raise RuntimeError(
                        "Failed to verify cables table creation")

                # Now safe to create thoughts table
                await self._ensure_table_exists(session, "thoughts")

                # Remove from list since we've handled them
                table_names = [
                    t for t in table_names if t not in ("cables", "thoughts")
                ]

            # Create any remaining tables
            for table_name in table_names:
                await self._ensure_table_exists(session, table_name)

        except Exception as e:
            Log.error(f"Failed to create tables in order: {str(e)}")
            raise RuntimeError(
                f"Database setup failed - table creation error: {str(e)}"
            ) from e

    # Private methods
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

    def _set_database_url(self, url: str) -> None:
        """Set the database URL for connections."""
        self.url = url
