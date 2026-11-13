import math
from typing import Protocol

from openai import OpenAI

from .models import Payload


class Embedder(Protocol):
    def embed(self, records: list[Payload]) -> list[list[float]]: ...


def check_vectors(vectors: list[list[float]], count: int) -> None:
    if len(vectors) != count:
        raise ValueError("Cantidad de embeddings incorrecta")
    for vector in vectors:
        if len(vector) != 1536 or not all(math.isfinite(v) for v in vector) or not any(vector):
            raise ValueError("Embedding inválido")


class OpenAIEmbedder:
    def __init__(self, client: OpenAI) -> None:
        self.client = client

    def embed(self, records: list[Payload]) -> list[list[float]]:
        vectors = []
        # 16 unidades de <=12000 caracteres limita también el total por solicitud.
        for start in range(0, len(records), 16):
            batch = records[start : start + 16]
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                dimensions=1536,
                input=[record.text for record in batch],
                encoding_format="float",
            )
            data = sorted(response.data, key=lambda item: item.index)
            if response.model != "text-embedding-3-small" or [d.index for d in data] != list(
                range(len(batch))
            ):
                raise ValueError("Respuesta de embeddings incompatible")
            vectors.extend(item.embedding for item in data)
        check_vectors(vectors, len(records))
        return vectors
