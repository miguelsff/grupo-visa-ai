"""Sonda de aceptación de Qdrant con datos sintéticos; no llama servicios externos."""

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from uuid import NAMESPACE_URL, uuid5

BASE_URL = "http://qdrant:6333"
ALIAS = "ocd_actual"
COLLECTION = "ocd_prueba_t1"
SOURCE_ID = "confluence:prueba:66048"
RECORD_KEY = "rule:OCD-C01"
POINT_ID = str(uuid5(NAMESPACE_URL, f"ocd:v1|{SOURCE_ID}|{RECORD_KEY}"))
TEXT = "Regla sintética de persistencia; solicitar datos faltantes."
PAYLOAD = {
    "schema_version": 1,
    "source_id": SOURCE_ID,
    "record_key": RECORD_KEY,
    "kind": "rule",
    "scope": "comun",
    "normative": True,
    "text": TEXT,
    "content_sha256": hashlib.sha256(TEXT.encode()).hexdigest(),
    "ingestion_run_id": "00000000000000000000000000000001",
    "loaded_at": "2026-11-13T00:00:00Z",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimensions": 1536,
    "source": {
        "system": "confluence",
        "id": "66048",
        "code": "MO-OCD-000",
        "title": "Prueba sintética T1",
        "url": "https://example.invalid/wiki/66048",
        "version": "1",
        "document_version": "1.0",
        "updated_at": None,
        "local_file": None,
        "locator": "rule:OCD-C01",
    },
    "applies_when": "Siempre",
    "rule": {
        "id": "OCD-C01",
        "class": "Completitud",
        "fields": None,
        "requirement": TEXT,
        "result": "FALTA_INFORMACION si falta un dato.",
        "mode": None,
    },
    "field": None,
}


def request(method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        BASE_URL + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)


def seed() -> None:
    request("PUT", f"/collections/{COLLECTION}", {"vectors": {"size": 1536, "distance": "Cosine"}})
    vector = [1.0] + [0.0] * 1535
    request("PUT", f"/collections/{COLLECTION}/points?wait=true", {
        "points": [{"id": POINT_ID, "vector": vector, "payload": PAYLOAD}]
    })
    request("POST", "/collections/aliases", {"actions": [{"create_alias": {
        "collection_name": COLLECTION, "alias_name": ALIAS
    }}]})


def verify() -> None:
    info = request("GET", f"/collections/{ALIAS}")["result"]
    assert info["config"]["params"]["vectors"] == {"size": 1536, "distance": "Cosine"}
    aliases = request("GET", "/aliases")["result"]["aliases"]
    assert {"alias_name": ALIAS, "collection_name": COLLECTION} in aliases
    point = request("GET", f"/collections/{ALIAS}/points/{POINT_ID}")["result"]
    assert point["payload"] == PAYLOAD
    result = request("POST", f"/collections/{ALIAS}/points/query", {
        "query": [1.0] + [0.0] * 1535, "limit": 1, "with_payload": True
    })["result"]["points"]
    assert len(result) == 1 and result[0]["id"] == POINT_ID
    print("PASS: alias, vector 1536/Cosine, UUID estable y payload conservados", flush=True)


def wait_ready() -> None:
    for _ in range(30):
        try:
            with urllib.request.urlopen(BASE_URL + "/readyz", timeout=3):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
    raise TimeoutError("Qdrant no llegó a estar disponible")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["seed", "verify"])
    wait_ready()
    if parser.parse_args().mode == "seed":
        seed()
    verify()
