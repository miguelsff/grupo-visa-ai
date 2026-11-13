"""Doble HTTP exclusivo de pruebas. No se copia a la imagen runtime."""

import json
import os
from pathlib import Path

import httpx

original_init = httpx.Client.__init__


def fixture_response(request):
    category = "pages" if "/wiki/" in request.url.path else "tickets"
    path = (
        Path(os.environ["TEST_FIXTURES"])
        / category
        / (request.url.path.rsplit("/", 1)[1] + ".json")
    )
    if request.method != "GET" or not path.is_file():
        raise AssertionError("Lectura no autorizada")
    return httpx.Response(200, json=json.loads(path.read_text()))


def fixture_client(self, *args, **kwargs):
    if str(kwargs.get("base_url", "")) == "https://grupo-visai.atlassian.net":
        kwargs["transport"] = httpx.MockTransport(fixture_response)
    original_init(self, *args, **kwargs)


httpx.Client.__init__ = fixture_client
