"""Publicación de una solicitud OCD en el proyecto Jira autorizado."""

import re
from dataclasses import dataclass

import httpx

from app.config import Settings

ALLOWED_JIRA_ORIGIN = "https://grupo-visai.atlassian.net"
_MARKER = re.compile(r"[A-Za-z0-9_-]{1,255}\Z")


@dataclass(frozen=True)
class JiraIssue:
    key: str
    url: str


class JiraRejectedError(Exception):
    """Jira rechazó definitivamente la solicitud; no se creó el ticket."""


class JiraUncertainError(Exception):
    """La solicitud pudo aplicarse, pero no se pudo confirmar el resultado."""


class JiraClient:
    def __init__(self, settings: Settings, http_client: httpx.Client | None = None) -> None:
        if settings.jira_base_url.rstrip("/") != ALLOWED_JIRA_ORIGIN:
            raise ValueError("El origen Jira no está autorizado.")
        if not settings.jira_email or not settings.jira_api_token:
            raise ValueError("Faltan credenciales Jira del backend.")
        if settings.jira_project_key != "SCRUM" or settings.jira_issue_type_id != "10003":
            raise ValueError("El destino Jira debe ser SCRUM/Tarea (10003).")
        self._settings = settings
        self._client = http_client or httpx.Client(
            timeout=min(settings.external_timeout, 30.0), follow_redirects=False
        )
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> JiraClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def find_issue(self, marker: str) -> JiraIssue | None:
        """Busca una etiqueta exacta dentro de SCRUM.

        None solo indica que el índice aún no muestra el ticket. Tras una creación
        incierta, el llamador debe conservar el intento pendiente y no repetir el POST.
        """
        self._validate_marker(marker)
        body = {
            "jql": f'project = SCRUM AND labels = "{marker}"',
            "fields": ["project", "labels"],
            "maxResults": 2,
        }
        try:
            response = self._client.post(
                f"{ALLOWED_JIRA_ORIGIN}/rest/api/3/search/jql",
                json=body,
                auth=self._auth(),
                timeout=min(self._settings.external_timeout, 30.0),
            )
        except httpx.RequestError as error:
            raise JiraUncertainError("No se pudo consultar Jira.") from error
        if response.status_code != 200:
            raise JiraUncertainError(
                f"Jira no permitió consultar el marcador ({response.status_code})."
            )
        try:
            result = response.json()
            issues = result["issues"]
            if not isinstance(issues, list):
                raise TypeError("issues no es una lista")
            if result.get("nextPageToken"):
                raise JiraUncertainError("La búsqueda Jira tiene más páginas sin verificar.")
            matches = [
                self._issue(issue["key"])
                for issue in issues
                if issue["fields"]["project"]["key"] == "SCRUM"
                and marker in issue["fields"]["labels"]
            ]
        except (ValueError, KeyError, TypeError) as error:
            raise JiraUncertainError("Jira devolvió una búsqueda inválida.") from error
        if len(matches) > 1:
            raise JiraUncertainError("El marcador aparece en más de un ticket Jira.")
        return matches[0] if matches else None

    def create_issue(self, title: str, description: str, marker: str) -> JiraIssue:
        """Envía un solo POST; el llamador reconcilia resultados inciertos con find_issue."""
        self._validate_marker(marker)
        if not title.strip() or not description.strip():
            raise ValueError("El título y la descripción de Jira son obligatorios.")
        fields = {
            "project": {"key": "SCRUM"},
            "issuetype": {"id": "10003"},
            "summary": title,
            "description": self._adf(description),
            "labels": [marker],
        }
        try:
            response = self._client.post(
                f"{ALLOWED_JIRA_ORIGIN}/rest/api/3/issue",
                json={"fields": fields},
                auth=self._auth(),
                timeout=min(self._settings.external_timeout, 30.0),
            )
        except httpx.RequestError as error:
            raise JiraUncertainError("No se pudo confirmar la creación en Jira.") from error
        if 400 <= response.status_code < 500 and response.status_code != 408:
            raise JiraRejectedError(f"Jira rechazó la creación ({response.status_code}).")
        if response.status_code != 201:
            raise JiraUncertainError(f"No se pudo confirmar la creación ({response.status_code}).")
        try:
            key = response.json()["key"]
            return self._issue(key)
        except (ValueError, KeyError, TypeError) as error:
            raise JiraUncertainError("Jira creó un ticket sin clave verificable.") from error

    def _auth(self) -> httpx.BasicAuth:
        return httpx.BasicAuth(self._settings.jira_email, self._settings.jira_api_token)

    @staticmethod
    def _validate_marker(marker: str) -> None:
        if not _MARKER.fullmatch(marker):
            raise ValueError("El marcador Jira debe ser una etiqueta alfanumérica válida.")

    @staticmethod
    def _adf(description: str) -> dict:
        lines = description.split("\n")
        content = []
        for index, line in enumerate(lines):
            if index:
                content.append({"type": "hardBreak"})
            if line:
                content.append({"type": "text", "text": line})
        return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": content}]}

    @staticmethod
    def _issue(key: object) -> JiraIssue:
        if not isinstance(key, str) or not re.fullmatch(r"SCRUM-[1-9][0-9]*", key):
            raise JiraUncertainError("Jira devolvió una clave fuera del proyecto SCRUM.")
        return JiraIssue(key=key, url=f"{ALLOWED_JIRA_ORIGIN}/browse/{key}")
