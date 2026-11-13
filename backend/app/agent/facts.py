"""Admisión de hechos con evidencia literal y detección limitada de secretos."""

import re

from app.agent.catalog import CATEGORY_FIELDS
from app.agent.models import Draft, ExtractedFact, Extraction, ServiceUnavailable, UserMessage

COMMON_FIELDS = (
    "titulo objetivo solicitante rol_solicitante responsable rol_responsable etapa ambientes "
    "ventana_inicio ventana_fin zona_horaria impacto ambiente_objetivo dependencias "
    "dependencias_ambientes plan_ejecucion resultado_ejecucion plan_pruebas resultado_pruebas "
    "plan_reversion resultado_reversion"
).split()
EXTRA_FIELDS = {
    "microservicio": "publica_version_diferente cambia_datos cambia_contrato "
    "criterio_funcional version_reversion",
    "azure": "replicas_min replicas_max bandera cambia_replicas cambia_bandera "
    "intervienen_credenciales",
    "red": "usa_dns regla_ejecutable tipo_origen tipo_destino",
    "identidad": "estado_identidad rol alcance api_destino emisor sujeto audiencia "
    "referencia_certificado vigencia_certificado prueba_permitida prueba_denegada",
}
ALLOWED_FIELDS = {"comun": set(COMMON_FIELDS)} | {
    scope: {part.strip() for field in fields for part in field.split("/")}
    | set(EXTRA_FIELDS[scope].split())
    for scope, fields in CATEGORY_FIELDS.items()
}
SENSITIVE_MARKER = "[DATO_SENSIBLE_OMITIDO]"
SECRET_PATTERNS = [
    re.compile(r"(?i)\bmongodb(?:\+srv)?://[^\s/@]+@[^\s]+"),
    re.compile(r"(?i)\bBasic\s+[A-Za-z0-9+/]+={0,2}"),
    re.compile(r"(?i)\bocd_session\s*=\s*[^\s;,]+"),
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|$)", re.S),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    re.compile(
        r"(?i)\b(?:password|contraseña|client_secret|api_key|access_token|token)"
        r"\s*[:=]\s*(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
    ),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9_.-]+"),
]


def redact(content: str) -> str:
    for pattern in SECRET_PATTERNS:
        content = pattern.sub(SENSITIVE_MARKER, content)
    return content


class InvalidExtraction(ServiceUnavailable):
    """El modelo debe corregir la extracción antes de guardar los datos del turno."""


def grounded(patch: Extraction, messages: list[UserMessage], draft: Draft) -> Extraction:
    contents = {message.id: message.content for message in messages}
    for fact in patch.facts:
        if fact.name not in ALLOWED_FIELDS[fact.scope]:
            raise InvalidExtraction(f"El campo propuesto no está admitido en {fact.scope}.")
    for item in [*patch.categories, *patch.facts]:
        if not item.quote.strip() or item.quote not in contents.get(item.message_id, ""):
            field = (
                f"{item.scope}.{item.name}" if isinstance(item, ExtractedFact) else item.category
            )
            raise InvalidExtraction(
                f"La cita de {field} no coincide con el mensaje {item.message_id}."
            )
    selected = set(draft.categories) | {item.category for item in patch.categories if item.selected}
    for fact in patch.facts:
        if (
            not fact.value.strip()
            or fact.value not in fact.quote
            or (fact.scope != "comun" and fact.scope not in selected)
        ):
            raise InvalidExtraction(
                f"No se pudo validar {fact.scope}.{fact.name} en el mensaje {fact.message_id}."
            )
    if len({(fact.scope, fact.name) for fact in patch.facts}) != len(patch.facts):
        raise InvalidExtraction("La extracción contiene hechos duplicados o contradictorios.")
    return patch
