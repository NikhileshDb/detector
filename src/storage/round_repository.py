from datetime import datetime, timezone

from storage.database import Database
from storage.models import (
    RoundStatus,
    StoredRound,
)


class RoundRepository:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    def create(
        self,
        sequence: int,
    ) -> StoredRound:

        now = datetime.now(
            timezone.utc
        )

        with self.database.connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO rounds (
                    sequence,
                    status,
                    started_at,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    sequence,
                    RoundStatus.ACTIVE.value,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            round_id = cursor.lastrowid

        return StoredRound(
            id=round_id,
            sequence=sequence,
            status=RoundStatus.ACTIVE,
            started_at=now,
            completed_at=None,
        )

    def get_by_sequence(
        self,
        sequence: int,
    ) -> StoredRound | None:

        with self.database.connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM rounds
                WHERE sequence = ?
                """,
                (sequence,),
            ).fetchone()

        if row is None:
            return None

        return self._map(row)

    def get_by_id(
        self,
        round_id: int,
        connection=None,
    ) -> StoredRound | None:

        if connection is not None:

            row = connection.execute(
                """
                SELECT *
                FROM rounds
                WHERE id = ?
                """,
                (round_id,),
            ).fetchone()

        else:

            with self.database.connect() as conn:

                row = conn.execute(
                    """
                    SELECT *
                    FROM rounds
                    WHERE id = ?
                    """,
                    (round_id,),
                ).fetchone()

        if row is None:
            return None

        return self._map(row)

    def mark_waiting_for_result(
        self,
        round_id: int,
    ) -> None:

        self._set_status(
            round_id,
            RoundStatus.WAITING_FOR_RESULT,
        )

    def mark_missing(
        self,
        round_id: int,
    ) -> None:

        self._set_status(
            round_id,
            RoundStatus.MISSING,
        )

    def mark_completed(
        self,
        round_id: int,
        connection=None,
    ) -> None:

        now = datetime.now(
            timezone.utc
        )

        if connection is not None:

            connection.execute(
                """
                UPDATE rounds
                SET
                    status = ?,
                    completed_at = ?
                WHERE id = ?
                """,
                (
                    RoundStatus.COMPLETED.value,
                    now.isoformat(),
                    round_id,
                ),
            )

        else:

            with self.database.connect() as conn:

                conn.execute(
                    """
                    UPDATE rounds
                    SET
                        status = ?,
                        completed_at = ?
                    WHERE id = ?
                    """,
                    (
                        RoundStatus.COMPLETED.value,
                        now.isoformat(),
                        round_id,
                    ),
                )

    def latest(
        self,
    ) -> StoredRound | None:

        with self.database.connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM rounds
                ORDER BY sequence DESC
                LIMIT 1
                """
            ).fetchone()

        if row is None:
            return None

        return self._map(row)

    def recent(
        self,
        limit: int = 50,
    ) -> list[StoredRound]:

        with self.database.connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM rounds
                ORDER BY sequence DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            self._map(row)
            for row in rows
        ]

    def _set_status(
        self,
        round_id: int,
        status: RoundStatus,
    ) -> None:

        with self.database.connect() as connection:

            connection.execute(
                """
                UPDATE rounds
                SET status = ?
                WHERE id = ?
                """,
                (
                    status.value,
                    round_id,
                ),
            )

    def _map(
        self,
        row,
    ) -> StoredRound:

        return StoredRound(
            id=row["id"],
            sequence=row["sequence"],
            status=RoundStatus(
                row["status"]
            ),
            started_at=datetime.fromisoformat(
                row["started_at"]
            ),
            completed_at=(
                datetime.fromisoformat(
                    row["completed_at"]
                )
                if row["completed_at"]
                else None
            ),
        )
