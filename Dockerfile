FROM node:24-alpine AS frontend
WORKDIR /build/frontend
ENV NEXT_TELEMETRY_DISABLED=1
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run typecheck && npm run build

FROM python:3.14-slim AS application
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATABASE_PATH=/data/ocd.sqlite3 \
    KNOWLEDGE_DIR=/app/knowledge \
    FRONTEND_DIR=/app/static
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /data \
    && chown app:app /data
COPY backend/app/ ./app/
COPY docs/modelos_operativos/ ./knowledge/
COPY --from=frontend /build/frontend/out/ ./static/
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM application AS tests
USER root
COPY backend/requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY backend/tests/ ./tests/
COPY backend/pyproject.toml ./pyproject.toml
USER app
CMD ["pytest", "-q", "-p", "no:cacheprovider"]

FROM application AS runtime
