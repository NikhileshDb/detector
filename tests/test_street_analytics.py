from datetime import datetime, timezone

from analytics.street_analytics import compute_street_stats
from storage.models import SpinSource, StoredSpin


def make_spin(round_id, number, color="RED"):

    return StoredSpin(
        id=f"spin-{round_id}",
        round_id=round_id,
        number=number,
        color=color,
        source=SpinSource.AUTO,
        confidence=0.9,
        original_number=None,
        detected_at=datetime.now(timezone.utc),
    )


def test_compute_street_stats_counts_and_gap():

    # most-recent-first, matching SpinRepository.recent()
    spins = [make_spin(3, "4"), make_spin(2, "1"), make_spin(1, "1")]

    stats = {item.street: item for item in compute_street_stats(spins)}

    assert stats[1].hits == 2
    assert stats[1].last_hit_round == 2
    assert stats[1].gap_spins == 1

    assert stats[2].hits == 1
    assert stats[2].last_hit_round == 3
    assert stats[2].gap_spins == 0

    assert stats[3].hits == 0
    assert stats[3].last_hit_round is None
    assert stats[3].gap_spins is None


def test_compute_street_stats_skips_zero_and_double_zero():

    spins = [make_spin(1, "0", "GREEN"), make_spin(2, "00", "GREEN")]

    stats = compute_street_stats(spins)

    assert all(item.hits == 0 for item in stats)
