"""Pruebas de integración para la base local."""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def configuration(tmp_path: Path, **overrides: str) -> Settings:
    frontend = tmp_path / "static"
    frontend.mkdir(exist_ok=True)
    (frontend / "index.html").write_text("<h1>Hola mundo</h1>", encoding="utf-8")
    knowledge = Path(os.environ.get("KNOWLEDGE_DIR", "../docs/modelos_operativos"))
    return Settings(
        database_path=tmp_path / "data" / "test.sqlite3",
        knowledge_dir=knowledge,
        frontend_dir=frontend,
        **overrides,
    )


def test_hello_persists_after_restart_and_knowledge_is_not_duplicated(tmp_path: Path) -> None:
    settings = configuration(tmp_path)
    with TestClient(create_app(settings)) as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/health").json()["document_count"] == 5
        response = client.post("/api/hello", json={"name": "  Equipo VISA  "})
        assert response.status_code == 201
        greeting = response.json()
        assert greeting["name"] == "Equipo VISA"
        assert "Equipo VISA" in greeting["message"]

    with TestClient(create_app(settings)) as client:
        assert client.get("/api/hello").json()["greetings"][0]["id"] == greeting["id"]
        health = client.get("/api/health").json()
        assert health["greeting_count"] == 1
        assert health["document_count"] == 5
        matches = client.get("/api/knowledge", params={"q": "microservicios"}).json()
        assert any(match["code"] == "MO-MIC-001" for match in matches)
        assert all(
            match["url"].startswith("https://grupo-visai.atlassian.net/") for match in matches
        )
        assert client.get("/api/knowledge", params={"q": '" OR * ()'}).status_code == 200


def test_invalid_names_do_not_write_and_unknown_routes_return_404(tmp_path: Path) -> None:
    with TestClient(create_app(configuration(tmp_path))) as client:
        for name in ["", "   ", "a" * 81]:
            assert client.post("/api/hello", json={"name": name}).status_code == 422
        assert client.get("/api/health").json()["greeting_count"] == 0
        assert client.get("/api/unknown").status_code == 404
        assert client.get("/missing-page").status_code == 404


def test_integrations_do_not_expose_credentials_or_claim_connectivity(tmp_path: Path) -> None:
    settings = configuration(tmp_path, openai_api_key="fake-secret-for-test")
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/integrations")
        assert "fake-secret-for-test" not in response.text
        statuses = {item["name"]: item["status"] for item in response.json()}
        assert statuses == {"OpenAI": "configured", "Jira": "pending", "Confluence": "pending"}
