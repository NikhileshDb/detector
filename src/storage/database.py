import sqlite3
from datetime import datetime, timezone
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

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0
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


                CREATE TABLE IF NOT EXISTS capture_stats (
                    round_id INTEGER PRIMARY KEY,
                    frames INTEGER NOT NULL,
                    unique_frames INTEGER NOT NULL,
                    duration_seconds REAL NOT NULL,
                    stream_fps REAL NOT NULL,
                    duplicate_ratio REAL NOT NULL,
                    wheel_view_ratio REAL NULL,
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY (round_id)
                    REFERENCES rounds(id)
                    ON DELETE CASCADE
                );


                CREATE TABLE IF NOT EXISTS rotor_snapshots (
                    round_id INTEGER PRIMARY KEY,
                    zero_angle REAL NOT NULL,
                    rev_per_second REAL NOT NULL,
                    residual_pockets REAL NOT NULL,
                    samples INTEGER NOT NULL,
                    pocket_at_top INTEGER NOT NULL,
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY (round_id)
                    REFERENCES rounds(id)
                    ON DELETE CASCADE
                );
                """
            )

            columns = {row["name"] for row in connection.execute("PRAGMA table_info(rounds)")}
            if "session_id" not in columns:
                connection.execute("ALTER TABLE rounds ADD COLUMN session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE")
            active = connection.execute("SELECT id FROM sessions WHERE is_active = 1 LIMIT 1").fetchone()
            if active is None:
                now = datetime.now(timezone.utc).isoformat()
                connection.execute("INSERT INTO sessions(name, started_at, is_active) VALUES (?, ?, 1)", ("Legacy session", now))
                session_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
                connection.execute("UPDATE rounds SET session_id = ? WHERE session_id IS NULL", (session_id,))
