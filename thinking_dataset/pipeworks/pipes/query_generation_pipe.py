"""Query Generation Pipeline Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import re
from typing import List, Any

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.sources.input_source import InputSource
from thinking_dataset.sources.output_source import OutputSource
from thinking_dataset.utils.log import Log
from .pipe import Pipe


class QueryGenerationPipe(Pipe):
    """Pipe for generating queries by combining templates with
       source text samples."""

    # Public methods
    @with_db_session
    def flow(self,
             df: pd.DataFrame,
             session: Any = None,
             **kwargs) -> pd.DataFrame:
        """Execute the query generation pipeline."""
        Log.info("Starting QueryGenerationPipe")

        # Get configuration values
        template = TemplateLoader.load(
            self.config["query"]["template"],
            self.config["query"].get("validate", True))
        batch_size = self.get_batch_size()
        sources = self._parse_source_configs()

        # Flush the root df (if configured)
        if self.config.get("flush", False):
            df = self.flush(df)

        # Generate queries with incremental id for each query
        queries = self._generate_queries(template, batch_size, sources,
                                         session)

        # Selection context logic: update DataFrame in one statement
        output = self._parse_output_configs()[0]
        df = df.copy().assign(
            id=[item["id"] for item in queries],
            **{output.column: [item["query"] for item in queries]})
        self.log_df_state(df, f"Final - {output.table}.{output.column}")
        self._write_to_db(df, session, output.table, output.if_exists)

        Log.info("Finished QueryGenerationPipe")
        return df

    def log_df_state(self, df: pd.DataFrame, state: str = "") -> None:
        """Log the current state of the DataFrame."""
        prefix = f"{state} " if state else ""
        Log.info(f"{prefix}DataFrame shape: {df.shape}")
        Log.info(f"{prefix}DataFrame columns: {df.columns.tolist()}")

    # Protected methods
    def _generate_queries(self, template: str, batch_size: int,
                          sources: List[InputSource],
                          session: Any) -> List[dict]:
        """Generate queries using multiple sources, each with a unique id."""
        if not sources:
            Log.info(
                "No sources configured - returning template text directly")
            return [{
                "id": i,
                "query": template
            } for i in range(1, batch_size + 1)]

        queries = []
        for i in range(1, batch_size + 1):
            query = template
            for source in sources:
                df_source = source.fetch_source(session)
                samples = source.get_samples(df_source, source.ellipsis)
                query = self._get_query(query, source, samples)
            queries.append({"id": i, "query": query})

        Log.info(f"Total queries generated: {len(queries)}")
        return queries

    def _get_query(self, template: str, source: InputSource,
                   seeds: List[str]) -> str:
        """Generate query by replacing labeled placeholders with seed texts."""
        value = '\n' + ''.join(f'- {seed}\n' for seed in seeds)
        pattern = r'{{\s*' + re.escape(source.label) + r'\s*}}'
        return re.sub(pattern, value, template)

    def _parse_source_configs(self) -> List[InputSource]:
        """Parse source configurations from config."""
        sources = []
        input_list = self.config.get("input", [])
        Log.info(f"Found {len(input_list)} input configurations")

        for input_config in input_list:
            if isinstance(input_config, dict):
                source_config = input_config.get("source", {})
                Log.info(f"Processing source config: {source_config}")
                if source_config:
                    try:
                        source = InputSource.from_config(source_config)
                        Log.info(
                            f"Created source: table={source.table}, "
                            f"column={source.column}, label={source.label}")
                        sources.append(source)
                    except Exception as e:
                        Log.warn(f"Failed to create source from config: {e}")
                else:
                    Log.warn(
                        f"Invalid source configuration found: {source_config}")

        Log.info(f"Total valid sources configured: {len(sources)}")
        return sources

    def _parse_output_configs(self) -> List[OutputSource]:
        """Parse output configurations from config."""
        outputs = []
        output_list = self.config.get("output", [])
        Log.info(f"Found {len(output_list)} output configurations")

        for output_config in output_list:
            if isinstance(output_config, dict):
                try:
                    output = OutputSource.from_config(
                        output_config.get("source", {}))
                    Log.info(f"Created output: table={output.table}, "
                             f"column={output.column}")
                    outputs.append(output)
                except Exception as e:
                    Log.warn(f"Failed to create output from config: {e}")

        Log.info(f"Total valid outputs configured: {len(outputs)}")
        return outputs

    def _prepare_df(self, template: str, out_column: str,
                    batch_size: int) -> pd.DataFrame:
        """Prepare DataFrame with template and IDs."""
        data = [{'id': i + 1, out_column: template} for i in range(batch_size)]
        df = pd.DataFrame(data)
        return df

    def _validate(self, df: pd.DataFrame, column: str) -> None:
        """Validate DataFrame and column requirements."""
        if df.empty:
            raise ValueError("DataFrame is empty.")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if df[column].isnull().all():
            raise ValueError(f"All values in column '{column}' are null.")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session: Any, out_table: str,
                     if_exists: str) -> None:
        """Write DataFrame to database with retry logic."""
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")
