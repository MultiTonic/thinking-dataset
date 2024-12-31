"""
@file thinking_dataset/db/database_session.py
@description Handles database session management with a finite state machine.
@version 1.0.0
@license MIT
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from .session_statemachine import SessionStateMachine as StateMachine
from ..utilities.log import Log


class DatabaseSession:
    """
    A class to handle database session management using FSM.
    """

    _session = None
    _Session = None

    def __init__(self, engine):
        self.log = Log.setup(self.__class__.__name__)
        if not DatabaseSession._Session:
            DatabaseSession._Session = sessionmaker(bind=engine)
            Log.info(self.log, "Sessionmaker initialized successfully.")
        self.state = StateMachine()
        Log.info(self.log,
                 "State machine and logger initialized successfully.")

    def _start(self):
        if self.state.is_idle:
            try:
                DatabaseSession._session = DatabaseSession._Session()
                self.state.start_session()
                Log.info(self.log, "Session started successfully.")
            except SQLAlchemyError as e:
                Log.error(self.log, f"Error starting session: {e}")

    def _commit(self):
        if self.state.is_active:
            try:
                DatabaseSession._session.commit()
                self.state.commit_session()
                Log.info(self.log, "Committed session")
            except SQLAlchemyError as e:
                Log.error(self.log, f"Error committing session: {e}")

    def _rollback(self, error):
        if DatabaseSession._session:
            try:
                DatabaseSession._session.rollback()
                self.state.rollback_session()
                Log.error(self.log, f"Session error: {error}")
            except SQLAlchemyError as e:
                Log.error(self.log, f"Error during rollback: {e}")

    def _close(self):
        if DatabaseSession._session:
            try:
                DatabaseSession._session.close()
                self.state.close_session()
                Log.info(self.log, "Session closed successfully.")
            except SQLAlchemyError as e:
                Log.error(self.log, f"Error closing session: {e}")

    @contextmanager
    def get(self):
        self._start()
        try:
            yield DatabaseSession._session
            self._commit()
        except SQLAlchemyError as e:
            self._rollback(e)
        finally:
            self._close()
