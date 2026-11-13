"""Separación de conversación y edición de borradores, con evidencia comprobada."""

import sqlite3

import pytest
from conftest import FakeModel
from fastapi.testclient import TestClient

from app.agent.conversation import NO_INFORMATION, Claim, Support, Synthesis
from app.agent.facts import redact
from app.main import create_app


class QueryModel(FakeModel):
    intent = "consulta"

    def classify(self, message, draft):
        return self.intent


def test_smalltalk_does_not_lookup_or_edit_even_after_review(settings, knowledge):
    model = QueryModel()
    with TestClient(create_app(settings, model=model, knowledge=knowledge)) as client:
        greet = client.post("/api/chat", json={"message": "¡Hola!"}).json()
        assert greet["revision"] == 0 and not greet["sources"]
        assert "OCD" in greet["answer"] and "fuentes" in greet["answer"]
        assert knowledge.resolutions == 0
        previous = client.post("/api/chat", json={"message": "comun.titulo=Pedidos"}).json()
        model.intent = "fuera_de_contexto"
        off = client.post("/api/chat", json={"message": "¿Qué sabor de helado prefieres?"}).json()
        assert "Solo puedo responder" in off["answer"] and "OCD" in off["answer"]
        assert not off["sources"] and off["draft"] == previous["draft"]
        assert client.get("/api/chat").json() == previous
        assert knowledge.resolutions == 1
        with sqlite3.connect(settings.database_path) as db:
            assert db.execute("SELECT content FROM chat_messages").fetchall() == [
                ("comun.titulo=Pedidos",)
            ]


def test_greeting_with_change_goes_through_draft_flow(settings, knowledge):
    with TestClient(create_app(settings, model=FakeModel(), knowledge=knowledge)) as client:
        review = client.post(
            "/api/chat", json={"message": "Hola, necesito un cambio\ncomun.titulo=Pedidos"}
        ).json()
        assert review["status"] == "reviewed"
        assert "Pedidos" in review["answer"]
        assert review["validations"] and review["draft"]["facts"]["comun.titulo"]


def test_document_question_uses_only_the_cited_point_and_preserves_draft(settings, knowledge):
    class ExplainRule(QueryModel):
        def compose(self, message, evidence, *, reviewing):
            key, entry = next((k, v) for k, v in evidence.items() if "OCD-C01" in v.text)
            return Synthesis(
                claims=[
                    Claim(
                        text="La OCD debe indicar la ventana con zona horaria.",
                        support=[Support(key=key, quote="ventana con zona horaria")],
                    )
                ]
            )

    with TestClient(create_app(settings, model=ExplainRule(), knowledge=knowledge)) as client:
        result = client.post("/api/chat", json={"message": "¿Qué exige OCD-C01?"}).json()
        assert "ventana con zona horaria" in result["answer"]
        assert "[MO-OCD-000]" in result["answer"]
        assert [s["record_key"] for s in result["sources"]] == ["rule:OCD-C01"]
        assert result["revision"] == 0 and result["draft"]["facts"] == {}
        assert client.get("/api/chat/revisions/1").status_code == 404


@pytest.mark.parametrize("mode", ["unknown_id", "wrong_quote", "unsupported", "no_answer"])
def test_without_admissible_evidence_abstains(settings, knowledge, mode):
    class Uncertain(QueryModel):
        def compose(self, message, evidence, *, reviewing):
            key, entry = next(iter(evidence.items()))
            if mode == "no_answer":
                return Synthesis(claims=[])
            return Synthesis(
                claims=[
                    Claim(
                        text="El responsable es Persona Inventada.",
                        support=[
                            Support(
                                key="inventado" if mode == "unknown_id" else key,
                                quote="inventada" if mode == "wrong_quote" else entry.text,
                            )
                        ],
                    )
                ]
            )

        def supported(self, message, proposal, selected, *, reviewing):
            assert mode == "unsupported"
            return False

    with TestClient(create_app(settings, model=Uncertain(), knowledge=knowledge)) as client:
        result = client.post("/api/chat", json={"message": "¿Quién aprobó mi solicitud?"}).json()
        assert result["answer"] == NO_INFORMATION
        assert not result["sources"] and not result["validations"]


def test_followup_uses_explicit_session_fact(settings, knowledge):
    class Recall(QueryModel):
        def compose(self, message, evidence, *, reviewing):
            if reviewing:
                return super().compose(message, evidence, reviewing=True)
            key = "dato:comun.titulo"
            assert evidence[key].text == "comun.titulo: Cambiar pedidos"
            return Synthesis(
                claims=[
                    Claim(
                        text="Le diste el título «Cambiar pedidos».",
                        support=[Support(key=key, quote="Cambiar pedidos")],
                    )
                ]
            )

    with TestClient(create_app(settings, model=Recall(), knowledge=knowledge)) as client:
        initial = client.post("/api/chat", json={"message": "comun.titulo=Cambiar pedidos"}).json()
        recalled = client.post("/api/chat", json={"message": "¿Qué título te indiqué?"}).json()
        assert recalled["answer"] == "Le diste el título «Cambiar pedidos»."
        assert recalled["revision"] == initial["revision"] and not recalled["sources"]
        assert client.get("/api/chat").json() == initial


def test_draft_with_facts_and_empty_synthesis_explains_next_step(settings, knowledge):
    class Empty(FakeModel):
        def compose(self, message, evidence, *, reviewing):
            return Synthesis(claims=[])

    with TestClient(create_app(settings, model=Empty(), knowledge=knowledge)) as client:
        values = (
            "categoria=microservicio\ncomun.titulo=Publicar pedidos\n"
            "microservicio.microservicio=pedidos-demo\nmicroservicio.version_actual=1.0\n"
            "microservicio.version_objetivo=2.0\ncomun.ambiente_objetivo=producción"
        )
        result = client.post("/api/chat", json={"message": values}).json()
        assert result["status"] == "reviewed"
        for detail in ("Publicar pedidos", "pedidos-demo", "1.0", "2.0", "producción"):
            assert detail in result["answer"]
        assert "objetivo" in result["answer"] and "[MO-OCD-000, OCD-C01]" in result["answer"]
        assert any(
            v["rule_id"] == "OCD-C01" and "comun.objetivo" in v["missing"]
            for v in result["validations"]
        )


@pytest.mark.parametrize(
    "secret",
    [
        "mongodb://usuario:contraseña@mongo:27017/ocd",
        "mongodb+srv://usuario:abcdef@mongodb.example",
        "Basic ZGVtbzpzZWNyZXQ=",
        "ocd_session=a-secret-cookie",
    ],
)
def test_chat_redacts_connection_credentials(secret):
    assert redact(f"Mi dato: {secret}") == "Mi dato: [DATO_SENSIBLE_OMITIDO]"
