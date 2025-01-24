# @file thinking_dataset/db/models/thoughts.py
# @description Defines the Thoughts model.
# @version 1.0.2
# @license MIT

from sqlalchemy import Column, ForeignKey, Integer, String
from .cables import Base


class Thoughts(Base):
    """
    SQLAlchemy model for the thoughts table.

    This class:
    1. Defines the schema for storing thought records
    2. Links thoughts to cables through foreign key relationship
    3. Manages thought content and metadata

    Attributes:
        id (int): Primary key for the thought record
        table_id (int): ID of the source table
        thought_id (int): Unique identifier for the thought
        content (str): The actual thought content
        table_name (str): Name of the source table
        cable_id (int): Optional foreign key to cables table
    """

    __tablename__ = 'thoughts'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Required columns
    table_id = Column(Integer, nullable=False)
    thought_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    table_name = Column(String, nullable=False)

    # Foreign key relationship to Cables model
    cable_id = Column(Integer,
                      ForeignKey('cables.id', ondelete='CASCADE'),
                      nullable=True)

    def __repr__(self):
        return (f"<Thought(id={self.id}, "
                f"table_id={self.table_id}, "
                f"thought_id={self.thought_id})>")
