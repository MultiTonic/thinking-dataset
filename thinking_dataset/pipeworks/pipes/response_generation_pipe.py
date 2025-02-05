"""Response Generation Pipeline Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import time
import asyncio
from typing import Any
from tenacity import (
    retry,
    wait_fixed,
    stop_after_attempt,
    retry_if_exception_type,
)

import pandas as pd
from sqlalchemy import update

from thinking_dataset.db.database import Database
from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.providers.ollama_provider import OllamaProvider
from thinking_dataset.templates.response_validator import ResponseValidator
from thinking_dataset.templates.template_extractor import TemplateExtractor
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import (
    XMLExtractionError,
    XMLValidationError,
    XMLLengthError,
)
from .pipe import Pipe


class ResponseGenerationPipe(Pipe):
    """Handle asynchronous generation of AI responses from input queries."""

    def __init__(self, config: dict) -> None:
        """Initialize ResponseGenerationPipe with configuration settings."""
        super().__init__(config)
        self.max_workers = self.config.get("max_workers", 4)
        self.template_path = self.config.get("template", None)
        self.db = Database()

    @with_db_session
    def flow(
        self,
        df: pd.DataFrame,
        session: Any = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Execute the main pipeline flow for response generation."""
        Log.info("Starting ResponseGenerationPipe")
        Log.info(f"Using max_workers: {self.max_workers}")
        Log.info(f"Using template: {self.template_path}")

        # Load template and configurations
        template = TemplateLoader.load(self.template_path)
        batch_size = self.get_batch_size()
        out_config = self.config["output"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        mock = self.config.get("mock", False)
        min_length = self.config.get("min_length", 0)

        # Get format configuration
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

        # Call the local async process method
        asyncio.run(
            self._run_async_process(session, df, out_table, out_column,
                                    in_column, format, template, mock,
                                    min_length))

        Log.info("Finished ResponseGenerationPipe")
        return df

    async def _run_async_process(
        self,
        session: Any,
        df: pd.DataFrame,
        out_table: str,
        out_column: str,
        in_column: str,
        format: str | None,
        template: str | None,
        mock: bool,
        min_length: int,
    ) -> None:
        """Asynchronously process the query generation and response."""
        try:
            provider = OllamaProvider.initialize(self.config, mock=mock)
            await self._process_queries(session, df, provider, out_table,
                                        out_column, in_column, format,
                                        template, min_length)
            Log.info("Provider processing completed successfully")
        except Exception as e:
            Log.error(f"Provider processing failed: {str(e)}")
            session.rollback()
            raise e

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    async def generate_response(
        self,
        query: str,
        provider: OllamaProvider,
        format: str | None,
        template: str | None,
        min_length: int = 0,
    ) -> str:
        response = await provider.process_request_async(prompt=query)
        response = self._format_response(response, template, format,
                                         min_length)
        return response

    def _validate_response_length(self, response: str,
                                  min_length: int) -> None:
        """Validate response meets minimum length requirement if specified."""
        if min_length > 0 and len(response) < min_length:
            raise XMLLengthError(f"Response length {len(response)} is "
                                 f"below minimum {min_length}")

    def _format_response(
        self,
        response: str,
        template: str | None,
        format: str | None,
        min_length: int = 0,
    ) -> str:
        """Format the response according to the specified format."""
        match format:
            case None:
                return response
            case "xml":
                try:
                    self._validate_response_length(response, min_length)
                    required_elements = \
                        TemplateExtractor.extract_required_elements(
                            template)
                    response_formatted = \
                        ResponseValidator.extract_xml_content(
                            response, required_elements)
                    return response_formatted
                except (XMLExtractionError, XMLValidationError,
                        XMLLengthError) as e:
                    raise XMLValidationError(f"XML format error: {str(e)}")
            case _:
                return response

    async def _process_queries(
        self,
        session: Any,
        df: pd.DataFrame,
        provider: OllamaProvider,
        out_table: str,
        out_column: str,
        in_column: str,
        format: str | None,
        template: str | None,
        min_length: int,
    ):
        """Process queries concurrently with controlled concurrency."""
        try:
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = [
                self._handle_process(row, semaphore, session, provider,
                                     out_table, out_column, in_column, format,
                                     template, min_length)
                for _, row in df.iterrows()
            ]
            await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as e:
            raise RuntimeError(
                f"Failed to process query batch: {str(e)}") from e

    def _log_metrics(
        self,
        row_id: int,
        duration: float,
        query: str | None = None,
        response: str | None = None,
        error: Exception | None = None,
    ) -> None:
        """Log processing metrics and results."""
        if error:
            Log.warn(f"Failed -- ID: {row_id} in "
                     f"{duration:.2f} sec | Error: {str(error)}")
            return

        if not response:
            Log.info(f"Completed -- ID: {row_id} in {duration:.2f} sec | "
                     "No response generated")
            return

        output_tokens = len(response) / 4
        input_tokens = len(query or "") / 4
        avg_tokens_per_sec = (
            (input_tokens + output_tokens) / 2) / duration if duration else 0

        Log.info(f"Completed -- ID: {row_id} in {duration:.2f} sec | "
                 f"Input: {input_tokens:.2f} tk | "
                 f"Output: {output_tokens:.2f} tk | "
                 f"Speed: {avg_tokens_per_sec:.2f} tk/sec")

    async def _handle_process(
        self,
        row: pd.Series,
        semaphore: asyncio.Semaphore,
        session: Any,
        provider: OllamaProvider,
        out_table: str,
        out_column: str,
        in_column: str,
        format: str | None,
        template: str | None,
        min_length: int,
    ) -> None:
        """Process a single row with metrics tracking."""
        async with semaphore:
            row_id = row.at['id']
            query = row.at[in_column]

            if pd.isna(row_id) or pd.isna(query) or str(query).strip() == '':
                Log.warn(f"Skipping -- ID: {row_id}, Query: {query}")
                return

            start_time = time.perf_counter()
            try:
                response = await self._process_query(
                    session,
                    int(row_id),
                    str(query),
                    provider,
                    out_table,
                    out_column,
                    format,
                    template,
                    min_length,
                )
                duration = time.perf_counter() - start_time
                self._log_metrics(row_id, duration, query, response)

            except (XMLValidationError, XMLLengthError) as e:
                duration = time.perf_counter() - start_time
                self._log_metrics(row_id, duration, error=e)
                raise

    async def _process_query(
        self,
        session: Any,
        row_id: int,
        query: str,
        provider: OllamaProvider,
        out_table: str,
        out_column: str,
        format: str | None,
        template: str | None,
        min_length: int = 0,
    ) -> str:
        """Process a query through the AI pipeline and return response."""
        try:
            response = await self.generate_response(query, provider, format,
                                                    template, min_length)
            await self._update_db(session, out_table, row_id, response,
                                  out_column)
            return response
        except Exception as e:
            Log.warn(
                f"Skipping row {row_id} due to unexpected error: {str(e)}")
            await self._update_db(session, out_table, row_id, None, out_column)
            return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
    )
    async def _update_db(
        self,
        session: Any,
        out_table: str,
        row_id: int,
        response: str,
        out_column: str,
    ) -> None:
        """Update the database with the generated AI response."""
        try:
            if row_id is None:
                raise ValueError("Row ID cannot be None")

            table = await self.db.ensure_table_exists(session, out_table)
            table = await self.db.ensure_column_exists(session, table,
                                                       out_column)
            stmt = (update(table).where(table.c.id == row_id).values(
                {out_column: response}))

            session.execute(stmt)
            session.commit()
            Log.info(
                f"Updated -- ID: {row_id} | "
                f"Table: {out_table} | "
                f"Column: {out_column}", )

        except Exception as e:
            if session:
                session.rollback()
            raise RuntimeError(f"Failed to update database: {str(e)}") from e
