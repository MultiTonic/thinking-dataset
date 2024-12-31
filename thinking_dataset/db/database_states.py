"""
@file thinking_dataset/db/session_states.py
@description Defines the states for session management.
@version 1.0.0
@license MIT
"""
from enum import Enum


class DatabaseStates(Enum):
    IDLE = "Idle"
    ACTIVE = "Active"
    COMMIT = "Commit"
    ROLLBACK = "Rollback"
