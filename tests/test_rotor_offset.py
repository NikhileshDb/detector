import random

from analytics.rotor_offset import best_window, offsets, window_report
from analytics.wheel_motion.wheel_order import WHEEL_ORDER
from detection.rotor_tracker import RotorState
from storage.rotor_snapshot_repository import RotorSnapshotRepository


def _row(number, pocket_at_top, rev=0.2):
    return {"number": str(number), "pocket_at_top": pocket_at_top, "rev_per_second": rev}


def test_offsets_use_wheel_order_and_direction():
    rows = [
        _row(WHEEL_ORDER[5], 3),
        _row(WHEEL_ORDER[1], 36, rev=-0.2),
    ]

    assert offsets(rows) == [2, 2]
    assert offsets(rows, direction=1) == [2]
    assert offsets(rows, direction=-1) == [2]


def test_best_window_wraps_around_zero():
    centre, hits = best_window([36, 0, 1, 36, 0, 10], width=5)

    assert centre in (36, 0)
    assert hits == 5


def test_uniform_offsets_are_not_significant():
    rng = random.Random(1)
    report = window_report([rng.randrange(37) for _ in range(400)], simulations=300)

    assert report["p_value"] > 0.05


def test_clustered_offsets_are_significant():
    rng = random.Random(2)
    values = [rng.randrange(37) for _ in range(300)] + [(10 + rng.randint(-2, 2)) % 37 for _ in range(60)]
    report = window_report(values, simulations=300)

    assert report["centre_offset"] in range(8, 13)
    assert report["p_value"] < 0.01


def test_empty_report():
    assert window_report([]) == {"spins": 0}


def test_repository_joins_results(database, round_repository, spin_repository):
    from storage.models import SpinSource

    stored_round = round_repository.create(sequence=1)
    spin_repository.create(round_id=stored_round.id, number="26", color="BLACK", source=SpinSource.AUTO)
    repository = RotorSnapshotRepository(database)
    state = RotorState(timestamp=1.0, zero_angle=0.5, rev_per_second=-0.24, residual_pockets=0.3, samples=30)

    repository.save(stored_round.id, state, pocket_at_top=4)

    rows = repository.with_results()
    assert len(rows) == 1
    assert rows[0]["number"] == "26"
    assert rows[0]["pocket_at_top"] == 4
    assert offsets(rows) == [(1 - 4) % 37]


def test_first_snapshot_for_a_round_wins(database, round_repository):
    stored_round = round_repository.create(sequence=1)
    repository = RotorSnapshotRepository(database)
    first = RotorState(timestamp=1.0, zero_angle=0.5, rev_per_second=0.24, residual_pockets=0.2, samples=30)
    later = RotorState(timestamp=9.0, zero_angle=2.0, rev_per_second=0.24, residual_pockets=0.2, samples=30)

    assert repository.save(stored_round.id, first, pocket_at_top=4)
    assert not repository.save(stored_round.id, later, pocket_at_top=20)

    with database.transaction() as connection:
        row = connection.execute("SELECT pocket_at_top FROM rotor_snapshots").fetchone()
    assert row["pocket_at_top"] == 4


def test_consistent_drops_pairs_with_unusual_timing():
    from analytics.rotor_offset import consistent

    def row(gap):
        return {"recorded_at": "2026-10-23T13:00:00+00:00", "detected_at": f"2026-10-23T13:00:{gap:02d}+00:00"}

    rows = [row(22), row(24), row(25), row(27), row(9), row(50)]

    kept = consistent(rows)

    assert [r["detected_at"][-8:-6] for r in kept] == ["22", "24", "25", "27"]
    assert consistent([]) == []
