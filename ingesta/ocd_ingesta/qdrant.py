import httpx

from .models import Payload
from .remote import request_json


class Qdrant:
    def __init__(self, client: httpx.Client, alias: str = "ocd_actual") -> None:
        self.client = client
        self.alias = alias

    def call(self, method: str, path: str, **kwargs) -> dict:
        return request_json(self.client, method, path, **kwargs)["result"]

    def aliases(self) -> dict[str, str]:
        return {
            item["alias_name"]: item["collection_name"]
            for item in self.call("GET", "/aliases")["aliases"]
        }

    def target(self) -> str | None:
        return self.aliases().get(self.alias)

    def collections(self) -> set[str]:
        return {item["name"] for item in self.call("GET", "/collections")["collections"]}

    def create(self, name: str) -> None:
        self.call(
            "PUT", f"/collections/{name}", json={"vectors": {"size": 1536, "distance": "Cosine"}}
        )
        for field in ("kind", "scope", "source_id", "rule.id", "normative"):
            self.call(
                "PUT",
                f"/collections/{name}/index?wait=true",
                json={
                    "field_name": field,
                    "field_schema": "bool" if field == "normative" else "keyword",
                },
            )

    def write(self, name: str, records: list[Payload], vectors: list[list[float]]) -> None:
        for start in range(0, len(records), 32):
            points = [
                {"id": record.point_id, "payload": record.payload(), "vector": vector}
                for record, vector in zip(
                    records[start : start + 32], vectors[start : start + 32], strict=True
                )
            ]
            self.call("PUT", f"/collections/{name}/points?wait=true", json={"points": points})

    def verify(self, name: str, records: list[Payload], vectors: list[list[float]]) -> None:
        info = self.call("GET", f"/collections/{name}")
        if info["config"]["params"]["vectors"] != {"size": 1536, "distance": "Cosine"}:
            raise ValueError("Configuración Qdrant incompatible")
        indexes = info["payload_schema"]
        for field in ("kind", "scope", "source_id", "rule.id", "normative"):
            if indexes[field]["data_type"] != ("bool" if field == "normative" else "keyword"):
                raise ValueError("Índice Qdrant incompatible")
        expected = {r.point_id: (r.payload(), v) for r, v in zip(records, vectors, strict=True)}
        found = set()
        offset = None
        while True:
            body = {"limit": 64, "with_payload": True, "with_vector": True}
            if offset is not None:
                body["offset"] = offset
            page = self.call("POST", f"/collections/{name}/points/scroll", json=body)
            for point in page["points"]:
                point_id = point["id"]
                if point_id in found or point_id not in expected:
                    raise ValueError("Puntos Qdrant inesperados")
                payload, vector = expected[point_id]
                if point["payload"] != payload or len(point["vector"]) != 1536:
                    raise ValueError("Payload Qdrant incompleto")
                # Qdrant normaliza vectores Cosine y usa float32.
                norm = sum(v * v for v in vector) ** 0.5
                if any(
                    abs(a - b / norm) > 1e-5 for a, b in zip(point["vector"], vector, strict=True)
                ):
                    raise ValueError("Vector Qdrant distinto")
                found.add(point_id)
            offset = page["next_page_offset"]
            if offset is None:
                break
        if found != expected.keys():
            raise ValueError("Carga Qdrant incompleta")

    def switch(self, name: str, old: str | None) -> None:
        actions = []
        if old is not None:
            actions.append({"delete_alias": {"alias_name": self.alias}})
        actions.append({"create_alias": {"alias_name": self.alias, "collection_name": name}})
        self.call("POST", "/collections/aliases", json={"actions": actions})

    def delete_unpublished(self, name: str) -> bool:
        # No borrar ninguna colección referenciada por otro alias.
        if name in self.aliases().values():
            return False
        if name in self.collections():
            self.call("DELETE", f"/collections/{name}")
        return True
