"""Caso de uso de chat: guardar, interpretar, recuperar y validar sin escrituras remotas."""

from threading import Lock
from typing import Protocol

from pydantic import ValidationError

from app.agent.facts import grounded, redact
from app.agent.models import Category, ChatResponse, Extraction, ServiceUnavailable
from app.agent.store import ChatStore
from app.agent.validation import validar_ocd
from app.integrations.openai import Orchestrator
from app.knowledge.models import Knowledge
from app.schemas import KnowledgeMatch


class KnowledgeReader(Protocol):
    def resolve(self) -> str: ...
    def retrieve(self, collection: str, categories: list[Category], query: str) -> Knowledge: ...
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
        self.store.append(session_id, redact(message))
        pending = self.store.pending(session_id)
        previous = self.store.get(session_id)
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
            result.answer = (
                "Borrador guardado y revisado. "
                + (
                    "Completa o corrige los datos indicados."
                    if result.questions
                    else "Los datos están completos para las comprobaciones disponibles."
                )
                + " La ejecución, los permisos y las evidencias técnicas siguen pendientes."
            )
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
