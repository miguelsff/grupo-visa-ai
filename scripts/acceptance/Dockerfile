FROM python:3.14-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*
COPY ingesta/tests/fixtures /fixtures
COPY scripts/acceptance/server.py /server.py
CMD ["python", "/server.py"]
