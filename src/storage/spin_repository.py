import uuid
from datetime import datetime, timezone

from storage.database import Database
from storage.models import (
    SpinSource,
    StoredSpin,
)


class SpinRepository:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    def create(
        self,
        round_id: int,
        number: str,
        color: str,
        source: SpinSource,
        confidence: float | None = None,
        original_number: str | None = None,
    ) -> StoredSpin:

        spin_id = str(
            uuid.uuid4()
        )

        now = datetime.now(
            timezone.utc
        )

        with self.database.connect() as connection:

            connection.execute(
                """
                INSERT INTO spins (
                    id,
                    round_id,
                    number,
                    color,
                    source,
                    confidence,
                    original_number,
                    detected_at,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    spin_id,
                    round_id,
                    number,
                    color,
                    source.value,
                    confidence,
                    original_number,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

        return StoredSpin(
            id=spin_id,
            round_id=round_id,
            number=number,
            color=color,
            source=source,
            confidence=confidence,
            original_number=original_number,
            detected_at=now,
        )

    def get_by_round(
        self,
        round_id: int,
    ) -> StoredSpin | None:

        with self.database.connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM spins
                WHERE round_id = ?
                """,
                (round_id,),
            ).fetchone()

        if row is None:
            return None

        return self._map(row)

    def recent(
        self,
        limit: int = 100,
    ) -> list[StoredSpin]:

        with self.database.connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM spins
                ORDER BY detected_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            self._map(row)
            for row in rows
        ]

    def update_correction(
        self,
        round_id: int,
        corrected_number: str,
        corrected_color: str,
    ) -> None:

        existing = self.get_by_round(
            round_id
        )

        if existing is None:
            raise ValueError(
                f"No spin exists for round {round_id}"
            )

        with self.database.connect() as connection:

            connection.execute(
                """
                UPDATE spins
                SET
                    original_number = ?,
                    number = ?,
                    color = ?,
                    source = ?
                WHERE round_id = ?
                """,
                (
                    existing.number,
                    corrected_number,
                    corrected_color,
                    SpinSource.CORRECTED.value,
                    round_id,
                ),
            )

    def _map(
        self,
        row,
    ) -> StoredSpin:

        return StoredSpin(
            id=row["id"],
            round_id=row["round_id"],
            number=row["number"],
            color=row["color"],
            source=SpinSource(
                row["source"]
            ),
            confidence=row["confidence"],
            original_number=row[
                "original_number"
            ],
            detected_at=datetime.fromisoformat(
                row["detected_at"]
            ),
        )
