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
from sqlalchemy import update
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
        """
        Execute the main pipeline flow for response generation.
        Parameters

        df : pd.DataFrame
            The input DataFrame containing data to be processed.
        session : Any, optional
            The database session to be used for database operations,
            by default None.
        **kwargs : dict
            Additional keyword arguments.

        Returns:
            pd.DataFrame: The DataFrame with the response generation results.

        Raises:
            Exception: If the provider processing fails.

        Notes:
            This method initializes the output column if it doesn't exist,
            logs the current DataFrame state, and processes the query
            generation and response asynchronously.
        """
        Log.info("Starting ResponseGenerationPipe")
        Log.info(f"Using max_workers: {self.max_workers}")

        # Get configurations
        batch_size = self.get_batch_size()
        out_config = self.config["output"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        mock = self.config.get("mock", False)

        # Get input column from previous pipe
        in_column = next(col for col in df.columns
                         if col not in ['id', out_column])

        # Logs the current DataFrame state
        self.log_df_state(df, batch_size, in_column, out_column)

        # Initialize output column if it doesn't exist
        if out_column not in df.columns:
            df[out_column] = None

        async def process() -> None:
            """Asynchronously process the query generation and response."""
            try:
                provider = OllamaProvider.initialize(self.config, mock=mock)
                await self._process_queries(session, df, provider, out_table,
                                            out_column, in_column)
                Log.info("Provider processing completed successfully")
            except Exception as e:
                Log.error(f"Provider processing failed: {str(e)}")
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
            provider (OllamaProvider): The AI provider instance to
                generate responses.

        Returns:
            str: The generated AI response.
        """
        return await provider.process_request_async(prompt=query)

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
            if row_id is None:
                raise ValueError("Row ID cannot be None")

            table = await self.db.ensure_table_exists(session, out_table)
            table = await self.db.ensure_column_exists(session, table,
                                                       out_column)
            stmt = (update(table).where(table.c.id == row_id).values(
                {out_column: response}))

            Log.info(f"Updating DB - ID: {row_id}, "
                     f"Table: {out_table}, "
                     f"Column: {out_column}")

            session.execute(stmt)
            session.commit()
            Log.info(f"Updated row with id {row_id} in '{out_table}' table")

        except Exception as e:
            Log.error(f"Database update failed: {str(e)}")
            if session:
                session.rollback()
            raise RuntimeError(f"Failed to update database: {str(e)}") from e

    async def _process_queries(self, session: Any, df: pd.DataFrame,
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
                """
                Process a single query within the semaphore context.
                This function processes a single row from a pandas DataFrame
                within the context of a semaphore to control concurrency. It
                checks for valid row ID and query, logs the processing steps,
                and calls another function to handle the actual
                query processing.

                Args:
                    row (pd.Series): A pandas Series object representing a
                        row from a DataFrame.
                Raises:
                    Exception: If query processing fails, an exception is
                        logged and re-raised.
                """
                try:
                    async with semaphore:
                        row_id = row.at['id']
                        query = row.at[in_column]

                        # Skip if no ID or empty/null query
                        if pd.isna(row_id) or pd.isna(query) or str(
                                query).strip() == '':
                            Log.warn(
                                f"Skipping row - ID: {row_id}, Query: {query}")
                            return

                        # Process valid query
                        Log.info(f"Processing row - ID: {row_id}, "
                                 f"Query length: {len(str(query))}")
                        await self._process_query(session, int(row_id),
                                                  str(query), provider,
                                                  out_table, out_column)
                except Exception as e:
                    Log.error(f"Query processing failed: {str(e)}")
                    raise

            tasks = [_process_semaphore(row) for _, row in df.iterrows()]
            await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as e:
            raise RuntimeError(
                f"Failed to process query batch: {str(e)}") from e

    async def _process_query(self, session: Any, row_id: int, query: str,
                             provider: OllamaProvider, out_table: str,
                             out_column: str):
        """Process a single query through the AI pipeline.

        This method generates a response for the input query and updates the
        corresponding database record with the generated response.

        Args:
            session (Any): The active database session.
            row_id (int): ID of the row to update.
            query (str): The input query string.
            provider (OllamaProvider): The AI provider instance.
            out_table (str): Name of the table to update with the response.
            out_column (str): Name of the column to store the response.
        """
        response = await self.generate_response(query, provider)
        await self._update_db(
            session,
            out_table,
            row_id,
            response,
            out_column,
        )

    def log_df_state(self, df: pd.DataFrame, batch_size: int, in_column: str,
                     out_column: str) -> None:
        """Log the state of the DataFrame before processing.

            Args:
                df (pd.DataFrame): The DataFrame to log.
                batch_size (int): The size of the batch to process.
                in_column (str): The input column name.
                out_column (str): The output column name.
            """
        Log.info(f"DataFrame shape: {df.shape}")
        Log.info(f"Batch size: {batch_size}")
        Log.info(f"Input column: {in_column}")
        Log.info(f"Output column: {out_column}")
