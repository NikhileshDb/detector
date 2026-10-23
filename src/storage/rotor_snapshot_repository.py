from datetime import datetime, timezone

from detection.rotor_tracker import RotorState
from storage.database import Database


class RotorSnapshotRepository:
    def __init__(self, database: Database):
        self.database = database

    def save(self, round_id: int, state: RotorState, pocket_at_top: int) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO rotor_snapshots (
                    round_id, zero_angle, rev_per_second, residual_pockets,
                    samples, pocket_at_top, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    round_id, state.zero_angle, state.rev_per_second, state.residual_pockets,
                    state.samples, pocket_at_top, datetime.now(timezone.utc).isoformat(),
                ),
            )

    def with_results(self) -> list[dict]:
        """Snapshots joined to the confirmed result of the same round."""
        with self.database.transaction() as connection:
            rows = connection.execute(
                """
                SELECT r.round_id, r.zero_angle, r.rev_per_second, r.residual_pockets,
                       r.samples, r.pocket_at_top, s.number
                FROM rotor_snapshots r
                JOIN spins s ON s.round_id = r.round_id
                ORDER BY r.round_id
                """
            ).fetchall()
        return [dict(row) for row in rows]
