"""Carga las copias documentales incluidas en el repositorio."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field


class Source(BaseModel):
    code: str
    title: str
    url: str
    version: str = Field(alias="documentVersion")
    local_file: str = Field(alias="localFile")


class Manifest(BaseModel):
    index: Source
    models: list[Source]


@dataclass(frozen=True)
class Document:
    code: str
    title: str
    url: str
    version: str
    content: str


def load_documents(directory: Path) -> list[Document]:
    root = directory.resolve()
    manifest = Manifest.model_validate_json((root / "manifest.json").read_text(encoding="utf-8"))
    documents: list[Document] = []
    for source in [manifest.index, *manifest.models]:
        path = (root / source.local_file).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"El archivo de {source.code} está fuera del directorio autorizado.")
        documents.append(
            Document(
                code=source.code,
                title=source.title,
                url=source.url,
                version=source.version,
                content=path.read_text(encoding="utf-8"),
            )
        )
    return documents
