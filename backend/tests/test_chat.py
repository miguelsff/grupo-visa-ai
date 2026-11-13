"""Flujo persistente, aislamiento, fallos y actualizaciones concurrentes."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor

from conftest import FakeKnowledge, FakeModel
from fastapi.testclient import TestClient

from app.agent.chat import ChatService
from app.agent.models import Draft, Extraction, SelectedCategory, ServiceUnavailable, UserMessage
from app.agent.store import ChatStore
from app.config import Settings
from app.database import Database
from app.main import create_app


def test_hello_health_and_legacy_records_survive(settings: Settings, model, knowledge) -> None:
    # Esquema legado representativo, con un registro que T3 no debe cargar ni borrar.
    with sqlite3.connect(settings.database_path) as db:
        db.execute("CREATE VIRTUAL TABLE documents USING fts5(code, content)")
        db.execute("INSERT INTO documents VALUES ('MO-OLD', 'contenido previo')")
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        assert client.get("/").status_code == 200
        health = client.get("/api/health").json()
        assert health == {"status": "ok", "backend": "ok", "sqlite": "ok", "frontend": "ok"}
        greeting = client.post("/api/hello", json={"name": "  Equipo VISA  "}).json()
        assert greeting["name"] == "Equipo VISA"
        for name in ["", " ", "a" * 81]:
            assert client.post("/api/hello", json={"name": name}).status_code == 422
        assert client.get("/api/unknown").status_code == 404
        matches = client.get("/api/knowledge", params={"q": "microservicio"}).json()
        assert set(matches[0]) == {"code", "title", "url", "version", "excerpt"}
        assert matches[0]["excerpt"]
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        assert client.get("/api/hello").json()["greetings"][0]["id"] == greeting["id"]
    with sqlite3.connect(settings.database_path) as db:
        assert db.execute("SELECT content FROM documents").fetchone()[0] == "contenido previo"


def test_followup_isolation_citations_and_restart(settings: Settings, model, knowledge) -> None:
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        first = client.post(
            "/api/chat", json={"message": "categoria=microservicio\ncomun.titulo=Pedido"}
        )
        assert first.status_code == 200
        assert "HttpOnly" in first.headers["set-cookie"]
        assert "SameSite=strict" in first.headers["set-cookie"]
        cookie = client.cookies.get("ocd_session")
        assert len(cookie) >= 40
        a = first.json()
        assert a["questions"] and a["collection"] == "ocd_test"
        second = client.post(
            "/api/chat", json={"message": "microservicio.version_objetivo=2.0"}
        ).json()
        assert second["revision"] == 2
        assert second["draft"]["facts"]["comun.titulo"]["value"] == "Pedido"
        assert second["draft"]["facts"]["microservicio.version_objetivo"]["value"] == "2.0"
        assert knowledge.resolutions == 2
        assert all(v["reference"]["excerpt"] for v in second["validations"])
        assert {
            v["rule_id"] for v in second["validations"] if not v["rule_id"].startswith("field:")
        } == {
            "OCD-C01",
            "OCD-C02",
            "OCD-C03",
            "OCD-C04",
            "OCD-C05",
            "OCD-C06",
            "MIC-R01",
            "MIC-R02",
            "MIC-R03",
            "MIC-R04",
            "MIC-R05",
        }
        knowledge.collection = "ocd_replaced_and_removed"
        assert client.get("/api/chat/revisions/1").json()["sources"] == a["sources"]
        client.cookies.clear()
        assert client.get("/api/chat").json()["draft"]["facts"] == {}
        assert client.get("/api/chat/revisions/1").status_code == 404
        assert (
            client.post("/api/chat", json={"message": "hola", "session_id": cookie}).status_code
            == 422
        )
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        client.cookies.set("ocd_session", cookie, path="/api/chat")
        assert client.get("/api/chat").json()["revision"] == 2
        assert client.get("/api/chat/revisions/1").json()["sources"] == a["sources"]


def test_dependency_failure_preserves_draft_and_can_resume(
    settings: Settings, model, knowledge
) -> None:
    class FailedKnowledge(FakeKnowledge):
        def resolve(self) -> str:
            raise ServiceUnavailable("No hay una carga publicada.")

    with TestClient(create_app(settings, model=model, knowledge=FailedKnowledge([]))) as client:
        response = client.post("/api/chat", json={"message": "comun.titulo=Conservar"})
        assert response.status_code == 503
        assert response.json()["draft"]["facts"]["comun.titulo"]["value"] == "Conservar"
        cookie = client.cookies.get("ocd_session")
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        client.cookies.set("ocd_session", cookie, path="/api/chat")
        result = client.post("/api/chat", json={"message": "reanudar"}).json()
        assert result["status"] == "reviewed"
        assert result["draft"]["facts"]["comun.titulo"]["value"] == "Conservar"


def test_model_failure_retains_unprocessed_messages(settings: Settings, knowledge) -> None:
    class FailingModel(FakeModel):
        def extract(self, messages, draft):
            raise ServiceUnavailable("Modelo no disponible.")

    with TestClient(create_app(settings, model=FailingModel(), knowledge=knowledge)) as client:
        assert (
            client.post("/api/chat", json={"message": "comun.titulo=Recuperar"}).status_code == 503
        )
        cookie = client.cookies.get("ocd_session")
    with TestClient(create_app(settings, model=FakeModel(), knowledge=knowledge)) as client:
        client.cookies.set("ocd_session", cookie, path="/api/chat")
        result = client.post("/api/chat", json={"message": "continuar"}).json()
        assert result["draft"]["facts"]["comun.titulo"]["value"] == "Recuperar"


def test_concurrent_turns_keep_all_facts_and_late_review_does_not_overwrite(
    settings, knowledge
) -> None:
    database = Database(settings.database_path)
    database.initialize()
    store = ChatStore(database)
    session, _ = store.session(None)

    class ConcurrentModel(FakeModel):
        def extract(self, messages: list[UserMessage], draft: Draft) -> Extraction:
            patch = super().extract(messages, draft)
            return patch

    service = ChatService(store, ConcurrentModel(), knowledge)
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(service.handle, session, "comun.titulo=Primero")
        b = pool.submit(service.handle, session, "comun.objetivo=Segundo")
        assert a.result().status == "reviewed"
        assert b.result().status == "reviewed"
    current = store.get(session)
    assert current.revision == 2
    assert current.draft.value("comun", "titulo") == "Primero"
    assert current.draft.value("comun", "objetivo") == "Segundo"


def test_integrations_remain_configuration_only(settings, model, knowledge) -> None:
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        assert {i["status"] for i in client.get("/api/integrations").json()} == {"pending"}


def test_unconfigured_openai_and_missing_qdrant_return_503_without_startup_io(settings) -> None:
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/health").status_code == 200
        response = client.post("/api/chat", json={"message": "Quiero preparar un cambio"})
        assert response.status_code == 503
        assert client.get("/api/chat").json()["revision"] == 1


def test_detected_secret_never_reaches_model_or_sqlite(settings, knowledge) -> None:
    class InspectModel(FakeModel):
        def extract(self, messages, draft):
            assert all("valor-privado" not in m.content for m in messages)
            return super().extract(messages, draft)

    with TestClient(create_app(settings, model=InspectModel(), knowledge=knowledge)) as client:
        response = client.post(
            "/api/chat", json={"message": "comun.titulo=Prueba\npassword=valor-privado"}
        )
        assert "valor-privado" not in response.text
        assert response.json()["draft"]["sensitive_detected"]
        result = next(r for r in response.json()["validations"] if r["rule_id"] == "OCD-C05")
        assert result["status"] == "ERROR"
    with sqlite3.connect(settings.database_path) as db:
        assert all(
            "valor-privado" not in row[0] for row in db.execute("SELECT content FROM chat_messages")
        )


def test_external_operations_do_not_hold_write_transactions(settings, knowledge) -> None:
    def probe():
        with sqlite3.connect(settings.database_path, timeout=0) as db:
            db.execute("BEGIN IMMEDIATE")
            db.rollback()

    class ProbeModel(FakeModel):
        def extract(self, messages, draft):
            probe()
            return super().extract(messages, draft)

        def tools(self, execute):
            probe()
            super().tools(execute)

    class ProbeKnowledge(FakeKnowledge):
        def resolve(self):
            probe()
            return super().resolve()

        def retrieve(self, collection, categories, query):
            probe()
            return super().retrieve(collection, categories, query)

    with TestClient(
        create_app(settings, model=ProbeModel(), knowledge=ProbeKnowledge(knowledge.points))
    ) as client:
        assert (
            client.post("/api/chat", json={"message": "comun.titulo=Sin bloqueo"}).status_code
            == 200
        )


def test_older_extraction_cannot_undo_a_newer_correction(settings):
    database = Database(settings.database_path)
    database.initialize()
    store = ChatStore(database)
    session, _ = store.session(None)
    store.append(session, "comun.titulo=Anterior")
    older = store.pending(session)
    store.append(session, "comun.titulo=Corregido")
    newer = store.pending(session)
    fake = FakeModel()
    store.merge(session, fake.extract(newer, Draft()), newer)
    store.merge(session, fake.extract(older, Draft()), older)
    assert store.get(session).draft.value("comun", "titulo") == "Corregido"
    assert store.get(session).revision == 1


def test_overlapping_batches_only_admit_unprocessed_facts(settings):
    database = Database(settings.database_path)
    database.initialize()
    store = ChatStore(database)
    session, _ = store.session(None)
    store.append(session, "comun.titulo=Anterior")
    first = store.pending(session)
    store.append(session, "comun.objetivo=Objetivo")
    overlapping = store.pending(session)
    model = FakeModel()
    store.merge(session, model.extract(first, Draft()), first)
    store.append(session, "comun.titulo=Corregido")
    correction = store.pending(session)
    store.merge(session, model.extract(correction, Draft()), correction)
    store.merge(session, model.extract(overlapping, Draft()), overlapping)
    assert store.get(session).revision == 2
    assert store.get(session).draft.value("comun", "titulo") == "Corregido"
    assert store.get(session).draft.value("comun", "objetivo") == "Objetivo"


def test_category_can_be_explicitly_removed_without_late_reactivation(settings):
    database = Database(settings.database_path)
    database.initialize()
    store = ChatStore(database)
    session, _ = store.session(None)
    store.append(session, "incluir red")
    first = store.pending(session)
    store.merge(
        session,
        Extraction(
            categories=[
                SelectedCategory(
                    category="red", selected=True, quote="incluir red", message_id=first[0].id
                )
            ],
            facts=[],
        ),
        first,
    )
    store.append(session, "retiro red del alcance")
    second = store.pending(session)
    store.merge(
        session,
        Extraction(
            categories=[
                SelectedCategory(
                    category="red", selected=False, quote="retiro red", message_id=second[0].id
                )
            ],
            facts=[],
        ),
        second,
    )
    assert store.get(session).draft.categories == []
    assert store.get(session, 1).draft.categories == ["red"]
    store.merge(
        session,
        Extraction(
            categories=[
                SelectedCategory(category="red", quote="incluir red", message_id=first[0].id)
            ],
            facts=[],
        ),
        first,
    )
    assert store.get(session).revision == 2
    assert store.get(session).draft.categories == []


def test_http_withdrawal_stops_using_category_facts_and_rules(settings, knowledge):
    class CorrectingModel(FakeModel):
        def extract(self, messages, draft):
            if messages[-1].content == "Retiro red del alcance":
                return Extraction(
                    categories=[
                        SelectedCategory(
                            category="red",
                            selected=False,
                            quote=messages[-1].content,
                            message_id=messages[-1].id,
                        )
                    ],
                    facts=[],
                )
            return super().extract(messages, draft)

    with TestClient(create_app(settings, model=CorrectingModel(), knowledge=knowledge)) as client:
        first = client.post(
            "/api/chat",
            json={
                "message": "categoria=red\nred.ambiente_destino=certificacion\n"
                "comun.ambiente_objetivo=produccion"
            },
        ).json()
        second = client.post("/api/chat", json={"message": "Retiro red del alcance"}).json()
        assert first["draft"]["categories"] == ["red"]
        assert second["draft"]["categories"] == []
        assert "red.ambiente_destino" not in second["draft"]["facts"]
        assert not any(v["rule_id"].startswith("RED-") for v in second["validations"])
        assert client.get("/api/chat/revisions/1").json() == first


def test_failure_after_review_keeps_previous_numbered_revision(settings, model, knowledge):
    class FailedModel(FakeModel):
        def extract(self, messages, draft):
            raise ServiceUnavailable("Indisponible")

    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        reviewed = client.post("/api/chat", json={"message": "comun.titulo=Conservar"}).json()
        cookie = client.cookies.get("ocd_session")
    with TestClient(create_app(settings, model=FailedModel(), knowledge=knowledge)) as client:
        client.cookies.set("ocd_session", cookie, path="/api/chat")
        failed = client.post("/api/chat", json={"message": "continuar"})
        assert failed.status_code == 503 and failed.json()["revision"] == 2
        assert client.get("/api/chat/revisions/1").json() == reviewed
