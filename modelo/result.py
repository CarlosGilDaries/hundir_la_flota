from enum import Enum, auto

class ShotResult(Enum):
    """
    Enum representing the result of a shot on the board.
    """
    WATER = auto()
    HIT = auto()
    SUNK = auto()
    REPEATED = auto()
    INVALID = auto()