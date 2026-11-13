FROM python:3.14-slim AS base
ARG TARGETARCH
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=America/Lima
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl tzdata \
    && rm -rf /var/lib/apt/lists/*
RUN case "$TARGETARCH" in \
      amd64) checksum=798d0f6cf11cb74109b6408c50b1222cdd7678e8e70895dcfa9c2701b4bd03d5 ;; \
      arm64) checksum=5f8d5ed5e02734b68d2d908719297f8558c2edbeb407072f86ed024a7b6ac74e ;; \
      *) exit 1 ;; esac \
    && curl -fsSL "https://github.com/aptible/supercronic/releases/download/v0.2.41/supercronic-linux-${TARGETARCH}" -o /usr/local/bin/supercronic \
    && echo "$checksum  /usr/local/bin/supercronic" | sha256sum -c - \
    && chmod 755 /usr/local/bin/supercronic
WORKDIR /app
COPY ingesta/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt setuptools==82.0.0
COPY ingesta/pyproject.toml ./pyproject.toml
COPY ingesta/ocd_ingesta ./ocd_ingesta
RUN pip install --no-cache-dir --no-deps --no-build-isolation . \
    && useradd --uid 10001 --create-home ingesta \
    && mkdir /state && chown ingesta:ingesta /state
COPY docs/modelos_operativos/manifest.json ./manifest.json
COPY ingesta/crontab ./crontab

FROM base AS tests
COPY ingesta/requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY ingesta/tests ./tests
COPY docs/ocd_payload.schema.json ./ocd_payload.schema.json
USER ingesta
CMD ["pytest", "-q"]

FROM base AS runtime
USER ingesta
CMD ["supercronic", "/app/crontab"]
