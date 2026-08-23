from enum import Enum, auto


class GameStatus(Enum):
    UNKNOWN = auto()

    PLACE_YOUR_BETS = auto()

    BETS_CLOSING = auto()

    BETS_CLOSED = auto()

    NEXT_GAME_SOON = auto()
