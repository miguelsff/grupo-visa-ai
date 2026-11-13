"""Persistencia SQLite y búsqueda FTS5."""

import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.knowledge.loader import Document
from app.schemas import Greeting, KnowledgeMatch


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self, documents: list[Document]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS greetings "
                "(id TEXT PRIMARY KEY, name TEXT NOT NULL, message TEXT NOT NULL, "
                "created_at TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5("
                "code UNINDEXED, title, content, url UNINDEXED, version UNINDEXED, "
                "tokenize='unicode61 remove_diacritics 2')"
            )
            connection.execute("DELETE FROM documents")
            connection.executemany(
                "INSERT INTO documents (code, title, content, url, version) VALUES (?, ?, ?, ?, ?)",
                [(doc.code, doc.title, doc.content, doc.url, doc.version) for doc in documents],
            )

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

    def counts(self) -> tuple[int, int]:
        with self.connect() as connection:
            documents = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            greetings = connection.execute("SELECT COUNT(*) FROM greetings").fetchone()[0]
            connection.execute(
                "SELECT code FROM documents WHERE documents MATCH ? LIMIT 1", ('"OCD"',)
            ).fetchall()
        return documents, greetings

    def search(self, query: str) -> list[KnowledgeMatch]:
        words = re.findall(r"\w+", query, flags=re.UNICODE)
        if not words:
            return []
        expression = " OR ".join(f'"{word}"' for word in words)
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT code, title, url, version, "
                "snippet(documents, 2, '', '', '…', 24) AS excerpt "
                "FROM documents WHERE documents MATCH ? ORDER BY rank LIMIT 5",
                (expression,),
            ).fetchall()
        return [KnowledgeMatch.model_validate(dict(row)) for row in rows]
