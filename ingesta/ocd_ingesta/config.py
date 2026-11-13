import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Config:
    base_url: str
    email: str = field(repr=False)
    token: str = field(repr=False)
    openai_key: str = field(repr=False)
    qdrant_url: str = "http://qdrant:6333"
    alias: str = "ocd_actual"
    model: str = "text-embedding-3-small"
    dimensions: int = 1536
    manifest: Path = Path("/app/manifest.json")
    state_dir: Path = Path("/state")

    def __post_init__(self) -> None:
        if (self.alias, self.model, self.dimensions) != (
            "ocd_actual",
            "text-embedding-3-small",
            1536,
        ):
            raise ValueError("Configuración incompatible con el contrato OCD v1")
        parsed = urlsplit(self.base_url)
        if (
            parsed.scheme != "https"
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("ATLASSIAN_BASE_URL debe ser un origen HTTPS")
        if not all((self.email, self.token, self.openai_key)):
            raise ValueError("Faltan credenciales de ingesta")
        qdrant = urlsplit(self.qdrant_url)
        if qdrant.scheme not in ("http", "https") or qdrant.username or qdrant.password:
            raise ValueError("QDRANT_URL inválida")

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            base_url=os.environ.get(
                "ATLASSIAN_BASE_URL", "https://grupo-visai.atlassian.net"
            ).rstrip("/"),
            email=os.environ.get("ATLASSIAN_EMAIL", ""),
            token=os.environ.get("ATLASSIAN_API_TOKEN", ""),
            openai_key=os.environ.get("OPENAI_API_KEY", ""),
            qdrant_url=os.environ.get("QDRANT_URL", "http://qdrant:6333"),
            alias=os.environ.get("QDRANT_ALIAS", "ocd_actual"),
            model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            dimensions=int(os.environ.get("OPENAI_EMBEDDING_DIMENSIONS", "1536")),
            manifest=Path(os.environ.get("INGESTA_MANIFEST", "/app/manifest.json")),
            state_dir=Path(os.environ.get("INGESTA_STATE_DIR", "/state")),
        )
