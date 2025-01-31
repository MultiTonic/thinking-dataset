"""Response Generation Pipeline Module.

This module provides functionality for asynchronously generating AI responses
from input queries stored in a database using configurable LLM providers.
It supports different response formats including raw text and XML validation.

Classes:
    ResponseGenerationPipe: Handles asynchronous AI response generation with
        optional format validation.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import asyncio
from typing import Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_result,
)

import pandas as pd
from sqlalchemy import update

from thinking_dataset.db.database import Database
from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.providers.ollama_provider import OllamaProvider
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.templates.template_validator import TemplateValidator
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import (
    XMLExtractionError,
    XMLValidationError,
)
from .pipe import Pipe


class ResponseGenerationPipe(Pipe):
    """Handle asynchronous generation of AI responses from input queries.

    This class processes input queries through an AI provider and generates
    responses with optional format validation. Methods are organized
    as follows:
    - Special methods (__init__)
    - Public methods (flow, generate_response)
    - Private methods (_process_queries, _process_query, etc.)
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
        template_path = self.config["response"]["template"]

        # Load template and configurations
        template = TemplateLoader.load(template_path)
        batch_size = self.get_batch_size()
        out_config = self.config["output"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        mock = self.config.get("mock", False)
        format = self.config.get("format", None)
        if format:
            format = format.lower()

        # Get input column from previous pipe
        in_column = next(col for col in df.columns
                         if col not in ['id', out_column])

        # Use parent class's log_df_state with state description
        self.log_df_state(df,
                          state=f"Batch size: {batch_size}, "
                          f"Columns: {in_column}, {out_column}")

        # Initialize output column if it doesn't exist
        if out_column not in df.columns:
            df[out_column] = None

        # Asynchronous process method
        async def process() -> None:
            """Asynchronously process the query generation and response."""
            try:
                provider = OllamaProvider.initialize(self.config, mock=mock)
                await self._process_queries(session, df, provider, out_table,
                                            out_column, in_column, format,
                                            template)
                Log.info("Provider processing completed successfully")
            except Exception as e:
                Log.error(f"Provider processing failed: {str(e)}")
                session.rollback()
                raise e

        # Run the asynchronous process
        asyncio.run(process())

        Log.info("Finished ResponseGenerationPipe")
        return df

    @retry(stop=stop_after_attempt(3),
           wait=wait_fixed(2),
           retry=retry_if_result(lambda x: x is None))
    async def generate_response(self, query: str, provider: OllamaProvider,
                                format: str | None,
                                template: str | None) -> str:
        response = await provider.process_request_async(prompt=query)

        match format:
            case None:
                return response
            case "xml":
                try:
                    content = TemplateValidator._extract_xml_content(
                        response, template)
                    return content
                except (XMLExtractionError, XMLValidationError) as e:
                    raise XMLValidationError(f"XML format error: {str(e)}")
            case _:
                return response

    async def _process_queries(self, session: Any, df: pd.DataFrame,
                               provider: OllamaProvider, out_table: str,
                               out_column: str, in_column: str,
                               format: str | None, template: str | None):
        """Process multiple queries concurrently with controlled concurrency.

        This method coordinates the concurrent processing of multiple queries
        while respecting the max_workers limit through semaphore control.

        Args:
            session (Any): The active database session
            df (pd.DataFrame): DataFrame containing queries to process
            provider (OllamaProvider): The AI provider instance
            out_table (str): Name of the table to update with responses
            out_column (str): Name of the column to store responses
            in_column (str): Name of the column containing input queries
            format (str | None): Response format for validation
            template (str | None): Template for validation

        Raises:
            RuntimeError: If processing any of the queries fails
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
                                                  out_table, out_column,
                                                  format, template)
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
                             out_column: str, format: str | None,
                             template: str | None):
        """Process a single query through the AI pipeline.

        Generates a response and handles database updates with error handling
        and retry logic.

        Args:
            session (Any): The active database session.
            row_id (int): ID of the row to update.
            query (str): The input query string.
            provider (OllamaProvider): The AI provider instance.
            out_table (str): Name of the table to update with the response.
            out_column (str): Name of the column to store the response.
            format (str | None): The format to validate the response.
            template (str | None): The template to validate the response.
        """
        try:
            response = await self.generate_response(query, provider, format,
                                                    template)
            await self._update_db(
                session,
                out_table,
                row_id,
                response,
                out_column,
            )
        except Exception as e:
            Log.warn(
                f"Skipping row {row_id} due to unexpected error: {str(e)}")
            await self._update_db(
                session,
                out_table,
                row_id,
                None,
                out_column,
            )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session: Any, out_table: str, row_id: int,
                         response: str, out_column: str) -> None:
        """Update the database with the generated AI response.

        Updates the specified table and column with retry logic on failure.

        Args:
            session (Any): The active database session
            out_table (str): Name of the table to update
            row_id (int): ID of the row to update
            response (str): The generated AI response to store
            out_column (str): Name of the column to store response

        Raises:
            RuntimeError: If database update fails after retries
            ValueError: If row_id is None
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
