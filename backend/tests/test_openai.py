"""SDK oficial con transporte simulado: Responses y embeddings, sin credenciales reales."""

import json

import httpx
from openai import OpenAI

from app.agent.conversation import Evidence
from app.agent.models import Draft, UserMessage
from app.integrations.openai import OpenAIIntegration


def response_body(output: list[dict]) -> dict:
    return {
        "id": "resp_fake",
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


def test_sdk_responses_extracts_and_dispatches_backend_tools(settings):
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert body["model"] == settings.openai_model
        assert body["store"] is False
        if "text" in body:
            category = body["text"]["format"]["schema"]["$defs"]["SelectedCategory"]
            assert "selected" in category["required"]
            assert "default" not in category["properties"]["selected"]
            return httpx.Response(
                200,
                json=response_body(
                    [
                        {
                            "id": "msg_fake",
                            "type": "message",
                            "role": "assistant",
                            "status": "completed",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": json.dumps(
                                        {
                                            "categories": [],
                                            "facts": [
                                                {
                                                    "scope": "comun",
                                                    "name": "titulo",
                                                    "value": "Mi cambio",
                                                    "quote": "Mi cambio",
                                                    "message_id": 1,
                                                }
                                            ],
                                        }
                                    ),
                                    "annotations": [],
                                }
                            ],
                        }
                    ]
                ),
            )
        if body["tool_choice"] == "none":
            outputs = [item for item in body["input"] if item.get("type") == "function_call_output"]
            assert len(outputs) == 2
            return httpx.Response(200, json=response_body([]))
        name = body["tool_choice"]["name"]
        return httpx.Response(
            200,
            json=response_body(
                [
                    {
                        "type": "function_call",
                        "name": name,
                        "arguments": "{}",
                        "call_id": f"call_{name}",
                        "id": f"fc_{name}",
                        "status": "completed",
                    }
                ]
            ),
        )

    sdk = OpenAI(
        api_key="fake-key", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    integration = OpenAIIntegration(settings, client=sdk)
    patch = integration.extract([UserMessage(id=1, content="Mi cambio")], Draft())
    assert patch.facts[0].value == "Mi cambio"
    executed = []

    def execute(name):
        executed.append(name)
        return "[]"

    integration.tools(execute)
    integration.close()
    assert executed == ["buscar_conocimiento", "validar_ocd"]
    assert len(requests) == 3
    assert all(t["name"] in {"buscar_conocimiento", "validar_ocd"} for t in requests[1]["tools"])


def test_sdk_embedding_uses_contract_model_and_dimensions(settings):
    def handler(request):
        assert request.url.path == "/v1/embeddings"
        body = json.loads(request.content)
        assert body["model"] == "text-embedding-3-small"
        assert body["dimensions"] == 1536
        return httpx.Response(
            200,
            json={
                "object": "list",
                "model": body["model"],
                "data": [{"object": "embedding", "index": 0, "embedding": [0.1] * 1536}],
                "usage": {"prompt_tokens": 1, "total_tokens": 1},
            },
        )

    sdk = OpenAI(
        api_key="fake-key", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    integration = OpenAIIntegration(settings, client=sdk)
    assert len(integration.embed("consulta")) == 1536
    integration.close()


def test_sdk_classifies_and_verifies_a_grounded_answer(settings):
    evidence = {"p1": Evidence("La regla exige un plan de pruebas.", None)}
    formats = []

    def handler(request):
        body = json.loads(request.content)
        name = body["text"]["format"]["name"]
        formats.append(name)
        assert body["store"] is False
        data = json.loads(body["input"][0]["content"])
        if name == "TurnIntent":
            assert "borrador" in data
            parsed = {"intent": "consulta"}
        elif name == "Synthesis":
            assert data["evidencia"]["p1"]["texto"] == evidence["p1"].text
            parsed = {
                "claims": [
                    {
                        "text": "Incluye un plan de pruebas.",
                        "support": [{"key": "p1", "quote": "plan de pruebas"}],
                    }
                ]
            }
        else:
            assert name == "Assessment"
            assert data["propuesta"]["claims"][0]["support"][0]["key"] == "p1"
            parsed = {"supported": True}
        return httpx.Response(
            200,
            json=response_body(
                [
                    {
                        "id": "msg_fake",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {"type": "output_text", "text": json.dumps(parsed), "annotations": []}
                        ],
                    }
                ]
            ),
        )

    sdk = OpenAI(
        api_key="fake-key", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    integration = OpenAIIntegration(settings, client=sdk)
    query = "¿Qué plan exige esa regla?"
    assert integration.classify(query, Draft()) == "consulta"
    proposal = integration.compose(query, evidence, reviewing=False)
    assert integration.supported(query, proposal, evidence, reviewing=False)
    assert formats == ["TurnIntent", "Synthesis", "Assessment"]
    integration.close()
