from datetime import datetime, timezone

from analytics.capture_stats import RoundCaptureStats
from storage.database import Database


class CaptureStatsRepository:
    def __init__(self, database: Database):
        self.database = database

    def save(self, round_id: int, stats: RoundCaptureStats) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO capture_stats (
                    round_id, frames, unique_frames, duration_seconds,
                    stream_fps, duplicate_ratio, wheel_view_ratio, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    round_id, stats.frames, stats.unique_frames, stats.duration_seconds,
                    stats.stream_fps, stats.duplicate_ratio, stats.wheel_view_ratio,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get(self, round_id: int) -> RoundCaptureStats | None:
        with self.database.transaction() as connection:
            row = connection.execute("SELECT * FROM capture_stats WHERE round_id = ?", (round_id,)).fetchone()
        if row is None: return None
        return RoundCaptureStats(
            frames=row["frames"],
            unique_frames=row["unique_frames"],
            duration_seconds=row["duration_seconds"],
            stream_fps=row["stream_fps"],
            duplicate_ratio=row["duplicate_ratio"],
            wheel_view_ratio=row["wheel_view_ratio"],
        )
