from datetime import datetime

from pydantic import BaseModel

from analytics.dashboard_summary import DashboardSummary, NumberFrequency
from analytics.street_analytics import StreetStats
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


class ManualResultIn(BaseModel):
    number: str


class CorrectionIn(BaseModel):
    corrected_number: str


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


class StreetStatsOut(BaseModel):
    street: int
    numbers: tuple[int, int, int]
    hits: int
    last_hit_round: int | None
    gap_spins: int | None

    @classmethod
    def from_domain(cls, stats: StreetStats) -> "StreetStatsOut":

        return cls(
            street=stats.street,
            numbers=stats.numbers,
            hits=stats.hits,
            last_hit_round=stats.last_hit_round,
            gap_spins=stats.gap_spins,
        )


class NumberFrequencyOut(BaseModel):
    number: str
    hits: int

    @classmethod
    def from_domain(cls, item: NumberFrequency) -> "NumberFrequencyOut":

        return cls(number=item.number, hits=item.hits)


class DashboardSummaryOut(BaseModel):
    current_state: str | None
    current_round_id: int | None
    window_size: int
    color_counts: dict[str, int]
    dozen_counts: dict[int, int]
    column_counts: dict[int, int]
    street_stats: list[StreetStatsOut]
    hot_numbers: list[NumberFrequencyOut]
    cold_numbers: list[NumberFrequencyOut]
    recent_spins: list[SpinOut]

    @classmethod
    def from_domain(cls, summary: DashboardSummary) -> "DashboardSummaryOut":

        return cls(
            current_state=summary.current_state,
            current_round_id=summary.current_round_id,
            window_size=summary.window_size,
            color_counts=summary.color_counts,
            dozen_counts=summary.dozen_counts,
            column_counts=summary.column_counts,
            street_stats=[
                StreetStatsOut.from_domain(item) for item in summary.street_stats
            ],
            hot_numbers=[
                NumberFrequencyOut.from_domain(item) for item in summary.hot_numbers
            ],
            cold_numbers=[
                NumberFrequencyOut.from_domain(item) for item in summary.cold_numbers
            ],
            recent_spins=[SpinOut.from_domain(item) for item in summary.recent_spins],
        )
