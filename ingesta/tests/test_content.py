import copy
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx
import jsonschema
import pytest
from bs4 import BeautifulSoup

from ocd_ingesta.content import collect, page_records
from ocd_ingesta.remote import Atlassian
from ocd_ingesta.safety import check_secrets
from tests.conftest import FIXTURES, remote_response


def test_complete_remote_load_contract_and_stable_ids(records, manifest):
    schema = json.loads(Path("ocd_payload.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(schema)
    for record in records:
        validator.validate(record.payload())
        assert record.source.local_file is None
        assert record.source.version
        assert record.point_id == str(
            uuid5(NAMESPACE_URL, f"ocd:v1|{record.source_id}|{record.record_key}")
        )
    with httpx.Client(
        base_url="https://grupo-visai.atlassian.net", transport=httpx.MockTransport(remote_response)
    ) as client:
        second = collect(Atlassian(client, manifest), manifest, "b" * 32, "2026-11-14T12:00:00Z")
    assert [r.point_id for r in records] == [r.point_id for r in second]
    assert [r.content_sha256 for r in records] == [r.content_sha256 for r in second]
    assert len([r for r in records if r.kind == "rule"]) == 26
    assert len({r.source.id for r in records if r.kind == "example"}) == 20
    field = next(r for r in records if r.record_key == "field:client_id / object_id")
    assert field.field.when == "Si existe la identidad"
    assert field.applies_when == "Sección identidad activada; Si existe la identidad"
    text = "\n".join(r.text for r in records if r.kind == "context")
    assert "2026-11-12" in text
    assert "Modelo operativo sintético" in text
    assert "Responsable ficticio" in text  # tabla del procedimiento
    assert all(not r.normative for r in records if r.kind == "example")
    check_secrets(records, ("secret-test-123",))


@pytest.mark.parametrize("change", ["condition", "rule", "version", "date", "missing", "extra"])
def test_remote_drift_rejected(manifest, change):
    entry = manifest["models"][-1]
    remote = json.loads((FIXTURES / "pages" / "294943.json").read_text())
    html = remote["body"]["view"]["value"]
    if change == "condition":
        html = html.replace("Si existe la identidad", "Siempre")
    elif change == "rule":
        html = html.replace("ID-R01", "ID-R99")
    elif change == "version":
        remote["version"]["number"] = 2
    elif change == "date":
        html = html.replace("2026-11-12", "2026-11-11")
    elif change == "missing":
        html = html.replace("ID-R01", "")
    else:
        html = html.replace("</tbody></table>", "<tr><td>Nueva regla</td></tr></tbody></table>")
    remote["body"]["view"]["value"] = html
    with pytest.raises(ValueError):
        page_records(remote, entry, manifest, "a" * 32, "2026-11-13T12:00:00Z")


def test_context_only_contains_remote_text_and_links_are_not_followed(manifest):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        response = remote_response(request)
        data = response.json()
        if "body" in data:
            data["body"]["view"]["value"] += (
                '<p>MARCADOR_REMOTO <a href="https://other.example/secret">enlace</a></p>'
            )
        return httpx.Response(200, json=data)

    with httpx.Client(
        base_url="https://grupo-visai.atlassian.net", transport=httpx.MockTransport(handler)
    ) as client:
        records = collect(Atlassian(client, manifest), manifest, "a" * 32, "2026-11-13T12:00:00Z")
    assert len(calls) == 25
    assert all("MARCADOR_REMOTO" in r.text for r in records if r.kind == "context")


def test_missing_jira_id_never_invented(manifest):
    def handler(request):
        data = remote_response(request).json()
        if "key" in data:
            data["id"] = ""
        return httpx.Response(200, json=data)

    with (
        httpx.Client(
            base_url="https://grupo-visai.atlassian.net", transport=httpx.MockTransport(handler)
        ) as client,
        pytest.raises(ValueError),
    ):
        collect(Atlassian(client, manifest), manifest, "a" * 32, "2026-11-13T12:00:00Z")


def test_secret_aborts_before_embedding(records):
    changed = copy.deepcopy(records)
    changed[0].text += " password=actual-secret-value"
    with pytest.raises(ValueError, match="Posible secreto"):
        check_secrets(changed, ())


def test_remote_fixture_panels_tables_dates_are_preserved(manifest):
    for entry in [manifest["index"], *manifest["models"]]:
        data = json.loads((FIXTURES / "pages" / (entry["pageId"] + ".json")).read_text())
        soup = BeautifulSoup(data["body"]["view"]["value"], "html.parser")
        assert len(soup.select('[data-type="panel-note"]')) == 1
        assert len(soup.find_all("time")) == 1
        assert len(soup.find_all("table")) >= 3
        result = page_records(data, entry, manifest, "a" * 32, "2026-11-13T12:00:00Z")
        context = "\n".join(r.text for r in result if r.kind == "context")
        for panel in soup.select('[data-type="panel-note"]'):
            assert panel.get_text() in context
        assert "2026-11-12" in context
