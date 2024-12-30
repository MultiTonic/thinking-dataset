"""
@file thinking_dataset/commands/load.py
@description CLI command to load downloaded dataset files into SQLite database.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from thinking_dataset.io.files import Files
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///thinking-dataset.db')
HF_DATASET_TYPE = os.getenv('HF_DATASET_TYPE', 'parquet')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


@click.command()
@click.option('--data-dir',
              default='data/raw',
              help='Directory containing raw dataset files.')
def load(data_dir):
    """Load downloaded dataset files into SQLite database."""
    # Ensure the data directory exists
    os.makedirs(data_dir, exist_ok=True)

    session = Session()
    files = Files(data_dir)
    dataset_files = files.list_files(data_dir,
                                     file_extension=f".{HF_DATASET_TYPE}")

    parquet_files = [files.get_file_path(data_dir, f) for f in dataset_files]

    for file_path in parquet_files:
        # Load parquet file into a DataFrame
        df = pd.read_parquet(file_path)
        # Use the file name as the table name (excluding extension)
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        # Load DataFrame into SQLite database
        df.to_sql(table_name, con=engine, if_exists='append', index=False)

    session.commit()
    session.close()
    click.echo("Successfully loaded dataset files into the database.")


if __name__ == "__main__":
    load()
