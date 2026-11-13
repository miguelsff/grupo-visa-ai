import hashlib
import unicodedata
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Source(StrictModel):
    system: Literal["confluence", "jira"]
    id: str = Field(min_length=1, pattern=r"^[0-9]+$")
    code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    version: str = Field(min_length=1)
    document_version: str | None
    updated_at: str | None
    local_file: None = None
    locator: str = Field(min_length=1)


class Rule(StrictModel):
    id: str
    rule_class: str = Field(alias="class")
    fields: str | None
    requirement: str
    result: str
    mode: str | None


class DocumentField(StrictModel):
    name: str
    type: str
    when: str
    example: str


class Payload(StrictModel):
    schema_version: Literal[1] = 1
    source_id: str
    record_key: str
    kind: Literal["rule", "field", "context", "example"]
    scope: Literal["comun", "microservicio", "azure", "red", "identidad"]
    normative: bool
    text: str = Field(min_length=1, max_length=12000)
    content_sha256: str
    ingestion_run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    loaded_at: str = Field(pattern=r"Z$")
    embedding_model: Literal["text-embedding-3-small"] = "text-embedding-3-small"
    embedding_dimensions: Literal[1536] = 1536
    source: Source
    applies_when: str | None
    rule: Rule | None = None
    field: DocumentField | None = None

    @model_validator(mode="after")
    def check_contract(self) -> Payload:
        if self.text != normalize(self.text):
            raise ValueError("Texto sin normalizar")
        if self.content_sha256 != hashlib.sha256(self.text.encode()).hexdigest():
            raise ValueError("Hash incorrecto")
        normative = self.kind in ("rule", "field")
        if self.normative != normative or normative != bool(self.applies_when):
            raise ValueError("Condición normativa inválida")
        if (self.rule is not None) != (self.kind == "rule"):
            raise ValueError("Regla incompatible")
        if (self.field is not None) != (self.kind == "field"):
            raise ValueError("Campo incompatible")
        expected = "jira" if self.kind == "example" else "confluence"
        if self.source.system != expected:
            raise ValueError("Procedencia incompatible")
        if not self.source_id.endswith(":" + self.source.id):
            raise ValueError("ID de procedencia incompatible")
        if not self.record_key.startswith(self.kind + ":"):
            raise ValueError("Clave de registro incompatible")
        return self

    @property
    def point_id(self) -> str:
        return str(uuid5(NAMESPACE_URL, f"ocd:v1|{self.source_id}|{self.record_key}"))

    def payload(self) -> dict:
        return self.model_dump(by_alias=True)
