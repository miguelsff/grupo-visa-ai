"""API y distribución del frontend estático."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.agent.service import say_hello
from app.config import Settings
from app.database import Database
from app.integrations.status import integration_status
from app.knowledge.loader import load_documents
from app.schemas import (
    Greeting,
    HealthResponse,
    HelloRequest,
    HelloResponse,
    IntegrationStatus,
    KnowledgeMatch,
)

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings or Settings.from_environment()
    database = Database(configuration.database_path)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        documents = load_documents(configuration.knowledge_dir)
        database.initialize(documents)
        logger.info("Base local preparada: %s documentos.", len(documents))
        yield

    application = FastAPI(title="Grupo VISA AI · Etapa 1", version="0.1.0", lifespan=lifespan)

    @application.exception_handler(sqlite3.Error)
    async def database_error(request: Request, error: sqlite3.Error) -> JSONResponse:
        logger.error("Falló una operación SQLite en %s: %s", request.url.path, type(error).__name__)
        return JSONResponse(
            status_code=503, content={"detail": "La base local no está disponible."}
        )

    @application.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse | JSONResponse:
        documents, greetings = database.counts()
        frontend_ready = (configuration.frontend_dir / "index.html").is_file()
        result = HealthResponse(
            frontend="ok" if frontend_ready else "missing",
            document_count=documents,
            greeting_count=greetings,
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
        return database.search(q)

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
