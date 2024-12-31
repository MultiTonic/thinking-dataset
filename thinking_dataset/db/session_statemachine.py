"""
@file thinking_dataset/db/session_statemachine.py
@description Defines the state machine for session management.
@version 1.0.0
@license MIT
"""

from statemachine import StateMachine, State
from .database_states import DatabaseStates as States
from ..utilities.log import Log


class SessionStateMachine(StateMachine):
    """
    A state machine for managing session states.
    """
    idle = State(States.IDLE.value, initial=True)
    active = State(States.ACTIVE.value)
    commit = State(States.COMMIT.value)
    rollback = State(States.ROLLBACK.value)

    start_session = idle.to(active)
    commit_session = active.to(commit)
    rollback_session = active.to(rollback)
    close_session = commit.to(idle) | rollback.to(idle) | active.to(idle)

    def __init__(self):
        super().__init__()
        self.log = Log.setup(self.__class__.__name__)

    @property
    def is_idle(self):
        """Check if the state is idle."""
        return self.current_state == self.idle

    @property
    def is_active(self):
        """Check if the state is active."""
        return self.current_state == self.active

    def on_enter_commit(self):
        """Define actions to take when entering the commit state."""
        try:
            Log.info(self.log, "Entering commit state.")
        except Exception as e:
            Log.error(self.log, f"Error entering commit state: {e}")

    def on_enter_rollback(self):
        """Define actions to take when entering the rollback state."""
        try:
            Log.info(self.log, "Entering rollback state.")
        except Exception as e:
            Log.error(self.log, f"Error entering rollback state: {e}")
