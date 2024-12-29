"""
@file thinking_dataset/db/session_statemachine.py
@description Defines the state machine for session management.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
from statemachine import StateMachine, State
from .session_states import SessionStates


class SessionStateMachine(StateMachine):
    """
    A state machine for managing session states.
    """
    idle = State(SessionStates.IDLE.value, initial=True)
    active = State(SessionStates.ACTIVE.value)
    commit = State(SessionStates.COMMIT.value, on_enter='commit')
    rollback = State(SessionStates.ROLLBACK.value, on_enter='rollback')

    start_session = idle.to(active)
    commit_session = active.to(commit)
    rollback_session = active.to(rollback)
    close_session = commit.to(idle) | rollback.to(idle) | active.to(idle)
