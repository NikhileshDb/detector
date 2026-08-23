from dataclasses import dataclass
from enum import Enum


class RouletteColor(str, Enum):
    RED = "RED"
    BLACK = "BLACK"
    GREEN = "GREEN"


@dataclass(frozen=True)
class StatusResult:
    number: str
    color: RouletteColor
    confidence: float


@dataclass(frozen=True)
class ResultEvidence:
    status_number: str | None
    status_color: RouletteColor | None
    status_confidence: float | None

    number_roi_number: str | None
    number_roi_confidence: float | None


@dataclass(frozen=True)
class ValidatedResult:
    number: str
    color: RouletteColor
    confidence: float
