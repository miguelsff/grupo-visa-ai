"""Hechos del solicitante, revisiones y resultados documentales."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Scope = Literal["comun", "microservicio", "azure", "red", "identidad"]
Category = Literal["microservicio", "azure", "red", "identidad"]
Status = Literal["CUMPLE", "FALTA_INFORMACION", "ERROR", "NO_VERIFICABLE"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserMessage(StrictModel):
    id: int
    content: str


class ExtractedFact(StrictModel):
    scope: Scope
    name: str
    value: str
    quote: str
    message_id: int


class SelectedCategory(StrictModel):
    selected: bool
    category: Category
    quote: str
    message_id: int


class Extraction(StrictModel):
    categories: list[SelectedCategory]
    facts: list[ExtractedFact]


class Draft(StrictModel):
    sensitive_detected: bool = False
    categories: list[Category] = Field(default_factory=list)
    facts: dict[str, ExtractedFact] = Field(default_factory=dict)
    category_messages: dict[Category, int] = Field(default_factory=dict)

    def value(self, scope: str, name: str) -> str:
        fact = self.facts.get(f"{scope}.{name}")
        if fact is None:
            return ""
        normalized = fact.value.strip().casefold()
        if normalized in {"", "no sé", "no se", "no_aplica", "no aplica", "n/a"}:
            return ""
        if normalized.startswith(
            (
                "pendiente",
                "desconocido",
                "por definir",
                "por confirmar",
                "no disponible",
                "sin definir",
            )
        ):
            return ""
        return fact.value.strip()


class Citation(StrictModel):
    point_id: str
    record_key: str
    source_id: str
    code: str
    title: str
    origin: str
    url: str
    version: str
    document_version: str | None
    locator: str
    excerpt: str


class ValidationResult(StrictModel):
    check: Literal["V-01", "V-02", "V-03"]
    rule_id: str
    status: Status
    detail: str
    missing: list[str] = Field(default_factory=list)
    reference: Citation


class ChatResponse(StrictModel):
    revision: int
    status: Literal["reviewed", "unavailable", "pending"]
    answer: str
    draft: Draft
    collection: str | None = None
    validations: list[ValidationResult] = Field(default_factory=list)
    sources: list[Citation] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    error: str | None = None


class ServiceUnavailable(Exception):
    """Una dependencia o su contrato no permite completar la revisión."""
