"""Does the rotor position at bets-closed say anything about the result?

For each spin, the offset is how many pockets (in wheel order) the winning
number sits from the pocket that was under the top of the screen when bets
closed. On an auto wheel that launches the ball at a random time and speed,
offsets are uniform. A cluster of offsets would be a usable signal.
"""
import random
from collections import Counter
from math import sqrt

from analytics.wheel_motion.wheel_order import wheel_index

POCKETS = 37


def offsets(rows: list[dict], direction: int | None = None) -> list[int]:
    """Offsets per spin. ``direction`` +1/-1 keeps only that rotor direction."""
    result = []
    for row in rows:
        if direction is not None and (row["rev_per_second"] > 0) != (direction > 0):
            continue
        result.append((wheel_index(row["number"]) - row["pocket_at_top"]) % POCKETS)
    return result


def best_window(values: list[int], width: int = 5) -> tuple[int, int]:
    """Centre offset and hit count of the busiest ``width``-pocket window."""
    counts = Counter(values)
    half = width // 2
    hits = {centre: sum(counts[(centre + d) % POCKETS] for d in range(-half, half + 1)) for centre in range(POCKETS)}
    centre = max(hits, key=hits.get)
    return centre, hits[centre]


def window_report(values: list[int], width: int = 5, simulations: int = 2000, seed: int = 0) -> dict:
    """Busiest window against what chance produces for the same sample size.

    The p-value is corrected for picking the best of 37 windows: it is the
    share of uniform random samples whose best window does at least as well.
    """
    n = len(values)
    if n == 0:
        return {"spins": 0}
    centre, hits = best_window(values, width)
    rng = random.Random(seed)
    as_good = sum(
        best_window([rng.randrange(POCKETS) for _ in range(n)], width)[1] >= hits
        for _ in range(simulations)
    )
    fair = width / POCKETS
    rate = hits / n
    return {
        "spins": n,
        "window": width,
        "centre_offset": centre,
        "hit_rate": rate,
        "fair_rate": fair,
        "standard_error": sqrt(fair * (1 - fair) / n),
        "p_value": (as_good + 1) / (simulations + 1),
    }


if __name__ == "__main__":
    from storage.database import Database
    from storage.rotor_snapshot_repository import RotorSnapshotRepository

    rows = RotorSnapshotRepository(Database()).with_results()
    for label, direction in (("all", None), ("clockwise", 1), ("anticlockwise", -1)):
        report = window_report(offsets(rows, direction))
        if report["spins"] == 0:
            print(f"{label}: no spins yet")
            continue
        print(
            f"{label}: {report['spins']} spins, best 5-pocket window at offset "
            f"{report['centre_offset']} hit {report['hit_rate']:.1%} "
            f"(fair {report['fair_rate']:.1%}), p={report['p_value']:.3f}"
        )
