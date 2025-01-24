# @file thinking_dataset/pipeworks/pipes/response_generation_pipe.py
# @description Pipe for generating responses from inspirations.
# @version 1.1.0
# @license MIT

import asyncio
from typing import Any, Optional

import pandas as pd
from sqlalchemy import (
    Table,
    MetaData,
    select,
    update,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
)

from .pipe import Pipe
from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.providers.ollama_provider import OllamaProvider
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database


class ResponseGenerationPipe(Pipe):
    """
    The ResponseGenerationPipe class handles the asynchronous generation
    of AI responses based on input queries from the database.

    This class:
    1. Fetches queries from specified database table/column
    2. Processes queries asynchronously through configured AI provider
    3. Updates database with generated responses
    4. Manages column creation and validation

    Methods:
        __init__(config): Initializes the pipe with configuration.
        flow(df, session): Main pipeline execution flow.
        _fetch_queries(session, table_name, in_column): Fetches queries
            from DB.
        _update_db(session, out_table, row_id, response, out_column):
            Updates DB.
        _generate_response(query, provider): Generates AI response.
        _process_queries(session, queries, provider, out_table, out_column):
            Process multiple queries concurrently.
        _process_single_query(session, row, provider, out_table, out_column):
            Process a single query through the AI provider.

    Config:
        input (list): Source table and column config for queries
        output (list): Target table and column config for responses
        provider (str): AI provider configuration
        if_exists (str): How to handle existing output table
        prompt (dict): Template configuration for responses
        max_workers (int): Maximum concurrent requests (default: 4)
    """

    def __init__(self, config: dict) -> None:
        """Initialize pipe with configuration settings."""
        super().__init__(config)
        self.max_workers = self.config.get("max_workers", 4)
        self.db = Database()  # Create single Database instance

    @with_db_session
    def flow(self,
             df: pd.DataFrame,
             session: Optional[Any] = None,
             **kwargs) -> pd.DataFrame:
        """
        Execute the main pipeline flow for response generation.

        Args:
            df (pd.DataFrame): Input DataFrame.
            session (Optional[Any]): Database session.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame: Output DataFrame with generated responses.
        """
        Log.info("Starting ResponseGenerationPipe")
        Log.info(f"Using max_workers: {self.max_workers}")

        in_config = self.config["input"][0]
        out_config = self.config["output"][0]
        in_table = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        mock = self.config.get("mock", False)

        async def process() -> None:
            try:
                queries = self._fetch_queries(session, in_table, in_column)
                provider = OllamaProvider.initialize(self.config, mock=mock)
                await self._process_queries(session, queries, provider,
                                            out_table, out_column, in_column)
            except Exception as e:
                session.rollback()
                raise e

        asyncio.run(process())
        Log.info("Finished ResponseGenerationPipe")
        return df

    # Database operations
    async def _ensure_column_exists(self, session: Any, table: Table,
                                    out_column: str) -> Table:
        """
        Ensure column exists in table, add if missing.

        Args:
            session (Any): The database session.
            table (Table): The table to check.
            out_column (str): The name of the column to ensure.

        Returns:
            Table: The updated table with the ensured column.
        """
        return await self.db._ensure_column_exists(session, table, out_column)

    def _fetch_queries(self, session, table_name: str,
                       in_column: str) -> pd.DataFrame:
        """
        Fetch input queries from database table.

        Args:
            session (Any): The database session.
            table_name (str): The name of the table to fetch queries from.
            in_column (str): The name of the column to fetch queries from.

        Returns:
            pd.DataFrame: DataFrame containing the fetched queries.
        """
        table = Table(table_name, MetaData(), autoload_with=session.bind)

        query = select(table.c.id, table.c[in_column])
        result = session.execute(query)
        rows = result.fetchall()

        queries = pd.DataFrame(rows, columns=['id', in_column])
        Log.info(f"Total Queries in {table_name}.{in_column}: {len(queries)}")
        return queries

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session: Any, out_table: str, row_id: int,
                         response: str, out_column: str) -> None:
        """
        Update database with generated response with retry logic.

        Args:
            session (Any): The database session.
            out_table (str): The name of the output table.
            row_id (int): The ID of the row to update.
            response (str): The generated response.
            out_column (str): The name of the output column.
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
        """
        Generate AI response for input query.

        Args:
            query (str): The input query.
            provider (OllamaProvider): The AI provider.

        Returns:
            str: The generated AI response.
        """
        return await provider.process_request_async(prompt=query)

    async def _process_queries(self, session, queries, provider, out_table,
                               out_column, in_column):
        """
        Process multiple queries concurrently with semaphore control.

        Args:
            session (Any): The database session.
            queries (pd.DataFrame): DataFrame containing the queries.
            provider (OllamaProvider): The AI provider.
            out_table (str): The name of the output table.
            out_column (str): The name of the output column.
            in_column (str): The name of the input column.
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
            Log.error(f"Query batch processing failed: {str(e)}")
            raise RuntimeError("Failed to process query batch") from e

    async def _process_single_query(self, session, row, provider, out_table,
                                    out_column, in_column):
        """
        Process a single query through the AI pipeline.

        Args:
            session (Any): The database session.
            row (pd.Series): The row containing the query.
            provider (OllamaProvider): The AI provider.
            out_table (str): The name of the output table.
            out_column (str): The name of the output column.
            in_column (str): The name of the input column.
        """
        response = await self._generate_response(row[in_column], provider)
        await self._update_db(
            session,
            out_table,
            row['id'],
            response,
            out_column,
        )
