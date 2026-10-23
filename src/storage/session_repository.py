from datetime import datetime, timezone

from storage.database import Database


class SessionRepository:
    def __init__(self, database: Database):
        self.database = database

    def list(self) -> list[dict]:
        with self.database.connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM sessions ORDER BY started_at DESC")]

    def start(self, name: str | None = None) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as connection:
            connection.execute("UPDATE sessions SET is_active = 0, ended_at = COALESCE(ended_at, ?) WHERE is_active = 1", (now,))
            cursor = connection.execute("INSERT INTO sessions(name, started_at, is_active) VALUES (?, ?, 1)", (name or f"Session {now[:19].replace('T', ' ')}", now))
            return dict(connection.execute("SELECT * FROM sessions WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def active(self) -> dict:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE is_active = 1 LIMIT 1").fetchone()
            return dict(row)

    def delete(self, session_id: int) -> bool:
        with self.database.connect() as connection:
            row = connection.execute("SELECT is_active FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if row is None:
                return False
            if row["is_active"]:
                raise ValueError("The active session cannot be deleted. Start another session first.")
            connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return True
