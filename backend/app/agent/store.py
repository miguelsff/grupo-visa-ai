"""Sesiones opacas, revisiones y reclamos atómicos de publicación."""

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from secrets import token_urlsafe
from typing import Literal
from uuid import uuid4

from app.agent.facts import SENSITIVE_MARKER
from app.agent.models import ChatResponse, Draft, Extraction, JiraPublication, UserMessage
from app.database import Database


class PublicationNotAvailable(Exception):
    """La revisión no pertenece a la sesión o no está lista para publicar."""


class PublicationInProgress(Exception):
    """Una publicación pendiente impide cambiar la revisión vigente."""


@dataclass(frozen=True)
class PublicationClaim:
    action: Literal["create", "reconcile", "confirmed"]
    marker: str
    preview_title: str = ""
    preview_description: str = ""
    publication: JiraPublication | None = None


class ChatStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def session(self, cookie: str | None) -> tuple[str, str | None]:
        session_id = self.existing_session(cookie)
        if session_id is not None:
            return session_id, None
        token = token_urlsafe(32)
        session_id = sha256(token.encode()).hexdigest()
        with self.database.connect() as connection:
            connection.execute("INSERT INTO chat_sessions(id) VALUES (?)", (session_id,))
        return session_id, token

    def existing_session(self, cookie: str | None) -> str | None:
        if not cookie or len(cookie) > 128:
            return None
        session_id = sha256(cookie.encode()).hexdigest()
        with self.database.connect() as connection:
            found = connection.execute(
                "SELECT 1 FROM chat_sessions WHERE id=?", (session_id,)
            ).fetchone()
        return session_id if found else None

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
            active = connection.execute(
                "SELECT 1 FROM jira_publications WHERE session_id=? AND revision="
                "(SELECT revision FROM chat_sessions WHERE id=?) "
                "AND status IN ('posting', 'uncertain')",
                (session_id, session_id),
            ).fetchone()
            if active:
                raise PublicationInProgress("Verificando publicación… Vuelve a intentarlo después.")
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

    def claim_publication(self, session_id: str, revision: int) -> PublicationClaim:
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            latest = connection.execute(
                "SELECT revision FROM chat_sessions WHERE id=?", (session_id,)
            ).fetchone()
            if latest is None or latest[0] != revision or revision < 1:
                raise PublicationNotAvailable("La revisión no es la vigente de esta sesión.")
            row = connection.execute(
                "SELECT response FROM chat_revisions WHERE session_id=? AND revision=?",
                (session_id, revision),
            ).fetchone()
            if row is None:
                raise PublicationNotAvailable("La revisión no existe en esta sesión.")
            response = ChatResponse.model_validate_json(row[0])
            preview = response.preview
            if (
                response.status != "reviewed"
                or preview is None
                or preview.project_key != "SCRUM"
                or preview.issue_type != "Tarea"
                or not preview.title.strip()
                or not preview.description.strip()
            ):
                raise PublicationNotAvailable(
                    "La revisión vigente no tiene una vista previa publicable."
                )
            attempt = connection.execute(
                "SELECT marker, status, issue_key, issue_url FROM jira_publications "
                "WHERE session_id=? AND revision=? ORDER BY id DESC LIMIT 1",
                (session_id, revision),
            ).fetchone()
            if attempt is not None:
                if attempt["status"] == "confirmed":
                    return PublicationClaim(
                        "confirmed",
                        attempt["marker"],
                        publication=JiraPublication(
                            key=attempt["issue_key"], url=attempt["issue_url"]
                        ),
                    )
                if attempt["status"] in ("posting", "uncertain"):
                    return PublicationClaim("reconcile", attempt["marker"])
            marker = f"ocd-{uuid4().hex}"
            connection.execute(
                "INSERT INTO jira_publications(session_id, revision, marker, status, created_at) "
                "VALUES (?, ?, ?, 'posting', ?)",
                (session_id, revision, marker, datetime.now(UTC).isoformat()),
            )
            return PublicationClaim(
                "create", marker, preview_title=preview.title,
                preview_description=preview.description,
            )

    def publication_uncertain(self, marker: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE jira_publications SET status='uncertain' "
                "WHERE marker=? AND status='posting'", (marker,),
            )

    def publication_rejected(self, marker: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE jira_publications SET status='rejected' "
                "WHERE marker=? AND status='posting'", (marker,),
            )

    def publication_confirmed(self, marker: str, publication: JiraPublication) -> JiraPublication:
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT session_id, revision, status, issue_key, issue_url "
                "FROM jira_publications WHERE marker=?", (marker,),
            ).fetchone()
            if row is None or row["status"] == "rejected":
                raise PublicationNotAvailable("El intento de publicación no está disponible.")
            if row["status"] == "confirmed":
                return JiraPublication(key=row["issue_key"], url=row["issue_url"])
            response_row = connection.execute(
                "SELECT response FROM chat_revisions WHERE session_id=? AND revision=?",
                (row["session_id"], row["revision"]),
            ).fetchone()
            response = ChatResponse.model_validate_json(response_row[0])
            response.publication = publication
            connection.execute(
                "UPDATE chat_revisions SET response=? WHERE session_id=? AND revision=?",
                (response.model_dump_json(), row["session_id"], row["revision"]),
            )
            connection.execute(
                "UPDATE jira_publications SET status='confirmed', issue_key=?, issue_url=? "
                "WHERE marker=?", (publication.key, publication.url, marker),
            )
        return publication
