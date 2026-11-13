"""Registro de entradas válidas, antes de cambiar el borrador del usuario."""

from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pymongo.errors import ConnectionFailure

from app.agent.facts import SENSITIVE_MARKER
from app.config import Settings
from app.main import create_app


def test_logs_valid_questions_before_chat_and_omits_secrets(
    settings: Settings, model, knowledge, monkeypatch: pytest.MonkeyPatch
) -> None:
    mongo = Mock()
    monkeypatch.setattr("app.integrations.questions.MongoClient", lambda *a, **kw: mongo)
    collection = mongo.ocd.get_collection.return_value
    conf = replace(settings, demo_password="clave", mongodb_uri="mongodb://localhost:27017")
    snapshot = datetime.now(UTC)
    auth = ("demo", "clave")
    with TestClient(create_app(conf, model=model, knowledge=knowledge)) as client:
        assert client.post("/api/chat", json={"message": "hola"}).status_code == 401
        assert client.post("/api/chat", json={"message": " "}, auth=auth).status_code == 422
        assert client.get("/api/chat", auth=auth).status_code == 200
        collection.insert_one.assert_not_called()

        text = "¿Puedes ayudarme con la OCD? token=secreto-de-prueba"
        response = client.post("/api/chat", json={"message": text}, auth=auth)
        assert response.status_code == 200
        collection.insert_one.assert_called_once()
        document = collection.insert_one.call_args.args[0]
        assert document.keys() == {"fecha", "texto"}
        assert document["texto"] == f"¿Puedes ayudarme con la OCD? {SENSITIVE_MARKER}"
        assert snapshot <= document["fecha"] <= datetime.now(UTC)
        assert document["fecha"].tzinfo == UTC

        previous = client.get("/api/chat", auth=auth).json()
        collection.insert_one.side_effect = ConnectionFailure("información del servidor")
        response = client.post("/api/chat", json={"message": "comun.titulo=Otro"}, auth=auth)
        assert response.status_code == 503
        assert response.json() == {"detail": "No se pudo confirmar el registro de la pregunta."}
        assert client.get("/api/chat", auth=auth).json() == previous
        assert client.get("/api/health").status_code == 200
    mongo.close.assert_called_once()


def test_railway_requires_mongo_uri(settings: Settings) -> None:
    with pytest.raises(ValueError, match="MONGODB_URI"):
        replace(settings, on_railway=True, demo_password="clave")
