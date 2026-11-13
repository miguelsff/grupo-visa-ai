"""Publicación idempotente de la revisión vigente a partir de su vista previa guardada."""

from typing import Protocol

from app.agent.models import JiraPublication
from app.agent.store import ChatStore
from app.integrations.jira import JiraIssue, JiraRejectedError, JiraUncertainError


class JiraPublisher(Protocol):
    def create_issue(self, title: str, description: str, marker: str) -> JiraIssue: ...
    def find_issue(self, marker: str) -> JiraIssue | None: ...


class PublicationPending(Exception):
    """El resultado remoto sigue incierto y no autoriza otro POST."""


class PublicationService:
    def __init__(self, store: ChatStore, jira: JiraPublisher) -> None:
        self.store = store
        self.jira = jira

    def publish(self, session_id: str, revision: int) -> tuple[JiraPublication, bool]:
        claim = self.store.claim_publication(session_id, revision)
        if claim.action == "confirmed":
            assert claim.publication is not None
            return claim.publication, False
        if claim.action == "reconcile":
            return self._reconcile(claim.marker), False
        try:
            issue = self.jira.create_issue(
                claim.preview_title, claim.preview_description, claim.marker
            )
        except JiraRejectedError:
            self.store.publication_rejected(claim.marker)
            raise
        except JiraUncertainError:
            self.store.publication_uncertain(claim.marker)
            return self._reconcile(claim.marker), False
        return self._confirm(claim.marker, issue), True

    def _reconcile(self, marker: str) -> JiraPublication:
        try:
            issue = self.jira.find_issue(marker)
        except JiraUncertainError as error:
            raise PublicationPending(
                "Verificando publicación… La consulta a Jira no concluyó."
            ) from error
        if issue is None:
            raise PublicationPending("Verificando publicación… Jira aún no muestra el resultado.")
        return self._confirm(marker, issue)

    def _confirm(self, marker: str, issue: JiraIssue) -> JiraPublication:
        return self.store.publication_confirmed(
            marker, JiraPublication(key=issue.key, url=issue.url)
        )
