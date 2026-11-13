import json
import re

from .models import Payload

SECRET = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}|"
    r"\b(?:password|contraseña|client_secret|api_token|access_token)\s*[:=]\s*[^\s,;]{8,}|"
    r"\bBearer\s+[A-Za-z0-9_.-]{20,}",
    re.IGNORECASE,
)


def check_secrets(records: list[Payload], credentials: tuple[str, ...]) -> None:
    for record in records:
        serialized = json.dumps(record.payload(), ensure_ascii=False)
        if SECRET.search(serialized) or any(c and c in serialized for c in credentials):
            raise ValueError(f"Posible secreto en fuente {record.source.code}")
