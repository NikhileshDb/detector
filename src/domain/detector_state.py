from enum import Enum, auto


class DetectorState(Enum):
    UNKNOWN = auto()

    PLACE_YOUR_BETS = auto()

    BETS_CLOSING = auto()

    WAITING_FOR_RESULT = auto()

    READING_RESULT = auto()

    RESULT_CONFIRMED = auto()

    NEXT_GAME_SOON = auto()
