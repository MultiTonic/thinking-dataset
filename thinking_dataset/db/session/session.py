"""
@file thinking_dataset/db/session/session.py
@description Handles database session management with a finite state machine.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from .statemachine import StateMachine
from ...utilities.log import Log


class Session:
    """
    A class to handle database session management using FSM.
    """

    _session = None
    _Session = None

    def __init__(self, engine):
        if not Session._Session:
            Session._Session = sessionmaker(bind=engine)
            Log.info("Sessionmaker initialized successfully.")

        self.state = StateMachine()
        self.logger = Log.setup(__name__)
        Log.info("State machine and logger initialized successfully.")

    def _start(self):
        if self.state.is_idle:
            try:
                Session._session = Session._Session()
                self.state.start_session()
                Log.info("Session started successfully.")
            except SQLAlchemyError as e:
                self.logger.error(f"Error starting session: {e}")

    def _commit(self):
        if self.state.is_active:
            try:
                Session._session.commit()
                self.state.commit_session()
                Log.info(self.logger, "Committed session")
            except SQLAlchemyError as e:
                self.logger.error(f"Error committing session: {e}")

    def _rollback(self, error):
        if Session._session:
            try:
                Session._session.rollback()
                self.state.rollback_session()
                Log.error(self.logger, f"Session error: {error}")
            except SQLAlchemyError as e:
                self.logger.error(f"Error during rollback: {e}")

    def _close(self):
        if Session._session:
            try:
                Session._session.close()
                self.state.close_session()
                Log.info("Session closed successfully.")
            except SQLAlchemyError as e:
                self.logger.error(f"Error closing session: {e}")

    @contextmanager
    def get(self):
        self._start()
        try:
            yield Session._session
            self._commit()
        except SQLAlchemyError as e:
            self._rollback(e)
        finally:
            self._close()
