"""Expone únicamente presencia de configuración; nunca sus valores."""

from app.config import Settings
from app.schemas import IntegrationStatus


def integration_status(settings: Settings) -> list[IntegrationStatus]:
    atlassian_configured = bool(
        settings.atlassian_base_url and settings.atlassian_email and settings.atlassian_api_token
    )
    services = [
        ("OpenAI", bool(settings.openai_api_key)),
        ("Jira", atlassian_configured),
        ("Confluence", atlassian_configured),
    ]
    return [
        IntegrationStatus(
            name=name,
            status="configured" if configured else "pending",
            detail=(
                "Credenciales presentes. Conexión pendiente de verificar."
                if configured
                else "Conexión prevista para la siguiente etapa."
            ),
        )
        for name, configured in services
    ]
