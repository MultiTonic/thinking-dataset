"""Pipe for generating queries from templates and seeds.

This module provides functionality for generating queries by combining
templates with seed text samples using configurable dynamic label replacements.
"""

import re
import random
import pandas as pd
from tqdm import tqdm
from .pipe import Pipe
from typing import List
from thinking_dataset.utils.log import Log
from sqlalchemy import select, Table, MetaData
from tenacity import retry, stop_after_attempt, wait_fixed
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.decorators.with_db_session import with_db_session

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class QueryGenerationPipe(Pipe):
    """Pipe for generating queries by combining templates with source
        text samples.

    This pipe:
    1. Fetches seed texts from a specified database table/column
    2. Randomly samples multiple seeds of configured length
    3. Combines seeds with a template to generate queries
    4. Writes generated queries to output database table

    Config:
        input (list): Source table and column config for seeds
        output (list): Target table and column config for queries
        seed_amount (int): Number of seeds to use per query
        seed_length (int): Length of each seed text
        seed_offset (int): Offset into seed text to start from
        batch_size (int): Number of queries to generate
        if_exists (str): How to handle existing output table
        prompt (dict): Template configuration
    """

    @with_db_session
    def flow(self, df: pd.DataFrame, session=None, **kwargs) -> pd.DataFrame:
        """Execute the query generation pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            session: Database session
            **kwargs: Additional keyword arguments including pipeline_config

        Returns:
            pd.DataFrame: DataFrame with generated queries

        Raises:
            ValueError: If batch_size is not provided in pipeline config
        """
        Log.info("Starting QueryGenerationPipe")
        template_path = self.config["prompt"]["template"]
        if_exists = self.config["if_exists"]
        use_ellipsis = self.config.get("elipsis", True)

        pipeline_config = kwargs.get("pipeline_config", {})
        if not pipeline_config:
            raise ValueError("Pipeline configuration is required")

        template = TemplateLoader.load(template_path)
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
        seeds = self._fetch_seeds(session, table_name, in_column)
        queries = self._generate_queries(seeds, seed_amount, seed_length,
                                         seed_offset, template, batch_size,
                                         label, use_ellipsis)

        Log.info(f"DataFrame Shape: {df.shape}")
        Log.info(f"Queries Generated: {len(queries)}")
        Log.info(f"ID Column Length: {len(df['id'])}")

        df = pd.DataFrame({"id": df['id'], out_column: queries})
        self._write_to_db(df, session, out_table, if_exists)

        Log.info("Finished QueryGenerationPipe")
        return df

    def _validate(self, df: pd.DataFrame, column: str):
        """Validate DataFrame and column requirements.

        Args:
            df (pd.DataFrame): DataFrame to validate
            column (str): Column name to validate

        Raises:
            ValueError: If validation fails
        """
        if df.empty:
            raise ValueError("DataFrame is empty.")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if df[column].isnull().all():
            raise ValueError(f"All values in column '{column}' are null.")

    def _prepare_df(self, template: str, out_column: str,
                    batch_size: int) -> pd.DataFrame:
        """Prepare DataFrame with template and IDs.

        Args:
            template (str): Template string
            out_column (str): Column name for queries
            batch_size (int): Number of rows to generate

        Returns:
            pd.DataFrame: Prepared DataFrame with IDs and template
        """
        data = [{'id': i + 1, out_column: template} for i in range(batch_size)]
        df = pd.DataFrame(data)
        return df

    def _get_seeds(self,
                   seeds: pd.DataFrame,
                   amount: int,
                   size: int,
                   offset: int,
                   use_ellipsis: bool = False) -> List[str]:
        """Get random seed texts from the input DataFrame.

        Args:
            seeds (pd.DataFrame): DataFrame containing seed texts
            amount (int): Number of seeds to sample
            size (int): Length of text to extract from each seed
            offset (int): Starting position for text extraction
            use_ellipsis (bool): Whether to add ellipsis to truncated text

        Returns:
            List[str]: List of extracted seed texts

        Raises:
            ValueError: If no seeds are available
        """
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

    def _fetch_seeds(self, session, table_name: str,
                     in_column: str) -> pd.DataFrame:
        """Fetch seed texts from database table.

        Args:
            session: Database session
            table_name (str): Source table name
            in_column (str): Column containing seed texts

        Returns:
            pd.DataFrame: DataFrame containing seed texts
        """
        Log.info(f"Fetching seeds from {table_name}.{in_column}")
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        Log.info(f"Total seeds in {table_name}.{in_column}: {len(seeds)}")
        return seeds

    def _get_query(self, template: str, seeds: List[str], label: str) -> str:
        """Generate query by replacing labeled placeholders with seed texts.

        Args:
            template (str): Template string with labeled placeholders
            seeds (List[str]): List of seed texts to inject
            label (str): Label to match in template placeholders

        Returns:
            str: Template with replaced values
        """
        value = '\n' + ''.join(f'- {seed}\n' for seed in seeds)
        pattern = r'{{\s*' + re.escape(label) + r'\s*}}'
        return re.sub(pattern, value, template)

    def _generate_queries(self, seeds_df: pd.DataFrame, seed_amount: int,
                          size: int, offset: int, template: str,
                          batch_size: int, label: str,
                          use_ellipsis: bool) -> List[str]:
        """Generate multiple queries using seed texts and template.

        Args:
            seeds_df (pd.DataFrame): DataFrame containing seed texts
            seed_amount (int): Number of seeds per query
            size (int): Length of text to extract from each seed
            offset (int): Starting position for text extraction
            template (str): Template string with placeholders
            batch_size (int): Number of queries to generate
            label (str): Label to match in template placeholders
            use_ellipsis (bool): Whether to add ellipsis to truncated text

        Returns:
            List[str]: List of generated queries
        """
        queries = []
        for _ in tqdm(range(batch_size), desc="Generating Queries", unit="qu"):
            seeds = self._get_seeds(seeds_df, seed_amount, size, offset,
                                    use_ellipsis)
            query = self._get_query(template, seeds, label)
            queries.append(query)
        return queries

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session, out_table: str,
                     if_exists: str):
        """Write DataFrame to database with retry logic.

        Args:
            df (pd.DataFrame): Data to write
            session: Database session
            out_table (str): Target table name
            if_exists (str): How to handle existing table
        """
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")
