"""
@file thinking_dataset/db/session_statemachine.py
@description Defines the state machine for session management.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from statemachine import StateMachine, State
from ..session.states import States
from ...utilities.log import Log


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
        self.logger = Log.setup(__name__)

    def on_enter_commit(self):
        """Define actions to take when entering the commit state."""
        try:
            self.logger.info("Entering commit state.")
            # Add your commit logic here
        except Exception as e:
            self.logger.error(f"Error entering commit state: {e}")

    def on_enter_rollback(self):
        """Define actions to take when entering the rollback state."""
        try:
            self.logger.info("Entering rollback state.")
            # Add your rollback logic here
        except Exception as e:
            self.logger.error(f"Error entering rollback state: {e}")
