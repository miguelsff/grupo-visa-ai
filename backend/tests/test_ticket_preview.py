"""Recorrido conversacional del pase preliminar de microservicios."""

from conftest import FakeModel
from fastapi.testclient import TestClient

from app.agent.models import ExtractedFact, Extraction, SelectedCategory
from app.main import create_app


class NaturalMicroserviceModel(FakeModel):
    def extract(self, messages, draft):
        categories = []
        facts = []
        for message in messages:
            content = message.content
            if "pase a producción" in content:
                categories.append(
                    SelectedCategory(
                        category="microservicio",
                        selected=True,
                        quote="pase a producción",
                        message_id=message.id,
                    )
                )
            for scope, name, value in (
                ("microservicio", "microservicio", "Pedidos"),
                ("microservicio", "microservicio", "Cobros"),
                ("microservicio", "version_objetivo", "1.9.0"),
                ("microservicio", "version_objetivo", "2.1.0"),
                ("comun", "objetivo", "Corrige la duplicación de pedidos."),
                ("comun", "objetivo", "Elimina el cobro duplicado."),
            ):
                if value in content:
                    facts.append(
                        ExtractedFact(
                            scope=scope,
                            name=name,
                            value=value,
                            quote=value,
                            message_id=message.id,
                        )
                    )
        return Extraction(categories=categories, facts=facts)


def test_two_turn_preview_and_revised_correction_survive_restart(settings, knowledge):
    model = NaturalMicroserviceModel()
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        first = client.post(
            "/api/chat", json={"message": "Quiero hacer un pase a producción de mi microservicio"}
        ).json()
        assert first["revision"] == 1
        assert first["questions"] == [
            "¿Qué microservicio vas a pasar y qué versión quieres publicar?"
        ]
        assert first["preview"] is None
        assert "microservicio.microservicio" not in first["draft"]["facts"]
        cookie = client.cookies.get("ocd_session")
        second = client.post(
            "/api/chat",
            json={"message": "Pedidos, versión 1.9.0. Corrige la duplicación de pedidos."},
        ).json()
        assert second["revision"] == 2
        assert second["preview"]["project_key"] == "SCRUM"
        assert second["preview"]["issue_type"] == "Tarea"
        assert second["preview"]["title"] == "Pase a producción de Pedidos 1.9.0"
        assert "Corrige la duplicación de pedidos." in second["preview"]["description"]
        assert second["preview"]["pending"] == [
            "ventana", "responsable", "repositorio", "pruebas", "reversión"
        ]
        assert not second["questions"]
        assert second["validations"] and second["sources"]
        assert second["draft"]["facts"]["comun.objetivo"]["quote"] == (
            "Corrige la duplicación de pedidos."
        )
        assert client.get("/api/chat/revisions/1").json()["preview"] is None

    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        client.cookies.set("ocd_session", cookie, path="/api/chat")
        assert client.get("/api/chat").json()["preview"] == second["preview"]
        corrected = client.post(
            "/api/chat",
            json={
                "message": "Cambia el microservicio a Cobros, versión 2.1.0. "
                "Elimina el cobro duplicado."
            },
        ).json()
        assert corrected["revision"] == 3
        assert corrected["preview"]["title"] == "Pase a producción de Cobros 2.1.0"
        assert "Elimina el cobro duplicado." in corrected["preview"]["description"]
        assert client.get("/api/chat/revisions/2").json()["preview"] == second["preview"]


def test_complete_first_turn_previews_without_question(settings, knowledge):
    with TestClient(
        create_app(settings, model=NaturalMicroserviceModel(), knowledge=knowledge)
    ) as client:
        result = client.post(
            "/api/chat",
            json={
                "message": "Quiero hacer un pase a producción de Pedidos, versión 1.9.0. "
                "Corrige la duplicación de pedidos."
            },
        ).json()
        assert result["revision"] == 1
        assert result["preview"]["title"] == "Pase a producción de Pedidos 1.9.0"
        assert result["questions"] == []


def test_contradictory_version_blocks_preview_until_corrected(settings, knowledge):
    with TestClient(create_app(settings, model=FakeModel(), knowledge=knowledge)) as client:
        first = client.post(
            "/api/chat",
            json={
                "message": "categoria=microservicio\n"
                "microservicio.microservicio=Cobros\n"
                "microservicio.version_actual=1.0\n"
                "microservicio.version_objetivo=1.0\n"
                "microservicio.publica_version_diferente=sí"
            },
        ).json()
        assert first["preview"] is None
        assert any(
            v["rule_id"] == "MIC-R02" and v["status"] == "ERROR"
            for v in first["validations"]
        )
        assert len(first["questions"]) == 1
        corrected = client.post(
            "/api/chat", json={"message": "microservicio.version_objetivo=1.1"}
        ).json()
        assert corrected["preview"]["title"] == "Pase a producción de Cobros 1.1"


def test_generic_service_name_cannot_open_preview(settings, knowledge):
    with TestClient(create_app(settings, model=FakeModel(), knowledge=knowledge)) as client:
        result = client.post(
            "/api/chat",
            json={
                "message": "categoria=microservicio\n"
                "microservicio.microservicio=mi microservicio\n"
                "microservicio.version_objetivo=3.0"
            },
        ).json()
        assert result["preview"] is None
        assert result["questions"] == ["¿Qué microservicio vas a pasar?"]
