# @file session_statemachine.py
# @description Session management state machine.
# @version 1.0.2
# @license MIT

from statemachine import StateMachine, State
from .database_states import DatabaseStates as States
from thinking_dataset.utils.log import Log


class SessionStateMachine(StateMachine):
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

    @property
    def is_idle(self):
        return self.current_state == self.idle

    @property
    def is_active(self):
        return self.current_state == self.active

    def on_enter_commit(self):
        try:
            Log.info("Entering commit state.")
        except Exception as e:
            Log.error(f"Error entering commit state: {e}")

    def on_enter_rollback(self):
        try:
            Log.info("Entering rollback state.")
        except Exception as e:
            Log.error(f"Error entering rollback state: {e}")
