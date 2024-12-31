import os
import sys
import pandas as pd
from dotenv import load_dotenv
from typing import List, Union, Optional
import logging
from thinking_dataset.db.database import Database

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class BaseDataset:
    """
    A base class that provides common dataset operations and logging functionalities.
    """

    def __init__(self, data_tonic, config):
        """
        Constructs all the necessary attributes for the BaseDataset object.
        """
        self.data_tonic = data_tonic
        self.config = config

        # Load environment variables
        load_dotenv()
        self.root_dir = os.path.abspath(os.getenv("ROOT_DIR", "."))
        self.data_dir = os.path.join(self.root_dir,
                                     os.getenv("DATA_DIR", "data"))
        self.raw_dir = os.path.join(self.data_dir, "raw")

    def get_path(self,
                 dataset_id: Optional[str] = None) -> Union[str, dict, None]:
        """
        Constructs the path for the dataset within the organization.
        """
        try:
            if dataset_id:
                dataset_info = self.data_tonic.get_info.execute(dataset_id)
                logger.info(f"Retrieved dataset info: {dataset_info}")
                return dataset_info
            path = f"{self.data_tonic.organization}/{self.data_tonic.dataset}"
            logger.info(f"Constructed dataset path: {path}")
            return path
        except Exception as e:
            logger.error(f"Error constructing dataset path: {e}")

    def list_files(self) -> Optional[List[str]]:
        """
        List dataset files in the raw directory.
        """
        try:
            dataset_files = self.data_tonic.get_file_list.execute(self.raw_dir)
            logger.info(
                f"Listed files in directory {self.raw_dir}: {dataset_files}")
            return dataset_files
        except Exception as e:
            logger.error(
                f"Error listing files in directory {self.raw_dir}: {e}")

    def create(self, db_url: str, db_config: str) -> Optional[Database]:
        """
        Create a Database instance.
        """
        try:
            database = Database(url=db_url, config_path=db_config)
            logger.info(f"Created database instance with URL: {db_url}")
            return database
        except Exception as e:
            logger.error(f"Error creating database instance: {e}")

    def load(self, database: Database) -> bool:
        """
        Load dataset files into the database.
        """
        dataset_files = self.list_files()
        if not dataset_files:
            logger.error("No files found in the data directory.")
            sys.exit(1)

        parquet_files = [os.path.join(self.raw_dir, f) for f in dataset_files]
        logger.info(f"Parquet files to be loaded: {parquet_files}")

        # Log the contents of the raw directory to verify if the files exist
        try:
            files_in_directory = os.listdir(self.raw_dir)
            logger.info(
                f"Files in directory {self.raw_dir}: {files_in_directory}")
        except Exception as e:
            logger.error(f"Error listing directory {self.raw_dir}: {e}")
            sys.exit(1)

        with database.get_session() as session:
            for file_path in parquet_files:
                try:
                    logger.info(f"Attempting to load file: {file_path}")
                    df = pd.read_parquet(file_path)
                    logger.info(f"DataFrame columns: {df.columns}")
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=database.engine,
                              if_exists='append',
                              index=False)
                except FileNotFoundError:
                    logger.error(f"File not found: {file_path}")
                    session.rollback()
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {e}",
                                 exc_info=True)
                    session.rollback()
                    sys.exit(1)
            try:
                session.commit()
                logger.info(
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error committing the session: {e}")
                sys.exit(1)

    def download(self, token: str, dataset_id: str, data_dir: str) -> bool:
        """
        Downloads the dataset from Hugging Face.
        """
        try:
            dataset_info = self.data_tonic.get_info.execute(dataset_id)
            if dataset_info:
                logger.info(f"Downloading dataset {dataset_id}...")

                download_urls = self.data_tonic.get_download_urls.execute(
                    dataset_id)
                for url in download_urls:
                    self.data_tonic.get_download_file.execute(
                        dataset_id, url, data_dir, token)

                logger.info(f"Dataset {dataset_id} downloaded successfully.")
                return True
            else:
                logger.error(f"Dataset {dataset_id} not found.")
                return False
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_id}: {e}")
            return False
