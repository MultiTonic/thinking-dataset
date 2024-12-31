"""
@file thinking_dataset/db/session_states.py
@description Defines the states for session management.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
from enum import Enum


class DatabaseStates(Enum):
    IDLE = "Idle"
    ACTIVE = "Active"
    COMMIT = "Commit"
    ROLLBACK = "Rollback"
