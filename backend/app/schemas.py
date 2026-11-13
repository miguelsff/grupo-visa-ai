"""Contratos de la API de la etapa 1."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class HelloRequest(BaseModel):
    name: Name


class Greeting(BaseModel):
    id: str
    name: str
    message: str
    created_at: datetime


class HelloResponse(BaseModel):
    message: str
    greetings: list[Greeting]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    backend: Literal["ok"] = "ok"
    sqlite: Literal["ok"] = "ok"
    fts5: Literal["ok"] = "ok"
    frontend: Literal["ok", "missing"]
    document_count: int
    greeting_count: int


class KnowledgeMatch(BaseModel):
    code: str
    title: str
    url: str
    version: str
    excerpt: str


class IntegrationStatus(BaseModel):
    name: str
    status: Literal["pending", "configured"]
    detail: str
