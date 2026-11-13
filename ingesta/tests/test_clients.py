import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest
from openai import OpenAI

from ocd_ingesta.config import Config
from ocd_ingesta.embeddings import OpenAIEmbedder, check_vectors
from ocd_ingesta.remote import Atlassian


@contextmanager
def openai_server(fail=False):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append(body)
            if fail:
                self.send_response(503)
                self.end_headers()
                return
            assert self.path == "/v1/embeddings"
            vectors = [
                {"index": i, "object": "embedding", "embedding": [1.0] + [0.0] * 1535}
                for i in range(len(body["input"]))
            ]
            data = {
                "object": "list",
                "model": "text-embedding-3-small",
                "data": vectors,
                "usage": {"prompt_tokens": 1, "total_tokens": 1},
            }
            encoded = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_official_sdk_batches_remote_text(records):
    with (
        openai_server() as (url, calls),
        OpenAI(api_key="test-only", base_url=url, max_retries=0) as client,
    ):
        vectors = OpenAIEmbedder(client).embed(records)
    assert len(vectors) == len(records)
    assert all(len(call["input"]) <= 16 for call in calls)
    assert all(call["dimensions"] == 1536 for call in calls)
    assert [text for call in calls for text in call["input"]] == [r.text for r in records]


@pytest.mark.parametrize("vector", [[0.0] * 1536, [1.0], [float("nan")] * 1536])
def test_bad_vectors_rejected(vector):
    with pytest.raises(ValueError):
        check_vectors([vector], 1)


def test_allowlist_and_bounded_read_retries(manifest, monkeypatch):
    monkeypatch.setattr("ocd_ingesta.remote.time.sleep", lambda _: None)
    calls = []

    def fail(request):
        calls.append(request)
        return httpx.Response(503)

    with httpx.Client(
        base_url="https://grupo-visai.atlassian.net", transport=httpx.MockTransport(fail)
    ) as client:
        atlassian = Atlassian(client, manifest)
        with pytest.raises(ValueError):
            atlassian.page("99999")
        with pytest.raises(ValueError):
            atlassian.ticket("OTHER-1")
        assert calls == []
        with pytest.raises(httpx.HTTPStatusError):
            atlassian.page("66048")
        assert len(calls) == 3


@pytest.mark.parametrize(
    "override",
    [{"model": "other"}, {"dimensions": 1}, {"alias": "other"}, {"base_url": "http://host"}],
)
def test_config_rejects_incompatible_contract(override):
    values = {
        "base_url": "https://grupo-visai.atlassian.net",
        "email": "demo@example.test",
        "token": "demo-token",
        "openai_key": "demo-key",
    }
    with pytest.raises(ValueError):
        Config(**(values | override))
