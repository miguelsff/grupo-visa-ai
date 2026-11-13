"""Acceso público de salud, autenticación de demo y aislamiento por sesión."""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_public_routes_require_login_except_health(settings: Settings) -> None:
    protected = replace(settings, demo_password="solo-para-prueba")
    with TestClient(create_app(protected)) as client:
        for method, path in (
            ("GET", "/"),
            ("GET", "/docs"),
            ("GET", "/openapi.json"),
            ("GET", "/api/knowledge?q=red"),
            ("POST", "/api/chat"),
            ("POST", "/api/health"),
        ):
            response = client.request(method, path)
            assert response.status_code == 401
            assert response.headers["www-authenticate"].startswith("Basic ")
            assert "set-cookie" not in response.headers
        for value in ("Basic %%%", "Basic /w==", "Bearer demo"):
            assert client.get("/docs", headers={"Authorization": value}).status_code == 401
        assert client.get("/docs", auth=("demo", "otra")).status_code == 401
        assert client.get("/docs", auth=("otro", protected.demo_password)).status_code == 401
        assert client.get("/docs", auth=("demo", protected.demo_password)).status_code == 200
        assert client.get("/api/health").status_code == 200
        assert client.head("/api/health").status_code == 200


def test_demo_sessions_own_their_revisions(settings: Settings, model, knowledge) -> None:
    auth = ("demo", "clave-de-prueba")
    app = create_app(
        replace(settings, on_railway=True, demo_password=auth[1]), model=model, knowledge=knowledge
    )
    with TestClient(app, base_url="https://testserver") as client:
        draft = client.post("/api/chat", json={"message": "comun.titulo=Pedidos"}, auth=auth)
        assert draft.status_code == 200
        assert client.get("/api/chat/revisions/1", auth=auth).json() == draft.json()
        assert client.get("/api/chat/revisions/1").status_code == 401
        client.cookies.clear()
        assert client.get("/api/chat/revisions/1", auth=auth).status_code == 404
        cookie = client.get("http://testserver/api/chat", auth=auth).headers["set-cookie"]
        assert "Secure" in cookie and "HttpOnly" in cookie


def test_railway_requires_demo_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAILWAY_ENVIRONMENT_ID", "production")
    monkeypatch.delenv("OCD_DEMO_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="OCD_DEMO_PASSWORD"):
        Settings.from_environment()
    monkeypatch.setenv("OCD_DEMO_PASSWORD", "   ")
    with pytest.raises(ValueError, match="OCD_DEMO_PASSWORD"):
        Settings.from_environment()
    monkeypatch.setenv("OCD_DEMO_PASSWORD", "valor-de-prueba")
    settings = Settings.from_environment()
    assert settings.on_railway
    assert settings.demo_password == "valor-de-prueba"
    assert settings.demo_password not in repr(settings)
