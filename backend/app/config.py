"""Configuración del backend mediante variables de entorno."""

import os
from dataclasses import dataclass
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
        )
