"""Sesiones opacas y revisiones inmutables con combinación atómica de hechos."""

from datetime import UTC, datetime
from hashlib import sha256
from secrets import token_urlsafe

from app.agent.facts import SENSITIVE_MARKER
from app.agent.models import ChatResponse, Draft, Extraction, UserMessage
from app.database import Database


class ChatStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def session(self, cookie: str | None) -> tuple[str, str | None]:
        if cookie and len(cookie) <= 128:
            session_id = sha256(cookie.encode()).hexdigest()
            with self.database.connect() as connection:
                if connection.execute(
                    "SELECT 1 FROM chat_sessions WHERE id=?", (session_id,)
                ).fetchone():
                    return session_id, None
        token = token_urlsafe(32)
        session_id = sha256(token.encode()).hexdigest()
        with self.database.connect() as connection:
            connection.execute("INSERT INTO chat_sessions(id) VALUES (?)", (session_id,))
        return session_id, token

    def append(self, session_id: str, content: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO chat_messages(session_id, content, created_at) VALUES (?, ?, ?)",
                (session_id, content, datetime.now(UTC).isoformat()),
            )

    def pending(self, session_id: str) -> list[UserMessage]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT id, content FROM chat_messages WHERE session_id=? AND extracted=0 "
                "ORDER BY id",
                (session_id,),
            ).fetchall()
        return [UserMessage.model_validate(dict(row)) for row in rows]

    def get(self, session_id: str, revision: int | None = None) -> ChatResponse:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT response FROM chat_revisions WHERE session_id=? "
                "AND (? IS NULL OR revision=?) ORDER BY revision DESC LIMIT 1",
                (session_id, revision, revision),
            ).fetchone()
        if row is None:
            return ChatResponse(
                revision=0,
                status="pending",
                answer="Describe el cambio que necesitas preparar.",
                draft=Draft(),
            )
        return ChatResponse.model_validate_json(row[0])

    def merge(
        self, session_id: str, patch: Extraction, messages: list[UserMessage]
    ) -> ChatResponse:
        # La extracción ocurre fuera de esta transacción. Se combina con la última revisión.
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT response FROM chat_revisions WHERE session_id=? "
                "ORDER BY revision DESC LIMIT 1",
                (session_id,),
            ).fetchone()
            current = ChatResponse.model_validate_json(row[0]) if row else None
            if messages:
                unprocessed = {
                    r[0]
                    for r in connection.execute(
                        "SELECT id FROM chat_messages WHERE session_id=? AND extracted=0",
                        (session_id,),
                    )
                }
                messages = [m for m in messages if m.id in unprocessed]
                if not messages and current is not None:
                    return current
                admitted = {m.id for m in messages}
                patch = Extraction(
                    categories=[c for c in patch.categories if c.message_id in admitted],
                    facts=[f for f in patch.facts if f.message_id in admitted],
                )
            draft = current.draft if current else Draft()
            draft.sensitive_detected |= any(SENSITIVE_MARKER in m.content for m in messages)
            for item in patch.categories:
                if item.message_id < draft.category_messages.get(item.category, 0):
                    continue
                draft.category_messages[item.category] = item.message_id
                if item.selected and item.category not in draft.categories:
                    draft.categories.append(item.category)
                elif not item.selected and item.category in draft.categories:
                    draft.categories.remove(item.category)
                    draft.facts = {
                        key: fact
                        for key, fact in draft.facts.items()
                        if fact.scope != item.category
                    }
            for fact in patch.facts:
                if fact.scope != "comun" and fact.scope not in draft.categories:
                    continue
                key = f"{fact.scope}.{fact.name}"
                previous = draft.facts.get(key)
                if previous is None or fact.message_id >= previous.message_id:
                    draft.facts[key] = fact
            revision = connection.execute(
                "UPDATE chat_sessions SET revision=revision+1 WHERE id=? RETURNING revision",
                (session_id,),
            ).fetchone()[0]
            result = ChatResponse(
                revision=revision,
                status="pending",
                draft=draft,
                answer="Borrador guardado. Revisión documental pendiente.",
            )
            connection.execute(
                "INSERT INTO chat_revisions VALUES (?, ?, ?, ?)",
                (session_id, revision, result.model_dump_json(), datetime.now(UTC).isoformat()),
            )
            connection.executemany(
                "UPDATE chat_messages SET extracted=1 WHERE session_id=? AND id=?",
                [(session_id, message.id) for message in messages],
            )
        return result

    def finish(self, session_id: str, result: ChatResponse) -> None:
        # Una respuesta tardía solo completa su revisión, nunca reemplaza otra posterior.
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE chat_revisions SET response=? WHERE session_id=? AND revision=?",
                (result.model_dump_json(), session_id, result.revision),
            )
