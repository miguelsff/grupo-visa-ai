"""SQLite local. No carga ni consulta conocimiento documental."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.schemas import Greeting


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS greetings (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL,
                    message TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY, revision INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES chat_sessions(id),
                    content TEXT NOT NULL, extracted INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS chat_messages_session ON chat_messages(session_id);
                CREATE TABLE IF NOT EXISTS chat_revisions (
                    session_id TEXT NOT NULL REFERENCES chat_sessions(id),
                    revision INTEGER NOT NULL, response TEXT NOT NULL,
                    created_at TEXT NOT NULL, PRIMARY KEY(session_id, revision)
                );
                CREATE TABLE IF NOT EXISTS jira_publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    marker TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK(
                        status IN ('posting', 'uncertain', 'confirmed', 'rejected')
                    ),
                    issue_key TEXT, issue_url TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id, revision)
                        REFERENCES chat_revisions(session_id, revision)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS jira_publications_active
                    ON jira_publications(session_id, revision)
                    WHERE status IN ('posting', 'uncertain', 'confirmed');
            """)

    def available(self) -> None:
        with self.connect() as connection:
            connection.execute("SELECT 1").fetchone()

    def create_greeting(self, name: str, message: str) -> Greeting:
        greeting = Greeting(
            id=str(uuid4()), name=name, message=message, created_at=datetime.now(UTC)
        )
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO greetings VALUES (?, ?, ?, ?)",
                (greeting.id, greeting.name, greeting.message, greeting.created_at.isoformat()),
            )
        return greeting

    def list_greetings(self) -> list[Greeting]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM greetings ORDER BY created_at DESC, id DESC LIMIT 5"
            ).fetchall()
        return [Greeting.model_validate(dict(row)) for row in rows]
