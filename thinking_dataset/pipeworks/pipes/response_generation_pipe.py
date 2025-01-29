"""Response Generation Pipeline Module.

This module provides functionality for asynchronously generating AI responses
from input queries stored in a database using configurable LLM providers.

Functions:
    None

Classes:
    ResponseGenerationPipe: Handles asynchronous AI response generation.
"""

import asyncio
from typing import Any

import pandas as pd
from sqlalchemy import (
    MetaData,
    Table,
    select,
    update,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
)

from thinking_dataset.db.database import Database
from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.providers.ollama_provider import OllamaProvider
from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class ResponseGenerationPipe(Pipe):
    """Handle asynchronous generation of AI responses from input queries.

    This class manages:
    1. Fetching queries from specified database table/column
    2. Processing queries asynchronously through configured AI provider
    3. Updating database with generated responses
    4. Managing column creation and validation

    Attributes:
        max_workers (int): Maximum concurrent requests
        db (Database): Database connection instance
    """

    def __init__(self, config: dict) -> None:
        """Initialize pipe with configuration settings.

        Args:
            config (dict): Configuration dictionary containing:
                max_workers (int): Maximum concurrent requests
                input (list): Source table and column configuration
                output (list): Target table and column configuration
                mock (bool): Whether to use mock responses
        """
        super().__init__(config)
        self.max_workers = self.config.get("max_workers", 4)
        self.db = Database()  # Initialize database connection

    @with_db_session
    def flow(self,
             df: pd.DataFrame,
             session: Any = None,
             **kwargs) -> pd.DataFrame:
        """Execute the main pipeline flow for response generation.

        Args:
            df (pd.DataFrame): Input DataFrame
            session: Database session
            **kwargs: Additional arguments including pipeline_config

        Returns:
            pd.DataFrame: DataFrame with generated responses
        """
        Log.info("Starting ResponseGenerationPipe")
        Log.info(f"Using max_workers: {self.max_workers}")

        # Get configurations
        batch_size = self.get_batch_size()
        in_config = self.config["input"][0]
        out_config = self.config["output"][0]
        in_table = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        mock = self.config.get("mock", False)

        Log.info(f"Using batch_size: {batch_size}")

        async def process() -> None:
            try:
                queries = self._fetch_queries(session, in_table, in_column,
                                              batch_size)
                provider = OllamaProvider.initialize(self.config, mock=mock)
                await self._process_queries(session, queries, provider,
                                            out_table, out_column, in_column)
            except Exception as e:
                session.rollback()
                raise e

        asyncio.run(process())
        Log.info("Finished ResponseGenerationPipe")
        return df

    # Database utility methods
    def _fetch_queries(self, session: Any, table_name: str, in_column: str,
                       batch_size: int) -> pd.DataFrame:
        """Fetch batch of input queries from database table.

        Args:
            session: Database session
            table_name (str): Name of the table to fetch queries from
            in_column (str): Name of the column containing queries
            batch_size (int): Number of queries to fetch

        Returns:
            pd.DataFrame: DataFrame containing the fetched queries with IDs
        """
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        query = select(table.c.id, table.c[in_column]).limit(batch_size)
        result = session.execute(query)
        rows = result.fetchall()

        queries = pd.DataFrame(rows, columns=['id', in_column])
        Log.info(
            f"Fetched {len(queries)} queries from {table_name}.{in_column}")
        return queries

    # Async database operations
    async def _ensure_column_exists(self, session: Any, table: Table,
                                    out_column: str) -> Table:
        """Ensure output column exists in table, create if missing.

        Args:
            session: Database session
            table (Table): SQLAlchemy table object to check
            out_column (str): Name of column to ensure exists

        Returns:
            Table: Updated table with ensured column

        Raises:
            RuntimeError: If column creation fails
        """
        return await self.db._ensure_column_exists(session, table, out_column)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session: Any, out_table: str, row_id: int,
                         response: str, out_column: str) -> None:
        """Update database with generated response with retry logic.

        Args:
            session: Database session
            out_table (str): Name of table to update
            row_id (int): ID of row to update
            response (str): Generated AI response text
            out_column (str): Name of column to update

        Raises:
            RuntimeError: If database update fails after retries
        """
        try:
            # Create all required tables in correct order
            await self.db.ensure_tables_exist(session, ["cables", "thoughts"])

            # Rest of the update logic
            table = Table(out_table, MetaData(), autoload_with=session.bind)
            Log.info(f"Updating table '{out_table}' row {row_id}")

            table = await self.db._ensure_column_exists(
                session, table, out_column)
            stmt = update(table).where(table.c.id == row_id).values(
                {out_column: response})

            session.execute(stmt)
            session.commit()
            Log.info(f"Updated row with id {row_id} in '{out_table}' table")

        except Exception as e:
            Log.error(f"Database update failed: {str(e)}")
            if session:
                session.rollback()
            raise RuntimeError(f"Failed to update database: {str(e)}") from e

    # Processing operations
    async def _generate_response(self, query: str,
                                 provider: OllamaProvider) -> str:
        """Generate AI response for a given input query.

        Args:
            query (str): Input query text to process
            provider (OllamaProvider): Configured AI provider instance

        Returns:
            str: Generated AI response text
        """
        return await provider.process_request_async(prompt=query)

    async def _process_queries(self, session, queries, provider, out_table,
                               out_column, in_column):
        """Process multiple queries concurrently with controlled concurrency.

        Args:
            session: Database session
            queries (pd.DataFrame): DataFrame containing queries to process
            provider (OllamaProvider): Configured AI provider instance
            out_table (str): Name of output table
            out_column (str): Name of output column
            in_column (str): Name of input column

        Raises:
            RuntimeError: If batch processing fails
        """
        try:
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = []

            async def process_with_semaphore(row):
                try:
                    async with semaphore:
                        return await self._process_single_query(
                            session, row, provider, out_table, out_column,
                            in_column)
                except Exception as e:
                    Log.error(f"Query processing failed: {str(e)}")
                    raise

            tasks = [
                process_with_semaphore(row) for _, row in queries.iterrows()
            ]
            await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as e:
            raise RuntimeError("Failed to process query batch") from e

    async def _process_single_query(self, session, row, provider, out_table,
                                    out_column, in_column):
        """Process a single query through the AI pipeline.

        Args:
            session: Database session
            row (pd.Series): Row containing query data
            provider (OllamaProvider): Configured AI provider instance
            out_table (str): Name of output table
            out_column (str): Name of output column
            in_column (str): Name of input column

        Raises:
            RuntimeError: If query processing fails
        """
        response = await self._generate_response(row[in_column], provider)
        await self._update_db(
            session,
            out_table,
            row['id'],
            response,
            out_column,
        )
