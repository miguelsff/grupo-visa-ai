"""Servidores REST aislados: snapshots Atlassian y respuestas OpenAI sintéticas."""

import base64
import json
import shutil
import ssl
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit

STATE = {"atlassian": True, "openai": True}


def response(output: list[dict]) -> dict:
    return {
        "id": "resp_acceptance",
        "object": "response",
        "created_at": 1,
        "status": "completed",
        "model": "gpt-6-luna",
        "output": output,
        "parallel_tool_calls": False,
        "tool_choice": "none",
        "tools": [],
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "metadata": {},
        "temperature": 1,
        "top_p": 1,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass

    def send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/health":
            self.send(200, STATE)
            return
        expected = base64.b64encode(b"acceptance@example.test:acceptance-fictional-token").decode()
        if self.headers.get("Authorization") != "Basic " + expected:
            self.send(401, {})
            return
        if not STATE["atlassian"]:
            self.send(503, {})
            return
        if path.startswith("/wiki/api/v2/pages/"):
            fixture = Path("/fixtures/pages") / (path.rsplit("/", 1)[1] + ".json")
        elif path.startswith("/rest/api/3/issue/"):
            fixture = Path("/fixtures/tickets") / (path.rsplit("/", 1)[1] + ".json")
        else:
            self.send(404, {})
            return
        self.send(200, json.loads(fixture.read_text()) if fixture.is_file() else {})

    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/control":
            STATE.update(body)
            self.send(200, STATE)
            return
        if not STATE["openai"]:
            self.send(503, {"error": {"message": "Fallo sintético", "type": "server_error"}})
            return
        if self.path == "/v1/embeddings":
            assert body["model"] == "text-embedding-3-small"
            assert body["dimensions"] == 1536
            inputs = body["input"] if isinstance(body["input"], list) else [body["input"]]
            self.send(
                200,
                {
                    "object": "list",
                    "model": body["model"],
                    "data": [
                        {
                            "object": "embedding",
                            "index": i,
                            "embedding": [1.0] + [0.0] * 1535,
                        }
                        for i in range(len(inputs))
                    ],
                    "usage": {"prompt_tokens": 1, "total_tokens": 1},
                },
            )
            return
        if self.path != "/v1/responses":
            self.send(404, {})
            return
        assert body["model"] == "gpt-6-luna" and body["store"] is False
        if "text" in body:
            data = json.loads(body["input"][0]["content"])
            schema = body["text"]["format"]["name"]
            if schema == "TurnIntent":
                result = {"intent": "borrador"}
            elif schema == "Assessment":
                result = {"supported": True}
            elif schema == "Synthesis":
                key, entry = next(iter(data["evidencia"].items()))
                result = {"claims": [{"text": entry["texto"], "support": [
                    {"key": key, "quote": entry["texto"]}
                ]}]}
            else:
                result = extraction(data["messages"])
            text = json.dumps(result)
            output = [
                {
                    "type": "message",
                    "id": "msg_acceptance",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": text, "annotations": []}],
                }
            ]
        else:
            name = body["tool_choice"]["name"]
            assert name in {"buscar_conocimiento", "validar_ocd"}
            output = [
                {
                    "type": "function_call",
                    "name": name,
                    "arguments": "{}",
                    "call_id": "call_" + name,
                    "id": "fc_" + name,
                    "status": "completed",
                }
            ]
        self.send(200, response(output))


def extraction(messages: list[dict]) -> dict:
    facts, categories = {}, {}
    for message in messages:
        for line in message["content"].splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            evidence = {"quote": line, "message_id": message["id"]}
            if key == "categoria":
                categories[value] = {"category": value, "selected": True, **evidence}
            else:
                scope, name = key.split(".", 1)
                facts[key] = {"scope": scope, "name": name, "value": value, **evidence}
    return {"categories": list(categories.values()), "facts": list(facts.values())}


def main() -> None:
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "2",
            "-keyout",
            "/key.pem",
            "-out",
            "/cert.pem",
            "-subj",
            "/CN=grupo-visai.atlassian.net",
            "-addext",
            "subjectAltName=DNS:grupo-visai.atlassian.net",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    shutil.copyfile("/cert.pem", "/trust/cert.pem")
    secure = ThreadingHTTPServer(("0.0.0.0", 443), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("/cert.pem", "/key.pem")
    secure.socket = context.wrap_socket(secure.socket, server_side=True)
    Thread(target=secure.serve_forever, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
