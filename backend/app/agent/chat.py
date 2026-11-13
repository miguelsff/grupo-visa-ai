"""Caso de uso de chat: guardar, interpretar, recuperar y validar sin escrituras remotas."""

from threading import Lock
from typing import Protocol

from pydantic import ValidationError

from app.agent.conversation import (
    INTRO,
    NO_INFORMATION,
    OFF_TOPIC,
    admitted_support,
    evidence_for,
    obvious_intent,
    render,
    review_summary,
)
from app.agent.facts import grounded, redact
from app.agent.models import Category, ChatResponse, Citation, Extraction, ServiceUnavailable
from app.agent.store import ChatStore
from app.agent.validation import validar_ocd
from app.integrations.openai import Orchestrator
from app.knowledge.models import Knowledge, Record
from app.schemas import KnowledgeMatch


class KnowledgeReader(Protocol):
    def resolve(self) -> str: ...
    def retrieve(self, collection: str, categories: list[Category], query: str) -> Knowledge: ...
    def documentary(self, collection: str, query: str) -> list[Record]: ...
    def search(self, query: str) -> list[KnowledgeMatch]: ...


class ChatService:
    def __init__(self, store: ChatStore, model: Orchestrator, knowledge: KnowledgeReader) -> None:
        self.store = store
        self.model = model
        self.knowledge = knowledge
        self._locks: dict[str, Lock] = {}
        self._guard = Lock()

    def handle(self, session_id: str, message: str) -> ChatResponse:
        with self._guard:
            lock = self._locks.setdefault(session_id, Lock())
        with lock:
            return self._handle(session_id, message)

    def _handle(self, session_id: str, message: str) -> ChatResponse:
        message = redact(message)
        previous = self.store.get(session_id)
        try:
            intent = obvious_intent(message) or self.model.classify(message, previous.draft)
            if intent == "borrador":
                return self._review(session_id, message, previous)
            result = ChatResponse(
                draft=previous.draft, revision=previous.revision, status="pending", answer=""
            )
            if intent == "saludo":
                result.answer = INTRO
            elif intent == "fuera_de_contexto":
                result.answer = OFF_TOPIC
            else:
                collection = self.knowledge.resolve()
                records = self.knowledge.documentary(collection, message)
                sources = {record.id: record.citation() for record in records}
                if previous.collection == collection:
                    sources.update({s.point_id: s for s in previous.sources})
                    result.validations = previous.validations
                result.answer, result.sources = self._compose(
                    message, result, list(sources.values()), reviewing=False
                )
                result.collection = collection
                used = {source.point_id for source in result.sources}
                result.validations = [v for v in result.validations if v.reference.point_id in used]
            return result
        except (ServiceUnavailable, ValidationError, KeyError, TypeError) as error:
            return ChatResponse(
                revision=previous.revision,
                draft=previous.draft,
                status="unavailable",
                answer="No se pudo consultar la información en este momento.",
                error=str(error)
                if isinstance(error, ServiceUnavailable)
                else "Respuesta inválida.",
            )

    def _compose(
        self, message: str, result: ChatResponse, sources: list[Citation], *, reviewing: bool
    ) -> tuple[str, list[Citation]]:
        evidence = evidence_for(result.draft, sources, result.validations)
        if not evidence:
            return NO_INFORMATION, []
        proposal = self.model.compose(message, evidence, reviewing=reviewing)
        selected = admitted_support(proposal, evidence)
        if selected and self.model.supported(message, proposal, selected, reviewing=reviewing):
            return render(proposal, selected)
        if reviewing:
            return review_summary(result.draft, result.validations), []
        return NO_INFORMATION, []

    def _review(self, session_id: str, message: str, previous: ChatResponse) -> ChatResponse:
        self.store.append(session_id, message)
        pending = self.store.pending(session_id)
        result: ChatResponse | None = None
        try:
            extracted = (
                self.model.extract(pending, previous.draft)
                if pending
                else Extraction(categories=[], facts=[])
            )
            patch = grounded(extracted, pending, previous.draft)
            result = self.store.merge(session_id, patch, pending)
            knowledge: Knowledge | None = None

            def execute(name: str) -> str:
                nonlocal knowledge
                assert result is not None
                if name == "buscar_conocimiento":
                    if knowledge is not None:
                        raise ServiceUnavailable("La recuperación ya se ejecutó en este turno.")
                    # Resolver una sola vez. Toda lectura posterior usa la colección física.
                    collection = self.knowledge.resolve()
                    query = "\n".join(f.value for f in result.draft.facts.values()) or redact(
                        message
                    )
                    knowledge = self.knowledge.retrieve(collection, result.draft.categories, query)
                    result.collection = knowledge.collection
                    result.sources = [r.citation() for r in knowledge.records]
                    return knowledge_to_json(knowledge)
                if name == "validar_ocd" and knowledge is not None:
                    result.validations = validar_ocd(result.draft, knowledge)
                    return "[" + ",".join(v.model_dump_json() for v in result.validations) + "]"
                raise ServiceUnavailable(
                    "La herramienta solicitada no está permitida en esta etapa."
                )

            self.model.tools(execute)
            if not result.validations:
                raise ServiceUnavailable("La revisión documental no llegó a completarse.")
            result.status = "reviewed"
            absent = list(dict.fromkeys(field for v in result.validations for field in v.missing))
            result.questions = [f"Indica {field}." for field in absent]
            contradictions = [v for v in result.validations if v.status == "ERROR"]
            result.questions.extend(f"Revisa {v.rule_id}: {v.detail}" for v in contradictions)
            result.answer, _ = self._compose(message, result, result.sources, reviewing=True)
        except (ServiceUnavailable, ValidationError, KeyError, TypeError) as error:
            if result is None:
                # Mantener mensajes sin extraer para reintentarlos en el próximo turno.
                result = self.store.merge(session_id, Extraction(categories=[], facts=[]), [])
            result.status = "unavailable"
            result.answer = (
                "No se pudo completar la revisión. Conservamos el borrador y puedes reanudarlo."
            )
            result.error = (
                str(error)
                if isinstance(error, ServiceUnavailable)
                else "El servicio devolvió un contrato incompatible."
            )
        self.store.finish(session_id, result)
        return result


def knowledge_to_json(knowledge: Knowledge) -> str:
    return "[" + ",".join(r.citation().model_dump_json() for r in knowledge.records) + "]"
