"""Response Generation Pipeline Module.

This module provides functionality for asynchronously generating AI responses
from input queries stored in a database using configurable LLM providers.

Functions:
    None

Classes:
    ResponseGenerationPipe: Handles asynchronous AI response generation.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

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


class ResponseGenerationPipe(Pipe):
    """Handle asynchronous generation of AI responses from input queries.

    This class manages the flow of fetching queries from the database,
    generating responses using an AI provider, and updating the database with
    the generated responses.

    Attributes:
        max_workers (int): Maximum number of concurrent AI requests.
        db (Database): Instance for database interactions.
    """

    def __init__(self, config: dict) -> None:
        """Initialize the ResponseGenerationPipe with configuration settings.

        Args:
            config (dict): Configuration dictionary containing pipe settings.
        """
        super().__init__(config)
        self.max_workers = self.config.get("max_workers", 4)
        self.db = Database()

    @with_db_session
    def flow(self,
             df: pd.DataFrame,
             session: Any = None,
             **kwargs) -> pd.DataFrame:
        """Execute the main pipeline flow for response generation.

        This method orchestrates the fetching of queries, generation of
        responses, and updating the database with the generated responses.

        Args:
            df (pd.DataFrame): Input DataFrame containing initial data.
            session (Any, optional): Database session object. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame: The updated DataFrame after processing.
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
            """Asynchronously process the query generation and response."""
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

    async def generate_response(self, query: str,
                                provider: OllamaProvider) -> str:
        """Generate an AI response for a given input query.

        This method sends the input query to the AI provider and awaits
        the response.

        Args:
            query (str): The input query string.
            provider (OllamaProvider): The AI provider instance to generate
                responses.

        Returns:
            str: The generated AI response.
        """
        return await provider.process_request_async(prompt=query)

    def _fetch_queries(self, session: Any, table_name: str, in_column: str,
                       batch_size: int) -> pd.DataFrame:
        """Fetch a batch of input queries from the specified database table.

        Args:
            session (Any): The active database session.
            table_name (str): Name of the table to fetch queries from.
            in_column (str): Name of the column containing input queries.
            batch_size (int): Number of queries to fetch in a batch.

        Returns:
            pd.DataFrame: DataFrame containing fetched queries.
        """
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        query = select(table.c.id, table.c[in_column]).limit(batch_size)
        result = session.execute(query)
        rows = result.fetchall()

        queries = pd.DataFrame(rows, columns=['id', in_column])
        Log.info(
            f"Fetched {len(queries)} queries from {table_name}.{in_column}")
        return queries

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session: Any, out_table: str, row_id: int,
                         response: str, out_column: str) -> None:
        """Update the database with the generated AI response with retry logic.

        This method ensures the output table and column exist before updating
        the row. If the update fails, it retries up to 3 times with a fixed
        wait time.

        Args:
            session (Any): The active database session.
            out_table (str): Name of the table to update.
            row_id (int): ID of the row to update.
            response (str): The generated AI response to store.
            out_column (str): Name of the column to store the response.

        Raises:
            RuntimeError: If the database update fails after retries.
        """
        try:
            table = await self.db.ensure_table_exists(session, out_table)
            table = await self.db.ensure_column_exists(session, table,
                                                       out_column)
            stmt = (update(table).where(table.c.id == row_id).values(
                {out_column: response}))

            session.execute(stmt)
            session.commit()
            Log.info(f"Updated row with id {row_id} in '{out_table}' table")

        except Exception as e:
            Log.error(f"Database update failed: {str(e)}")
            if session:
                session.rollback()
            raise RuntimeError(f"Failed to update database: {str(e)}") from e

    async def _process_queries(self, session: Any, queries: pd.DataFrame,
                               provider: OllamaProvider, out_table: str,
                               out_column: str, in_column: str):
        """Process multiple queries concurrently with controlled concurrency.

        This method leverages asyncio's Semaphore to limit the number of
        concurrent AI requests based on the `max_workers` configuration.

        Args:
            session (Any): The active database session.
            queries (pd.DataFrame): DataFrame containing queries to process.
            provider (OllamaProvider): The AI provider instance.
            out_table (str): Name of the table to update with responses.
            out_column (str): Name of the column to store responses.
            in_column (str): Name of the column containing input queries.

        Raises:
            RuntimeError: If processing any of the queries fails.
        """
        try:
            semaphore = asyncio.Semaphore(self.max_workers)

            async def _process_semaphore(row: pd.Series):
                """Process a single query within the semaphore context."""
                try:
                    async with semaphore:
                        await self._process_query(session, row, provider,
                                                  out_table, out_column,
                                                  in_column)
                except Exception as e:
                    Log.error(f"Query processing failed: {str(e)}")
                    raise

            tasks = [_process_semaphore(row) for _, row in queries.iterrows()]
            await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as e:
            raise RuntimeError("Failed to process query batch") from e

    async def _process_query(self, session: Any, row: pd.Series,
                             provider: OllamaProvider, out_table: str,
                             out_column: str, in_column: str):
        """Process a single query through the AI pipeline.

        This method generates a response for the input query and updates the
        corresponding database record with the generated response.

        Args:
            session (Any): The active database session.
            row (pd.Series): A row in the DataFrame containing a query.
            provider (OllamaProvider): The AI provider instance.
            out_table (str): Name of the table to update with the response.
            out_column (str): Name of the column to store the response.
            in_column (str): Name of the column containing the input query.
        """
        response = await self.generate_response(row[in_column], provider)
        await self._update_db(
            session,
            out_table,
            row['id'],
            response,
            out_column,
        )
