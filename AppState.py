from enum import Enum

class AppState(Enum):
    DETECTING = 1,
    SEIZURE_DETECTED = 2,
    SEIZURE_ACTION_HANDLED = 3