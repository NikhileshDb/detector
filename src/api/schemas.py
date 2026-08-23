from datetime import datetime

from pydantic import BaseModel

from storage.models import StoredRound, StoredSpin


class RoundOut(BaseModel):
    id: int
    sequence: int
    status: str
    started_at: datetime
    completed_at: datetime | None

    @classmethod
    def from_domain(cls, round_item: StoredRound) -> "RoundOut":

        return cls(
            id=round_item.id,
            sequence=round_item.sequence,
            status=round_item.status.value,
            started_at=round_item.started_at,
            completed_at=round_item.completed_at,
        )


class SpinOut(BaseModel):
    id: str
    round_id: int
    number: str
    color: str
    source: str
    confidence: float | None
    original_number: str | None
    detected_at: datetime

    @classmethod
    def from_domain(cls, spin: StoredSpin) -> "SpinOut":

        return cls(
            id=spin.id,
            round_id=spin.round_id,
            number=spin.number,
            color=spin.color,
            source=spin.source.value,
            confidence=spin.confidence,
            original_number=spin.original_number,
            detected_at=spin.detected_at,
        )
