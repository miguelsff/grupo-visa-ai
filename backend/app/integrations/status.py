"""Expone únicamente presencia de configuración; nunca sus valores."""

from app.config import Settings
from app.schemas import IntegrationStatus


def integration_status(settings: Settings) -> list[IntegrationStatus]:
    atlassian_configured = bool(
        settings.atlassian_base_url and settings.atlassian_email and settings.atlassian_api_token
    )
    services = [
        ("OpenAI", bool(settings.openai_api_key)),
        (
            "Jira",
            bool(settings.jira_base_url and settings.jira_email and settings.jira_api_token),
        ),
        ("Confluence", atlassian_configured),
    ]
    return [
        IntegrationStatus(
            name=name,
            status="configured" if configured else "pending",
            detail=(
                "Credenciales presentes. Conexión pendiente de verificar."
                if configured
                else (
                    "Falta OPENAI_API_KEY para inferencia y embeddings de consulta."
                    if name == "OpenAI"
                    else (
                        "Faltan credenciales Jira del backend. "
                        "Este endpoint no verifica su conexión."
                        if name == "Jira"
                        else "Atlassian se configura en ingesta. "
                        "Este endpoint no verifica su estado."
                    )
                )
            ),
        )
        for name, configured in services
    ]
