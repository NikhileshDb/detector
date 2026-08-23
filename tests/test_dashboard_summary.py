from datetime import datetime, timezone

from analytics.dashboard_summary import compute_dashboard_summary
from storage.models import SpinSource, StoredSpin


def make_spin(round_id, number, color):

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


def test_compute_dashboard_summary_basic():

    spins = [
        make_spin(1, "1", "RED"),
        make_spin(2, "1", "RED"),
        make_spin(3, "2", "BLACK"),
        make_spin(4, "0", "GREEN"),
    ]

    summary = compute_dashboard_summary(
        spins,
        current_state="WAITING_FOR_RESULT",
        current_round_id=5,
    )

    assert summary.current_state == "WAITING_FOR_RESULT"
    assert summary.current_round_id == 5
    assert summary.window_size == 4
    assert summary.color_counts == {"RED": 2, "BLACK": 1, "GREEN": 1}
    assert summary.hot_numbers[0].number == "1"
    assert summary.hot_numbers[0].hits == 2
    assert len(summary.street_stats) == 12


def test_compute_dashboard_summary_empty():

    summary = compute_dashboard_summary([])

    assert summary.window_size == 0
    assert summary.color_counts == {"RED": 0, "BLACK": 0, "GREEN": 0}
    assert summary.hot_numbers == []
    assert summary.cold_numbers == []
