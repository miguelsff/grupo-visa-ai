import json
import os
import time
from pathlib import Path

import httpx
import pytest

from ocd_ingesta.content import collect, load_manifest
from ocd_ingesta.qdrant import Qdrant
from ocd_ingesta.remote import Atlassian

FIXTURES = Path(__file__).parent / "fixtures"


def remote_response(request: httpx.Request) -> httpx.Response:
    if request.url.path.startswith("/wiki/api/v2/pages/"):
        assert dict(request.url.params) == {"body-format": "view"}
        path = FIXTURES / "pages" / (request.url.path.rsplit("/", 1)[1] + ".json")
    elif request.url.path.startswith("/rest/api/3/issue/"):
        assert request.url.params["fields"] == "summary,description,updated"
        path = FIXTURES / "tickets" / (request.url.path.rsplit("/", 1)[1] + ".json")
    else:
        raise AssertionError("Lectura no autorizada")
    assert request.method == "GET"
    return httpx.Response(200, json=json.loads(path.read_text()))


@pytest.fixture
def manifest():
    return load_manifest(Path("manifest.json"), "https://grupo-visai.atlassian.net")


@pytest.fixture
def records(manifest):
    with httpx.Client(
        base_url="https://grupo-visai.atlassian.net", transport=httpx.MockTransport(remote_response)
    ) as client:
        return collect(Atlassian(client, manifest), manifest, "a" * 32, "2026-11-13T12:00:00Z")


@pytest.fixture
def qdrant():
    url = os.environ.get("QDRANT_TEST_URL")
    if not url:
        pytest.skip("Requiere Qdrant aislado: ejecutar Test-Ingesta.ps1")
    with httpx.Client(base_url=url, timeout=15) as client:
        deadline = time.monotonic() + 40
        while True:
            try:
                client.get("/readyz").raise_for_status()
                break
            except httpx.HTTPError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.2)
        qdrant = Qdrant(client)
        existing_aliases = qdrant.aliases()
        existing_collections = qdrant.collections()
        if "ocd_actual" in existing_aliases:
            pytest.skip("ocd_actual preexistente: usar un proyecto aislado vacío")
        yield qdrant
        # Solo se usa el Qdrant del proyecto temporal de pruebas.
        for alias in qdrant.aliases().keys() - existing_aliases.keys():
            qdrant.call(
                "POST",
                "/collections/aliases",
                json={"actions": [{"delete_alias": {"alias_name": alias}}]},
            )
        for name in qdrant.collections() - existing_collections:
            qdrant.delete_unpublished(name)
