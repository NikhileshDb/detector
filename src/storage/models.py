from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RoundStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WAITING_FOR_RESULT = (
        "WAITING_FOR_RESULT"
    )
    COMPLETED = "COMPLETED"
    MISSING = "MISSING"


class SpinSource(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    CORRECTED = "CORRECTED"
    INSERTED = "INSERTED"


@dataclass(frozen=True)
class StoredRound:
    id: int
    sequence: int
    status: RoundStatus
    started_at: datetime
    completed_at: datetime | None


@dataclass(frozen=True)
class StoredSpin:
    id: str
    round_id: int
    number: str
    color: str
    source: SpinSource
    confidence: float | None
    original_number: str | None
    detected_at: datetime
