import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator


DATABASE_PATH = "data/roulette.db"


class Database:
    def __init__(
        self,
        path: str = DATABASE_PATH,
    ):
        self.path = path

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def connect(
        self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    @contextmanager
    def transaction(
        self,
    ) -> Iterator[sqlite3.Connection]:

        with closing(self.connect()) as connection:

            with connection:
                yield connection

    def initialize(
        self,
    ) -> None:

        with self.connect() as connection:

            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    sequence INTEGER NOT NULL UNIQUE,

                    status TEXT NOT NULL,

                    started_at TEXT NOT NULL,

                    completed_at TEXT NULL,

                    created_at TEXT NOT NULL
                );


                CREATE TABLE IF NOT EXISTS spins (
                    id TEXT PRIMARY KEY,

                    round_id INTEGER NOT NULL UNIQUE,

                    number TEXT NOT NULL,

                    color TEXT NOT NULL,

                    source TEXT NOT NULL,

                    confidence REAL NULL,

                    original_number TEXT NULL,

                    detected_at TEXT NOT NULL,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (
                        round_id
                    )
                    REFERENCES rounds(id)
                    ON DELETE CASCADE
                );


                CREATE INDEX IF NOT EXISTS
                idx_rounds_sequence
                ON rounds(sequence);


                CREATE INDEX IF NOT EXISTS
                idx_spins_detected_at
                ON spins(detected_at);
                """
            )
