"""Publicación de la revisión vigente con Jira simulado, sin red externa."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event

import pytest
from fastapi.testclient import TestClient

from app.agent.models import ChatResponse, Draft, Extraction, JiraPreview
from app.agent.publication import PublicationPending, PublicationService
from app.agent.store import ChatStore, PublicationInProgress
from app.config import Settings
from app.database import Database
from app.integrations.jira import JiraIssue, JiraRejectedError, JiraUncertainError
from app.main import create_app

AUTH = ("demo", "clave-de-prueba")
ISSUE = JiraIssue("SCRUM-41", "https://grupo-visai.atlassian.net/browse/SCRUM-41")


class FakeJira:
    def __init__(self) -> None:
        self.posts: list[tuple[str, str, str]] = []
        self.visible = False
        self.uncertain = False
        self.rejected = False
        self.started = Event()
        self.release = Event()
        self.block = False

    def create_issue(self, title: str, description: str, marker: str) -> JiraIssue:
        self.posts.append((title, description, marker))
        self.started.set()
        if self.block:
            assert self.release.wait(5)
        if self.rejected:
            raise JiraRejectedError("Jira rechazó la creación.")
        if self.uncertain:
            raise JiraUncertainError("Respuesta incierta.")
        self.visible = True
        return ISSUE

    def find_issue(self, marker: str) -> JiraIssue | None:
        return ISSUE if self.visible and any(post[2] == marker for post in self.posts) else None


def reviewed(
    store: ChatStore, title: str = "Título exacto", description: str = "Línea 1\nLínea 2"
) -> tuple[str, str]:
    session_id, token = store.session(None)
    response = ChatResponse(
        revision=1,
        status="reviewed",
        answer="Revisión completa.",
        draft=Draft(),
        preview=JiraPreview(
            project_key="SCRUM", issue_type="Tarea", title=title,
            description=description, pending=["evidencia"],
        ),
    )
    with store.database.connect() as connection:
        connection.execute("UPDATE chat_sessions SET revision=1 WHERE id=?", (session_id,))
        connection.execute(
            "INSERT INTO chat_revisions(session_id, revision, response, created_at) "
            "VALUES (?, 1, ?, '2026-11-13T00:00:00Z')",
            (session_id, response.model_dump_json()),
        )
    assert token is not None
    return session_id, token


def client_settings(settings: Settings) -> Settings:
    return replace(settings, demo_password=AUTH[1])


def test_publish_uses_saved_preview_and_survives_restart(settings: Settings) -> None:
    fake = FakeJira()
    configured = client_settings(settings)
    with TestClient(create_app(configured, jira=fake)) as client:
        store = ChatStore(Database(configured.database_path))
        _, token = reviewed(store, "  Título sin modificar  ", "Primera línea\n\nÚltima línea")
        client.cookies.set("ocd_session", token, path="/api/chat")
        response = client.post(
            "/api/chat/revisions/1/publish",
            json={"title": "Título inyectado", "description": "Descripción inyectada"},
            auth=AUTH,
        )
        assert response.status_code == 201
        assert response.json() == {"key": ISSUE.key, "url": ISSUE.url}
        assert fake.posts[0][:2] == ("  Título sin modificar  ", "Primera línea\n\nÚltima línea")
        assert fake.posts[0][2].startswith("ocd-")
        assert token not in fake.posts[0][2]
        assert client.post("/api/chat/revisions/1/publish", auth=AUTH).status_code == 200
        assert len(fake.posts) == 1
        assert client.get("/api/chat", auth=AUTH).json()["publication"] == response.json()
        assert (
            client.get("/api/chat/revisions/1", auth=AUTH).json()["publication"]
            == response.json()
        )
    with TestClient(create_app(configured, jira=fake)) as restarted:
        restarted.cookies.set("ocd_session", token, path="/api/chat")
        assert restarted.get("/api/chat", auth=AUTH).json()["publication"] == response.json()
        assert restarted.post("/api/chat/revisions/1/publish", auth=AUTH).status_code == 200
        assert len(fake.posts) == 1


def test_publish_requires_auth_and_owned_current_review(settings: Settings) -> None:
    fake = FakeJira()
    configured = client_settings(settings)
    with TestClient(create_app(configured, jira=fake)) as client:
        store = ChatStore(Database(configured.database_path))
        session_id, token = reviewed(store)
        assert client.post("/api/chat/revisions/1/publish").status_code == 401
        client.cookies.set("ocd_session", "otra-sesion", path="/api/chat")
        assert client.post("/api/chat/revisions/1/publish", auth=AUTH).status_code == 404
        client.cookies.set("ocd_session", token, path="/api/chat")
        with store.database.connect() as connection:
            connection.execute("UPDATE chat_sessions SET revision=2 WHERE id=?", (session_id,))
        assert client.post("/api/chat/revisions/1/publish", auth=AUTH).status_code == 409
        assert fake.posts == []


def test_pending_preview_cannot_publish(settings: Settings) -> None:
    fake = FakeJira()
    configured = client_settings(settings)
    with TestClient(create_app(configured, jira=fake)) as client:
        store = ChatStore(Database(configured.database_path))
        session_id, token = reviewed(store)
        with store.database.connect() as connection:
            row = connection.execute(
                "SELECT response FROM chat_revisions WHERE session_id=?", (session_id,)
            ).fetchone()
            response = ChatResponse.model_validate_json(row[0])
            response.status = "unavailable"
            connection.execute(
                "UPDATE chat_revisions SET response=? WHERE session_id=?",
                (response.model_dump_json(), session_id),
            )
        client.cookies.set("ocd_session", token, path="/api/chat")
        assert client.post("/api/chat/revisions/1/publish", auth=AUTH).status_code == 409
        assert fake.posts == []


def test_uncertain_result_reconciles_without_second_post(settings: Settings) -> None:
    store = ChatStore(Database(settings.database_path))
    store.database.initialize()
    session_id, _ = reviewed(store)
    fake = FakeJira()
    fake.uncertain = True
    service = PublicationService(store, fake)
    with pytest.raises(PublicationPending, match="Verificando publicación"):
        service.publish(session_id, 1)
    with pytest.raises(PublicationPending):
        service.publish(session_id, 1)
    assert len(fake.posts) == 1
    assert store.get(session_id).publication is None
    fake.visible = True
    result, created = service.publish(session_id, 1)
    assert result.key == ISSUE.key and not created
    assert store.get(session_id).publication == result
    assert len(fake.posts) == 1


def test_uncertain_http_result_is_not_success(settings: Settings) -> None:
    fake = FakeJira()
    fake.uncertain = True
    configured = client_settings(settings)
    with TestClient(create_app(configured, jira=fake)) as client:
        store = ChatStore(Database(configured.database_path))
        _, token = reviewed(store)
        client.cookies.set("ocd_session", token, path="/api/chat")
        first = client.post("/api/chat/revisions/1/publish", auth=AUTH)
        second = client.post("/api/chat/revisions/1/publish", auth=AUTH)
        assert first.status_code == second.status_code == 503
        assert "Verificando publicación" in first.json()["detail"]
        assert "key" not in first.json()
        assert len(fake.posts) == 1
        fake.visible = True
        reconciled = client.post("/api/chat/revisions/1/publish", auth=AUTH)
        assert reconciled.status_code == 200
        assert reconciled.json()["key"] == ISSUE.key


def test_parallel_click_and_edit_do_not_duplicate(settings: Settings) -> None:
    store = ChatStore(Database(settings.database_path))
    store.database.initialize()
    session_id, _ = reviewed(store)
    fake = FakeJira()
    fake.block = True
    service = PublicationService(store, fake)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(service.publish, session_id, 1)
        assert fake.started.wait(5)
        with pytest.raises(PublicationPending):
            service.publish(session_id, 1)
        with pytest.raises(PublicationInProgress):
            store.merge(session_id, Extraction(categories=[], facts=[]), [])
        fake.release.set()
        assert first.result(timeout=5)[0].key == ISSUE.key
    assert service.publish(session_id, 1)[0].key == ISSUE.key
    assert len(fake.posts) == 1
    assert store.get(session_id).revision == 1


def test_definitive_rejection_allows_new_marker(settings: Settings) -> None:
    store = ChatStore(Database(settings.database_path))
    store.database.initialize()
    session_id, _ = reviewed(store)
    fake = FakeJira()
    fake.rejected = True
    service = PublicationService(store, fake)
    with pytest.raises(JiraRejectedError):
        service.publish(session_id, 1)
    fake.rejected = False
    assert service.publish(session_id, 1)[0].key == ISSUE.key
    assert len(fake.posts) == 2
    assert fake.posts[0][2] != fake.posts[1][2]
