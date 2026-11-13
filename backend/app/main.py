"""API y distribución del frontend estático."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.agent.chat import ChatService, KnowledgeReader
from app.agent.models import ChatResponse, ServiceUnavailable
from app.agent.service import say_hello
from app.agent.store import ChatStore
from app.auth import require_demo_login
from app.config import Settings
from app.database import Database
from app.integrations.openai import OpenAIIntegration, Orchestrator
from app.integrations.questions import QuestionLog, QuestionLogUnavailable
from app.integrations.status import integration_status
from app.knowledge.qdrant import QdrantKnowledge
from app.schemas import (
    ChatRequest,
    Greeting,
    HealthResponse,
    HelloRequest,
    HelloResponse,
    IntegrationStatus,
    KnowledgeMatch,
)

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    model: Orchestrator | None = None,
    knowledge: KnowledgeReader | None = None,
) -> FastAPI:
    configuration = settings or Settings.from_environment()
    database = Database(configuration.database_path)
    store = ChatStore(database)
    integration = OpenAIIntegration(configuration)
    client = httpx.Client(base_url=configuration.qdrant_url, timeout=configuration.external_timeout)
    reader = knowledge or QdrantKnowledge(configuration, integration, client)
    chat = ChatService(store, model or integration, reader)
    questions = QuestionLog(configuration.mongodb_uri) if configuration.mongodb_uri else None

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        try:
            yield
        finally:
            integration.close()
            client.close()
            if questions is not None:
                questions.close()

    application = FastAPI(title="Grupo VISA AI · OCD local", version="0.3.0", lifespan=lifespan)
    if configuration.demo_password:
        require_demo_login(application, configuration.demo_username, configuration.demo_password)

    @application.exception_handler(sqlite3.Error)
    async def database_error(request: Request, error: sqlite3.Error) -> JSONResponse:
        logger.error("Falló una operación SQLite en %s: %s", request.url.path, type(error).__name__)
        return JSONResponse(
            status_code=503, content={"detail": "La base local no está disponible."}
        )

    @application.head("/api/health", response_model=HealthResponse, include_in_schema=False)
    @application.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse | JSONResponse:
        database.available()
        frontend_ready = (configuration.frontend_dir / "index.html").is_file()
        result = HealthResponse(
            frontend="ok" if frontend_ready else "missing",
        )
        if not frontend_ready:
            return JSONResponse(status_code=503, content=result.model_dump())
        return result

    @application.get("/api/hello", response_model=HelloResponse)
    def hello() -> HelloResponse:
        return HelloResponse(
            message="Hola mundo desde FastAPI", greetings=database.list_greetings()
        )

    @application.post("/api/hello", response_model=Greeting, status_code=201)
    def create_hello(body: HelloRequest) -> Greeting:
        return say_hello(body.name, database)

    @application.get("/api/knowledge", response_model=list[KnowledgeMatch])
    def search_knowledge(
        q: Annotated[str, Query(min_length=1, max_length=200)],
    ) -> list[KnowledgeMatch]:
        try:
            return reader.search(q)
        except ServiceUnavailable as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    def chat_response(
        request: Request, body: ChatRequest | None = None, revision: int | None = None
    ) -> JSONResponse:
        session_id, token = store.session(request.cookies.get("ocd_session"))
        result = chat.handle(session_id, body.message) if body else store.get(session_id, revision)
        if revision is not None and result.revision == 0:
            raise HTTPException(status_code=404, detail="La revisión no existe en esta sesión.")
        response = JSONResponse(
            status_code=503 if result.status == "unavailable" and body else 200,
            content=result.model_dump(mode="json"),
        )
        response.headers["Cache-Control"] = "no-store"
        if token:
            response.set_cookie(
                "ocd_session",
                token,
                httponly=True,
                samesite="strict",
                secure=configuration.on_railway or request.url.scheme == "https",
                path="/api/chat",
            )
        return response

    @application.post("/api/chat", response_model=ChatResponse)
    def post_chat(body: ChatRequest, request: Request) -> JSONResponse:
        if questions is not None:
            try:
                questions.record(body.message)
            except QuestionLogUnavailable:
                raise HTTPException(
                    503, "No se pudo confirmar el registro de la pregunta."
                ) from None
        return chat_response(request, body)

    @application.get("/api/chat", response_model=ChatResponse)
    def get_chat(request: Request) -> JSONResponse:
        return chat_response(request)

    @application.get("/api/chat/revisions/{revision}", response_model=ChatResponse)
    def get_revision(request: Request, revision: int) -> JSONResponse:
        if revision < 1:
            raise HTTPException(status_code=404, detail="La revisión no existe en esta sesión.")
        return chat_response(request, revision=revision)

    @application.get("/api/integrations", response_model=list[IntegrationStatus])
    def integrations() -> list[IntegrationStatus]:
        return integration_status(configuration)

    @application.api_route(
        "/api/{path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    def unknown_api(path: str) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "La ruta de API no existe."})

    application.mount(
        "/",
        StaticFiles(directory=configuration.frontend_dir, html=True, check_dir=False),
        name="frontend",
    )
    return application


app = create_app()
