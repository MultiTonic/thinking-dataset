# @file thinking_dataset/db/models/cables.py
# @description Defines the Cables model.
# @version 1.0.2
# @license MIT

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Cables(Base):
    """
    SQLAlchemy model for the cables table.

    This class:
    1. Defines the schema for storing cable records
    2. Manages cable queries and thinking responses
    3. Serves as the parent table for thoughts

    Attributes:
        id (int): Primary key for the cable record
        query (str): The input query text
        thinking (str): The generated thinking response
    """

    __tablename__ = 'cables'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Content columns
    query = Column(String, nullable=False)
    thinking = Column(String, nullable=True)

    def __repr__(self):
        return f"<Cable(id={self.id})>"
