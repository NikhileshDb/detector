from collections import Counter
from dataclasses import dataclass

from analytics.street_analytics import (
    StreetStats,
    compute_street_stats,
)
from domain.roulette_table import column_of, dozen_of
from storage.models import StoredSpin


@dataclass(frozen=True)
class NumberFrequency:
    number: str
    hits: int


@dataclass(frozen=True)
class DashboardSummary:
    current_state: str | None
    current_round_id: int | None
    window_size: int
    color_counts: dict[str, int]
    dozen_counts: dict[int, int]
    column_counts: dict[int, int]
    street_stats: list[StreetStats]
    hot_numbers: list[NumberFrequency]
    cold_numbers: list[NumberFrequency]
    recent_spins: list[StoredSpin]


def compute_dashboard_summary(
    spins: list[StoredSpin],
    current_state: str | None = None,
    current_round_id: int | None = None,
    hot_cold_count: int = 5,
) -> DashboardSummary:
    """`spins` must be ordered most-recent-first, matching SpinRepository.recent()."""

    color_counts = {"RED": 0, "BLACK": 0, "GREEN": 0}
    dozen_counts = {1: 0, 2: 0, 3: 0}
    column_counts = {1: 0, 2: 0, 3: 0}

    number_frequency: Counter[str] = Counter()

    for spin in spins:

        color_counts[spin.color] = color_counts.get(spin.color, 0) + 1

        number_frequency[spin.number] += 1

        try:
            number = int(spin.number)
        except ValueError:
            continue

        dozen = dozen_of(number)

        if dozen is not None:
            dozen_counts[dozen] += 1

        column = column_of(number)

        if column is not None:
            column_counts[column] += 1

    ranked = number_frequency.most_common()

    hot_numbers = [
        NumberFrequency(number=number, hits=hits)
        for number, hits in ranked[:hot_cold_count]
    ]

    cold_numbers = [
        NumberFrequency(number=number, hits=hits)
        for number, hits in ranked[-hot_cold_count:][::-1]
    ]

    return DashboardSummary(
        current_state=current_state,
        current_round_id=current_round_id,
        window_size=len(spins),
        color_counts=color_counts,
        dozen_counts=dozen_counts,
        column_counts=column_counts,
        street_stats=compute_street_stats(spins),
        hot_numbers=hot_numbers,
        cold_numbers=cold_numbers,
        recent_spins=spins,
    )
