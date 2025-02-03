"""Query Generation Pipeline Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import random
import re
from typing import List, Any

import pandas as pd
from sqlalchemy import MetaData, Table, select
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm import tqdm

from thinking_dataset.decorators.with_db_session import with_db_session
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.utils.log import Log
from .pipe import Pipe


class QueryGenerationPipe(Pipe):
    """Pipe for generating queries by combining templates with source
        text samples."""

    def log_df_state(self, df: pd.DataFrame, state: str = "") -> None:
        """Log the current state of the DataFrame."""
        prefix = f"{state} " if state else ""
        Log.info(f"{prefix}DataFrame shape: {df.shape}")
        Log.info(f"{prefix}DataFrame columns: {df.columns.tolist()}")

    @with_db_session
    def flow(self,
             df: pd.DataFrame,
             session: Any = None,
             **kwargs) -> pd.DataFrame:
        """Execute the query generation pipeline."""
        Log.info("Starting QueryGenerationPipe")

        # Get configuration values
        template_path = self.config["prompt"]["template"]
        validate_template = self.config["prompt"].get("validate", True)
        if_exists = self.config["if_exists"]
        use_ellipsis = self.config.get("elipsis", True)

        # Load template and get configuration values
        template = TemplateLoader.load(template_path, validate_template)
        batch_size = self.get_batch_size()
        in_config = self.config["input"][0]
        out_config = self.config["output"][0]
        table_name = in_config["table"]
        in_column = in_config["columns"][0]
        label = in_config.get("label", "seeds")
        seed_amount = in_config.get("seed_amount", 3)
        seed_length = in_config.get("seed_length", 2500)
        seed_offset = in_config.get("seed_offset", 0)
        out_table = out_config["table"]
        out_column = out_config["columns"][0]

        Log.info(f"Using batch_size: {batch_size} for table {table_name}")
        df = self._prepare_df(template, out_column, batch_size)
        self.log_df_state(df, "Prepared")

        # Get seeds and generate queries
        seeds = self._fetch_seeds(session, table_name, in_column)
        queries = self._generate_queries(seeds, seed_amount, seed_length,
                                         seed_offset, template, batch_size,
                                         label, use_ellipsis)

        # Prepare and write output DataFrame
        df = pd.DataFrame({"id": df['id'], out_column: queries})
        self.log_df_state(df, "Final")
        self._write_to_db(df, session, out_table, if_exists)

        Log.info("Finished QueryGenerationPipe")
        return df

    def _validate(self, df: pd.DataFrame, column: str) -> None:
        """Validate DataFrame and column requirements."""
        if df.empty:
            raise ValueError("DataFrame is empty.")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if df[column].isnull().all():
            raise ValueError(f"All values in column '{column}' are null.")

    def _prepare_df(self, template: str, out_column: str,
                    batch_size: int) -> pd.DataFrame:
        """Prepare DataFrame with template and IDs."""
        data = [{'id': i + 1, out_column: template} for i in range(batch_size)]
        df = pd.DataFrame(data)
        return df

    def _get_seeds(self,
                   seeds: pd.DataFrame,
                   amount: int,
                   size: int,
                   offset: int,
                   use_ellipsis: bool = False) -> List[str]:
        """Get random seed texts from the input DataFrame."""
        seeds_length = len(seeds)
        if seeds_length == 0:
            raise ValueError("No seeds available to generate.")
        indices = random.sample(range(seeds_length), amount)
        seed_texts = []
        for idx in indices:
            full_text = seeds.iloc[idx].values[0]
            seed = full_text[offset:offset + size]
            if use_ellipsis and len(full_text[offset:]) > size:
                seed = seed + "..."
            seed_texts.append(seed)
        return seed_texts

    def _fetch_seeds(self, session: Any, table_name: str,
                     in_column: str) -> pd.DataFrame:
        """Fetch seed texts from database table."""
        Log.info(f"Fetching seeds from {table_name}.{in_column}")
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        Log.info(f"Total seeds in {table_name}.{in_column}: {len(seeds)}")
        return seeds

    def _get_query(self, template: str, seeds: List[str], label: str) -> str:
        """Generate query by replacing labeled placeholders with seed texts."""
        value = '\n' + ''.join(f'- {seed}\n' for seed in seeds)
        pattern = r'{{\s*' + re.escape(label) + r'\s*}}'
        return re.sub(pattern, value, template)

    def _generate_queries(self, seeds_df: pd.DataFrame, seed_amount: int,
                          size: int, offset: int, template: str,
                          batch_size: int, label: str,
                          use_ellipsis: bool) -> List[str]:
        """Generate multiple queries using seed texts and template."""
        queries = []
        for _ in tqdm(range(batch_size), desc="Generating Queries", unit="qu"):
            seeds = self._get_seeds(seeds_df, seed_amount, size, offset,
                                    use_ellipsis)
            query = self._get_query(template, seeds, label)
            queries.append(query)
        return queries

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session: Any, out_table: str,
                     if_exists: str) -> None:
        """Write DataFrame to database with retry logic."""
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")
