"""Prueba HTTP contra un backend en ejecución y comprueba sus inserciones en MongoDB."""

import json
import os
import time
from datetime import UTC, datetime

import httpx
from pymongo import MongoClient


def main() -> None:
    base = os.environ["OCD_TEST_URL"].rstrip("/")
    password = os.environ.get("OCD_DEMO_PASSWORD")
    messages = {
        "saludo": "Hola, ¿qué puedes hacer?",
        "fuera": "Oye, ¿qué sabor de helado te gusta?",
        "regla": "¿Qué planes exige la regla OCD-C02 en una OCD?",
        "desconocido": "¿Cuál es el nombre exacto del responsable de mi cambio demo-lima-7319?",
        "borrador": (
            "Prepara una OCD para publicar el microservicio demo-lima-7319 "
            "de la versión 1.0 a la 2.0 en producción. El título es Actualizar pedidos."
        ),
    }
    with (
        MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=8000) as mongo,
        httpx.Client(
            base_url=base, auth=("demo", password) if password else None, timeout=180
        ) as client,
    ):
        for _ in range(45):
            try:
                if client.get("/api/health", timeout=4).status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(2)
        else:
            raise RuntimeError("Servicio HTTP no disponible")

        collection = mongo.ocd.preguntas
        query = {"texto": {"$in": list(messages.values())}, "fecha": {"$gte": datetime.now(UTC)}}
        for case, message in messages.items():
            response = client.post("/api/chat", json={"message": message})
            response.raise_for_status()
            body = response.json()
            answer = body["answer"]
            sources = sorted({s["code"] for s in body["sources"]})
            print("OCD_TURNO", json.dumps({
                "caso": case, "http": response.status_code, "revision": body["revision"],
                "answer": answer, "fuentes": sources, "validaciones": len(body["validations"]),
            }, ensure_ascii=False), flush=True)
            assert answer.strip()
            if case in {"saludo", "fuera", "desconocido"}:
                assert not sources and body["revision"] == 0
            if case == "regla":
                assert "MO-OCD-000" in sources and body["revision"] == 0
                assert all(term in answer.lower() for term in ("ejecución", "pruebas", "reversión"))
            if case == "borrador":
                assert body["revision"] == 1 and body["validations"] and sources
                assert "microservicio" in body["draft"]["categories"]
                assert any(term in answer.casefold() for term in ("demo-lima-7319", "actualizar pedidos"))
        recovered = client.get("/api/chat").raise_for_status().json()
        assert recovered["revision"] == 1
        rows = list(collection.find(query, {"texto": 1}))
        assert sorted(row["texto"] for row in rows) == sorted(messages.values())
        print("OCD_VERIFICADO", json.dumps({"turnos": len(messages), "preguntas_mongo": len(rows)}),
              flush=True)


if __name__ == "__main__":
    main()
