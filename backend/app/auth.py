"""Control de acceso de demostración para la API y los archivos estáticos."""

from base64 import b64encode
from secrets import compare_digest

from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, Response


def require_demo_login(application: FastAPI, password: str) -> None:
    expected = b64encode(f"demo:{password}".encode())

    @application.middleware("http")
    async def authenticate(request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.scope["path"] == "/api/health" and request.method in {"GET", "HEAD"}:
            return await call_next(request)
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "basic" or not compare_digest(token.encode("latin-1"), expected):
            return JSONResponse(
                {"detail": "Se requieren las credenciales de demostración."},
                status_code=401,
                headers={
                    "WWW-Authenticate": 'Basic realm="OCD", charset="UTF-8"',
                    "Cache-Control": "no-store",
                },
            )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response
