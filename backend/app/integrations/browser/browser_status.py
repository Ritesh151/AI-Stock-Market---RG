"""
Browser and Authentication State Enumerations.
Separates operational browser lifecycle state from ChatGPT login authentication state.
"""

from enum import Enum


class BrowserState(str, Enum):
    """
    Explicit lifecycle states of the managed browser instance.
    """
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    AUTHENTICATED = "AUTHENTICATED"
    TARGET_OPEN = "TARGET_OPEN"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    STOPPING = "STOPPING"


class LoginState(str, Enum):
    """
    Independent authentication status of the ChatGPT session.
    """
    UNKNOWN = "UNKNOWN"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    AUTHENTICATED = "AUTHENTICATED"
    CHALLENGE_DETECTED = "CHALLENGE_DETECTED"
