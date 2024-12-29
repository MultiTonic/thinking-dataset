"""
@file thinking_dataset/db/session.py
@description Handles database session management with a finite state machine.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .session_statemachine import SessionStateMachine
from ...utilities.log import Log


class Session:
    """
    A class to handle database session management using FSM.
    """

    _session = None
    _Session = None

    def __init__(self, engine):
        """
        Constructs all the necessary attributes for the SessionStore object.

        Parameters
        ----------
        engine : Engine
            The SQLAlchemy engine to bind sessions to.
        """
        if not Session._Session:
            Session._Session = sessionmaker(bind=engine)
        self.state_machine = SessionStateMachine()
        self.logger = Log.setup(__name__)

    def commit(self):
        if Session._session:
            Session._session.commit()
        Log.info(self.logger, "Committed session")

    def rollback(self):
        if Session._session:
            Session._session.rollback()
            Session._session = None
        Log.info(self.logger, "Rolled back session")

    def get(self):
        if self.state_machine.is_idle:
            Session._session = Session._Session()
            self.state_machine.start_session()
        try:
            yield Session._session
        except SQLAlchemyError as e:
            self.state_machine.rollback_session()
            Log.error(self.logger, f"Session error: {e}")
