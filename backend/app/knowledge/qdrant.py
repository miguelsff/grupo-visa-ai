"""Lecturas Qdrant fijadas a una generación, con paginación normativa completa."""

import re
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from app.agent.catalog import CATEGORY_FIELDS, RULE_IDS
from app.agent.models import Category, ServiceUnavailable
from app.config import Settings
from app.knowledge.models import Embedder, Knowledge, Record, parse_record
from app.schemas import KnowledgeMatch


class QdrantKnowledge:
    def __init__(self, settings: Settings, embedder: Embedder, client: httpx.Client) -> None:
        self.settings = settings
        self.embedder = embedder
        self.client = client

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        for attempt in range(2):
            try:
                response = self.client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()["result"]
            except (httpx.TimeoutException, httpx.NetworkError) as error:
                if attempt:
                    raise ServiceUnavailable("Qdrant no está disponible.") from error
            except (httpx.HTTPStatusError, ValueError, KeyError) as error:
                raise ServiceUnavailable("Qdrant no tiene conocimiento disponible.") from error
        raise ServiceUnavailable("Qdrant no está disponible.")

    def resolve(self) -> str:
        aliases = self._request("GET", "/aliases")["aliases"]
        names = [
            a["collection_name"] for a in aliases if a["alias_name"] == self.settings.qdrant_alias
        ]
        if len(names) != 1:
            raise ServiceUnavailable("No hay una colección de conocimiento publicada.")
        name = names[0]
        config = self._request("GET", f"/collections/{quote(name, safe='')}")
        vectors = config["config"]["params"]["vectors"]
        if vectors.get("size") != 1536 or vectors.get("distance") != "Cosine":
            raise ServiceUnavailable("La colección tiene una configuración incompatible.")
        return name

    def retrieve(self, collection: str, categories: list[Category], query: str) -> Knowledge:
        scopes = ["comun", *categories]
        filters = {
            "must": [
                {"key": "scope", "match": {"any": scopes}},
                {"key": "normative", "match": {"value": True}},
            ]
        }
        records: list[Record] = []
        offset = None
        seen_offsets: set[str] = set()
        while True:
            page = self._request(
                "POST",
                f"/collections/{quote(collection, safe='')}/points/scroll",
                json={
                    "filter": filters,
                    "limit": 64,
                    "offset": offset,
                    "with_payload": True,
                    "with_vector": False,
                },
            )
            records.extend(self._parse(p, collection) for p in page["points"])
            offset = page["next_page_offset"]
            if offset is None:
                break
            if str(offset) in seen_offsets:
                raise ServiceUnavailable("La paginación normativa es inconsistente.")
            seen_offsets.add(str(offset))
            if len(seen_offsets) > 128:
                raise ServiceUnavailable("La paginación normativa superó el límite de seguridad.")
        expected = {f"{scope}:rule:{r}" for scope in scopes for r in RULE_IDS[scope]}
        expected |= {
            f"{scope}:field:{name}" for scope in categories for name in CATEGORY_FIELDS[scope]
        }
        actual = [f"{r.payload.scope}:{r.payload.record_key}" for r in records]
        if set(actual) != expected or len(actual) != len(expected):
            raise ServiceUnavailable(
                "La generación no contiene todas las reglas y campos aplicables."
            )
        records.extend(self.semantic(collection, query, scopes, normative=False))
        return Knowledge(collection, records)

    def semantic(
        self, collection: str, query: str, scopes: list[str], normative: bool | None = None
    ) -> list[Record]:
        must: list[dict[str, Any]] = [{"key": "scope", "match": {"any": scopes}}]
        if normative is not None:
            must.append({"key": "normative", "match": {"value": normative}})
        vector = self.embedder.embed(query)
        if len(vector) != 1536:
            raise ServiceUnavailable("El embedding de consulta tiene una dimensión incompatible.")
        result = self._request(
            "POST",
            f"/collections/{quote(collection, safe='')}/points/query",
            json={
                "query": vector,
                "filter": {"must": must},
                "limit": 5,
                "with_payload": True,
                "with_vector": False,
            },
        )
        records = [self._parse(point, collection) for point in result["points"]]
        if any(
            r.payload.scope not in scopes
            or (normative is not None and r.payload.normative != normative)
            for r in records
        ):
            raise ServiceUnavailable("La búsqueda devolvió registros fuera del filtro autorizado.")
        return records

    def _parse(self, point: dict[str, Any], collection: str) -> Record:
        record = parse_record(point)
        if not re.fullmatch(r"ocd_[0-9a-f]{32}", collection) or (
            collection != "ocd_" + record.payload.ingestion_run_id
        ):
            raise ServiceUnavailable("La generación física no coincide con el payload.")
        return record

    def search(self, query: str) -> list[KnowledgeMatch]:
        try:
            collection = self.resolve()
            records = self.semantic(collection, query, ["comun", *CATEGORY_FIELDS])
            return [
                KnowledgeMatch(
                    code=r.payload.source.code,
                    title=r.payload.source.title,
                    url=r.payload.source.url,
                    version=r.payload.source.version,
                    excerpt=r.payload.text,
                )
                for r in records
            ]
        except (ValidationError, KeyError, TypeError) as error:
            raise ServiceUnavailable("El conocimiento tiene un contrato incompatible.") from error
