"""
@file project_root/thinking_dataset/db/database.py
@description Implementation of the Database class.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
from sqlalchemy import create_engine
from contextlib import contextmanager
from .session.session import Session
from ..utilities.log import Log
from ..utilities.execute import execute
from .operations.query import Query
from .operations.fetch_data import FetchData


class Database:

    def __init__(self, url: str):
        self.url = url
        self.engine = create_engine(self.url)
        self.session = Session(self.engine)
        self.logger = Log.setup_logger(__name__)

    @contextmanager
    def get_session(self):
        session = self.session.get()
        yield session

    @execute(Query)
    def query(self, query: str):
        return query

    @execute(FetchData)
    def fetch_data(self, query: str):
        return query
