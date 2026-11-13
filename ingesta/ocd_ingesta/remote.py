import time

import httpx


def request_json(client: httpx.Client, method: str, path: str, **kwargs) -> dict:
    """Solo las lecturas se reintentan; nunca repetir una publicación incierta."""
    attempts = 3 if method == "GET" else 1
    for attempt in range(attempts):
        try:
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as error:
            if error.response.status_code not in (429, 500, 502, 503, 504):
                raise
            if attempt == attempts - 1:
                raise
        except httpx.TransportError:
            if attempt == attempts - 1:
                raise
        time.sleep(0.2 * (attempt + 1))
    raise RuntimeError("Lectura agotada")


class Atlassian:
    def __init__(self, client: httpx.Client, manifest: dict) -> None:
        self.client = client
        self.pages = {p["pageId"] for p in [manifest["index"], *manifest["models"]]}
        self.tickets = {e["key"] for m in manifest["models"] for e in m["examples"]}

    def page(self, page_id: str) -> dict:
        if page_id not in self.pages:
            raise ValueError("Página fuera del manifiesto")
        return request_json(
            self.client, "GET", f"/wiki/api/v2/pages/{page_id}", params={"body-format": "view"}
        )

    def ticket(self, key: str) -> dict:
        if key not in self.tickets:
            raise ValueError("Ticket fuera del manifiesto")
        return request_json(
            self.client,
            "GET",
            f"/rest/api/3/issue/{key}",
            params={"fields": "summary,description,updated", "expand": "renderedFields"},
        )
