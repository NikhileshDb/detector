from dataclasses import dataclass

from domain.roulette_table import (
    STREET_COUNT,
    numbers_in_street,
    street_of,
)
from storage.models import StoredSpin


@dataclass(frozen=True)
class StreetStats:
    street: int
    numbers: tuple[int, int, int]
    hits: int
    last_hit_round: int | None
    gap_spins: int | None


def compute_street_stats(
    spins: list[StoredSpin],
) -> list[StreetStats]:
    """`spins` must be ordered most-recent-first, matching SpinRepository.recent()."""

    hits = {street: 0 for street in range(1, STREET_COUNT + 1)}
    last_hit_round: dict[int, int | None] = {
        street: None for street in range(1, STREET_COUNT + 1)
    }
    gap_spins: dict[int, int | None] = {
        street: None for street in range(1, STREET_COUNT + 1)
    }

    for index, spin in enumerate(spins):

        try:
            number = int(spin.number)
        except ValueError:
            continue

        if number == 0:
            continue

        street = street_of(number)

        hits[street] += 1

        if last_hit_round[street] is None:
            last_hit_round[street] = spin.round_id
            gap_spins[street] = index

    return [
        StreetStats(
            street=street,
            numbers=numbers_in_street(street),
            hits=hits[street],
            last_hit_round=last_hit_round[street],
            gap_spins=gap_spins[street],
        )
        for street in range(1, STREET_COUNT + 1)
    ]
