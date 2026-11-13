"""Contrato de lectura OCD y trazabilidad de puntos recuperados."""

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol
from urllib.parse import urlparse
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from app.agent.catalog import CATEGORY_FIELDS, RULE_IDS, RULE_SIGNATURES, SOURCE_PAGES
from app.agent.facts import redact
from app.agent.models import Citation, Scope, ServiceUnavailable, StrictModel


class Source(StrictModel):
    system: Literal["confluence", "jira"]
    id: str = Field(pattern=r"^\d+$")
    code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str
    version: str = Field(min_length=1)
    document_version: str | None
    updated_at: str | None
    local_file: str | None
    locator: str = Field(min_length=1)


class Rule(StrictModel):
    id: str
    rule_class: str = Field(alias="class")
    fields: str | None
    requirement: str
    result: str
    mode: str | None


class RequiredField(StrictModel):
    name: str
    type: str
    when: str
    example: str


class Payload(StrictModel):
    schema_version: Literal[1]
    source_id: str
    record_key: str
    kind: Literal["rule", "field", "context", "example"]
    scope: Scope
    normative: bool
    text: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ingestion_run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    loaded_at: str = Field(pattern=r"Z$")
    embedding_model: Literal["text-embedding-3-small"]
    embedding_dimensions: Literal[1536]
    source: Source
    applies_when: str | None
    rule: Rule | None
    field: RequiredField | None


@dataclass(frozen=True)
class Record:
    id: str
    payload: Payload

    def citation(self) -> Citation:
        p = self.payload
        s = p.source
        return Citation(
            point_id=self.id,
            record_key=p.record_key,
            source_id=p.source_id,
            code=s.code,
            title=s.title,
            origin=s.system,
            url=s.url,
            version=s.version,
            document_version=s.document_version,
            locator=s.locator,
            excerpt=p.text,
        )


@dataclass(frozen=True)
class Knowledge:
    collection: str
    records: list[Record]


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


def parse_record(raw: dict[str, Any]) -> Record:
    p = Payload.model_validate(raw["payload"])
    expected_id = str(uuid5(NAMESPACE_URL, f"ocd:v1|{p.source_id}|{p.record_key}"))
    valid = (
        str(raw["id"]) == expected_id
        and hashlib.sha256(p.text.encode()).hexdigest() == p.content_sha256
        and p.source_id == f"{p.source.system}:086061bf-9e78-4235-82e3-dac00ef74f4f:{p.source.id}"
        and urlparse(p.source.url).scheme == "https"
        and urlparse(p.source.url).netloc == "grupo-visai.atlassian.net"
        and redact(p.text) == p.text
    )
    if p.source.system == "confluence":
        valid &= (p.source.code, p.source.id) == SOURCE_PAGES[p.scope]
        valid &= p.source.document_version == "1.0"
        valid &= f"/pages/{p.source.id}/" in p.source.url
    else:
        prefix = {"microservicio": 5, "azure": 10, "red": 15, "identidad": 20}.get(p.scope)
        valid &= prefix is not None and p.source.code in {
            f"SCRUM-{n}" for n in range(prefix or 0, (prefix or 0) + 5)
        }
        valid &= p.source.url == f"https://grupo-visai.atlassian.net/browse/{p.source.code}"
        valid &= p.source.document_version is None
    if p.kind == "rule" and p.rule:
        signature = hashlib.sha256(
            json.dumps(
                [p.rule.model_dump(by_alias=True), p.applies_when],
                sort_keys=True,
                ensure_ascii=False,
            ).encode()
        ).hexdigest()
        valid &= signature == RULE_SIGNATURES.get(p.rule.id)
        valid &= p.rule.id in RULE_IDS[p.scope]
        valid &= p.record_key == f"rule:{p.rule.id}" and p.field is None
    elif p.kind == "field" and p.field:
        expected_when = CATEGORY_FIELDS.get(p.scope, {}).get(p.field.name)
        valid &= p.field.when == expected_when and expected_when is not None
        valid &= p.applies_when == f"Sección {p.scope} activada; {expected_when}"
        valid &= p.record_key == f"field:{p.field.name}" and p.rule is None
    elif p.kind in {"example", "context"}:
        valid &= p.rule is None and p.field is None and p.applies_when is None
        valid &= p.kind != "example" or p.source.system == "jira"
        valid &= bool(re.fullmatch(f"{p.kind}:\\d+", p.record_key))
    else:
        valid = False
    valid &= p.normative == (p.kind in {"rule", "field"})
    valid &= not p.normative or p.source.system == "confluence"
    if not valid:
        raise ServiceUnavailable("El conocimiento requiere revisión de contrato o versión.")
    return Record(str(raw["id"]), p)
