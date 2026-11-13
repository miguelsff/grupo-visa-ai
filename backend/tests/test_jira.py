"""Contrato de publicación Jira con transporte HTTP simulado."""

import json
from dataclasses import replace

import httpx
import pytest

from app.integrations.jira import JiraClient, JiraRejectedError, JiraUncertainError


def _client(settings, handler):
    configured = replace(
        settings,
        jira_email="demo@example.com",
        jira_api_token="token-secreto",
    )
    transport = httpx.MockTransport(handler)
    return JiraClient(configured, httpx.Client(transport=transport))


def test_create_issue_preserves_preview_and_uses_only_approved_destination(settings):
    preview = "Primera línea\n\nÚltima línea\n"
    calls = []

    def handler(request):
        calls.append(request)
        assert request.url == "https://grupo-visai.atlassian.net/rest/api/3/issue"
        assert request.headers["authorization"].startswith("Basic ")
        fields = json.loads(request.content)["fields"]
        assert fields["project"] == {"key": "SCRUM"}
        assert fields["issuetype"] == {"id": "10003"}
        assert fields["summary"] == "Actualizar pedidos"
        assert fields["labels"] == ["ocd-42-rev-3"]
        assert "ocd-42-rev-3" not in json.dumps(fields["description"])
        nodes = fields["description"]["content"][0]["content"]
        reconstructed = "".join(
            "\n" if node["type"] == "hardBreak" else node["text"] for node in nodes
        )
        assert reconstructed == preview
        return httpx.Response(201, json={"key": "SCRUM-25"})

    jira = _client(settings, handler)
    issue = jira.create_issue("Actualizar pedidos", preview, "ocd-42-rev-3")
    assert issue.key == "SCRUM-25"
    assert issue.url == "https://grupo-visai.atlassian.net/browse/SCRUM-25"
    assert len(calls) == 1


def test_find_issue_requires_project_and_exact_label(settings):
    def handler(request):
        assert request.url == "https://grupo-visai.atlassian.net/rest/api/3/search/jql"
        body = json.loads(request.content)
        assert body["jql"] == 'project = SCRUM AND labels = "ocd-42-rev-3"'
        assert body["maxResults"] == 2
        return httpx.Response(
            200,
            json={"issues": [
                {"key": "SCRUM-25", "fields": {"project": {"key": "SCRUM"}, "labels": ["other"]}},
                {
                    "key": "SCRUM-26",
                    "fields": {"project": {"key": "SCRUM"}, "labels": ["ocd-42-rev-3"]},
                },
            ]},
        )

    issue = _client(settings, handler).find_issue("ocd-42-rev-3")
    assert issue is not None and issue.key == "SCRUM-26"


@pytest.mark.parametrize(
    "status,error",
    [(400, JiraRejectedError), (403, JiraRejectedError), (500, JiraUncertainError)],
)
def test_create_issue_classifies_response_without_retry(settings, status, error):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={"message": "sensible"})

    with pytest.raises(error) as caught:
        _client(settings, handler).create_issue("Título", "Descripción", "ocd-42")
    assert len(calls) == 1
    assert "sensible" not in str(caught.value)


def test_create_issue_timeout_is_uncertain_and_not_retried(settings):
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("timeout", request=request)

    with pytest.raises(JiraUncertainError):
        _client(settings, handler).create_issue("Título", "Descripción", "ocd-42")
    assert len(calls) == 1


def test_find_issue_rejects_duplicate_marker(settings):
    def handler(_request):
        issue = {"fields": {"project": {"key": "SCRUM"}, "labels": ["ocd-42"]}}
        return httpx.Response(
            200, json={"issues": [{"key": "SCRUM-25", **issue}, {"key": "SCRUM-26", **issue}]}
        )

    with pytest.raises(JiraUncertainError, match="más de un ticket"):
        _client(settings, handler).find_issue("ocd-42")


def test_configuration_and_marker_are_restricted(settings):
    base = replace(settings, jira_email="demo@example.com", jira_api_token="secret")
    with pytest.raises(ValueError, match="origen"):
        JiraClient(replace(base, jira_base_url="https://example.org"))
    with pytest.raises(ValueError, match="destino"):
        JiraClient(replace(base, jira_project_key="OTHER"))
    with pytest.raises(ValueError, match="marcador"):
        JiraClient(base).create_issue("Título", "Descripción", 'x" OR project = OTHER')
    assert "secret" not in repr(base)
