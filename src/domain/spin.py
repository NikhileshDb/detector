from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class SpinSource(Enum):
    AUTO = auto()
    MANUAL = auto()
    CORRECTED = auto()


@dataclass(frozen=True)
class Spin:
    id: str

    round_id: int

    number: str

    source: SpinSource

    confidence: float | None

    detected_at: datetime

    original_number: str | None = None
