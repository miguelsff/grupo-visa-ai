"""Aceptación HTTP contra aplicación empaquetada y colección publicada por la CLI."""

import json
import sys
from pathlib import Path

import httpx
from app.knowledge.models import parse_record

EVIDENCE = Path("/data/acceptance.json")


def report_failure(response: httpx.Response) -> None:
    if response.status_code >= 400:
        response.read()
        print("HTTP", response.status_code, response.json().get("error"), flush=True)


def points(client: httpx.Client, collection: str) -> list[dict]:
    records = []
    offset = None
    while True:
        page = (
            client.post(
                f"/collections/{collection}/points/scroll",
                json={"limit": 64, "offset": offset, "with_payload": True},
            )
            .raise_for_status()
            .json()["result"]
        )
        records.extend(page["points"])
        offset = page["next_page_offset"]
        if offset is None:
            return records


def active(client: httpx.Client) -> str:
    aliases = client.get("/aliases").raise_for_status().json()["result"]["aliases"]
    return next(a["collection_name"] for a in aliases if a["alias_name"] == "ocd_actual")


def main(phase: str) -> None:
    with (
        httpx.Client(
            base_url="http://localhost:8000", timeout=60, event_hooks={"response": [report_failure]}
        ) as app,
        httpx.Client(base_url="http://qdrant:6333", timeout=15) as q,
        httpx.Client(base_url="http://doubles:8080", timeout=15) as double,
    ):
        assert app.get("/api/health").raise_for_status().json() == {
            "status": "ok",
            "backend": "ok",
            "sqlite": "ok",
            "frontend": "ok",
        }
        assert app.get("/").status_code == 200
        if phase == "first":
            collection = active(q)
            records = points(q, collection)
            for point in records:
                parse_record(point)
            payloads = [p["payload"] for p in records]
            assert len({p["id"] for p in records}) == len(records)
            assert len([p for p in payloads if p["kind"] == "rule"]) == 26
            assert (
                len({p["source_id"] for p in payloads if p["source"]["system"] == "confluence"})
                == 5
            )
            assert len({p["source_id"] for p in payloads if p["source"]["system"] == "jira"}) == 20
            assert all(collection == "ocd_" + p["ingestion_run_id"] for p in payloads)
            EVIDENCE.write_text(
                json.dumps({"first": collection, "ids": sorted(p["id"] for p in records)})
            )
        elif phase == "chat":
            evidence = json.loads(EVIDENCE.read_text())
            collection = active(q)
            assert collection != evidence["first"]
            records = points(q, collection)
            assert sorted(p["id"] for p in records) == evidence["ids"]
            assert all(collection == "ocd_" + p["payload"]["ingestion_run_id"] for p in records)
            assert (
                app.get("/api/knowledge", params={"q": "microservicio"}).raise_for_status().json()
            )
            first = (
                app.post(
                    "/api/chat",
                    json={
                        "message": "categoria=microservicio\ncategoria=azure\ncategoria=red\n"
                        "categoria=identidad\ncomun.titulo=Cambio de aceptación"
                    },
                )
                .raise_for_status()
                .json()
            )
            assert first["revision"] == 1 and first["status"] == "reviewed"
            assert first["questions"] and first["sources"]
            rules = {
                v["rule_id"] for v in first["validations"] if not v["rule_id"].startswith("field:")
            }
            assert len(rules) == 26, rules
            indexed = {p["id"]: p["payload"] for p in records}
            for source in first["sources"]:
                payload = indexed[source["point_id"]]
                assert source["excerpt"] == payload["text"]
                assert source["url"] == payload["source"]["url"]
                assert source["version"] == payload["source"]["version"]
            second = (
                app.post(
                    "/api/chat",
                    json={
                        "message": "microservicio.version_objetivo=2.0\n"
                        "comun.zona_horaria=America/Lima"
                    },
                )
                .raise_for_status()
                .json()
            )
            assert second["revision"] == 2 and second["collection"] == collection
            assert second["draft"]["facts"]["comun.titulo"]["value"] == "Cambio de aceptación"
            assert second["draft"]["facts"]["microservicio.version_objetivo"]["value"] == "2.0"
            assert second["questions"]
            evidence.update(
                collection=collection,
                cookie=app.cookies.get("ocd_session"),
                reviewed=second,
            )
            EVIDENCE.write_text(json.dumps(evidence))
            double.post("/control", json={"atlassian": False}).raise_for_status()
        elif phase == "publication":
            first = app.post("/api/chat", json={"message": "Quiero un pase a producción"}).raise_for_status().json()
            assert first["questions"] == ["¿Qué microservicio vas a pasar y qué versión quieres publicar?"]
            assert first["preview"] is None
            second = app.post("/api/chat", json={"message": "Pedidos, versión 1.9.0. Corrige la duplicación de pedidos."}).raise_for_status().json()
            preview = second["preview"]
            assert preview["title"] == "Pase a producción de Pedidos 1.9.0"
            assert preview["pending"] == ["ventana", "responsable", "repositorio", "pruebas", "reversión"]
            assert "Corrige la duplicación de pedidos." in preview["description"]
            revision = second["revision"]
            result = app.post(f"/api/chat/revisions/{revision}/publish")
            assert result.status_code == 201, result.text
            assert result.json() == {"key": "SCRUM-999", "url": "https://grupo-visai.atlassian.net/browse/SCRUM-999"}
            fields = double.get("/captured").raise_for_status().json()["issues"][0]["fields"]
            assert fields["project"] == {"key": "SCRUM"} and fields["issuetype"] == {"id": "10003"}
            assert fields["summary"] == preview["title"]
            nodes = fields["description"]["content"][0]["content"]
            assert "".join("\n" if n["type"] == "hardBreak" else n["text"] for n in nodes) == preview["description"]
            assert app.post(f"/api/chat/revisions/{revision}/publish").status_code == 200
            assert len(double.get("/captured").json()["issues"]) == 1
            assert app.get("/api/chat").json()["publication"] == result.json()
            evidence = json.loads(EVIDENCE.read_text())
            evidence.update(publication_cookie=app.cookies.get("ocd_session"), publication=result.json())
            EVIDENCE.write_text(json.dumps(evidence))
        else:
            evidence = json.loads(EVIDENCE.read_text())
            app.cookies.set("ocd_session", evidence["cookie"], path="/api/chat")
            assert active(q) == evidence["collection"]
            assert (
                app.get("/api/chat/revisions/2").raise_for_status().json() == evidence["reviewed"]
            )
            if phase == "offline":
                assert app.get("/api/knowledge", params={"q": "red"}).raise_for_status().json()
                result = (
                    app.post(
                        "/api/chat",
                        json={"message": "comun.objetivo=Conservar el cambio"},
                    )
                    .raise_for_status()
                    .json()
                )
                assert result["revision"] == 3 and result["status"] == "reviewed"
                double.post("/control", json={"openai": False}).raise_for_status()
                failed = app.post("/api/chat", json={"message": "comun.impacto=Sin interrupción"})
                assert failed.status_code == 503 and failed.json()["status"] == "unavailable"
                assert app.get("/api/chat/revisions/3").json() == result
                double.post("/control", json={"openai": True}).raise_for_status()
                EVIDENCE.write_text(json.dumps(evidence | {"last_reviewed": result}))
            elif phase == "resume":
                with httpx.Client(base_url="http://localhost:8000", timeout=15) as published:
                    published.cookies.set("ocd_session", evidence["publication_cookie"], path="/api/chat")
                    assert published.get("/api/chat").json()["publication"] == evidence["publication"]
                    assert published.post("/api/chat/revisions/2/publish").status_code == 200
                    assert len(double.get("/captured").json()["issues"]) == 1
                assert app.get("/api/chat").json()["revision"] == 4
                assert app.get("/api/chat/revisions/3").json() == evidence["last_reviewed"]
                result = (
                    app.post("/api/chat", json={"message": "continuar"}).raise_for_status().json()
                )
                assert result["revision"] == 5 and result["status"] == "reviewed"
                assert result["draft"]["facts"]["comun.impacto"]["value"] == "Sin interrupción"
        print("ACEPTADO", phase)


if __name__ == "__main__":
    main(sys.argv[1])
