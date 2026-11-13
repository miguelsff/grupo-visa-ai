"""Configuración del backend mediante variables de entorno."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self


@dataclass(frozen=True)
class Settings:
    database_path: Path
    knowledge_dir: Path
    frontend_dir: Path
    openai_api_key: str = ""
    openai_model: str = "gpt-6-luna"
    atlassian_base_url: str = ""
    atlassian_email: str = ""
    atlassian_api_token: str = ""
    qdrant_url: str = "http://qdrant:6333"
    qdrant_alias: str = "ocd_actual"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    external_timeout: float = 30.0
    on_railway: bool = False
    demo_password: str = field(default="", repr=False)
    mongodb_uri: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if (self.on_railway or self.demo_password) and not self.demo_password.strip():
            raise ValueError("Configura OCD_DEMO_PASSWORD para el acceso de demostración.")
        if self.on_railway and not self.mongodb_uri:
            raise ValueError("Configura MONGODB_URI para registrar las preguntas en Railway.")
        if self.embedding_model != "text-embedding-3-small" or self.embedding_dimensions != 1536:
            raise ValueError("El contrato OCD requiere text-embedding-3-small y 1536 dimensiones.")
        if self.external_timeout <= 0:
            raise ValueError("El tiempo máximo externo debe ser positivo.")

    @classmethod
    def from_environment(cls) -> Self:
        return cls(
            database_path=Path(os.environ.get("DATABASE_PATH", "data/ocd.sqlite3")),
            knowledge_dir=Path(os.environ.get("KNOWLEDGE_DIR", "../docs/modelos_operativos")),
            frontend_dir=Path(os.environ.get("FRONTEND_DIR", "../frontend/out")),
            openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
            openai_model=os.environ.get("OPENAI_MODEL", "gpt-6-luna"),
            atlassian_base_url=os.environ.get("ATLASSIAN_BASE_URL", "").strip(),
            atlassian_email=os.environ.get("ATLASSIAN_EMAIL", "").strip(),
            atlassian_api_token=os.environ.get("ATLASSIAN_API_TOKEN", "").strip(),
            qdrant_url=os.environ.get("QDRANT_URL", "http://qdrant:6333"),
            qdrant_alias=os.environ.get("QDRANT_ALIAS", "ocd_actual"),
            embedding_model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dimensions=int(os.environ.get("OPENAI_EMBEDDING_DIMENSIONS", "1536")),
            external_timeout=float(os.environ.get("EXTERNAL_TIMEOUT_SECONDS", "30")),
            on_railway="RAILWAY_ENVIRONMENT_ID" in os.environ,
            demo_password=os.environ.get("OCD_DEMO_PASSWORD", ""),
            mongodb_uri=os.environ.get("MONGODB_URI", "").strip(),
        )
