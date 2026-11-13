import json
import os
import re
from pathlib import Path

from .models import Payload
from .qdrant import Qdrant

GENERATION = re.compile(r"^ocd_[0-9a-f]{32}$")


class Publisher:
    """Diario durable de propiedad; recuperar antes de iniciar otra generación."""

    def __init__(self, qdrant: Qdrant, state_dir: Path) -> None:
        self.qdrant = qdrant
        self.path = state_dir / "publication.json"
        self.state = (
            json.loads(self.path.read_text())
            if self.path.exists()
            else {"owned": [], "active": None, "previous": None, "pending": None}
        )
        if not all(GENERATION.fullmatch(name) for name in self.state["owned"]):
            raise ValueError("Diario de publicación inválido")

    def save(self) -> None:
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(self.state, stream)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.path)
        # La imagen ejecuta Linux: fsync del directorio hace durable el rename.
        descriptor = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def recover(self) -> None:
        target = self.qdrant.target()
        pending = self.state["pending"]
        if pending:
            if target == pending["candidate"]:
                self.state["previous"] = pending["old"]
                self.state["active"] = target
            elif target != pending["old"]:
                raise ValueError("Destino del alias inesperado; conservar generaciones")
            self.state["pending"] = None
            self.save()
        if self.state["active"] is None:
            self.state["active"] = target
            self.save()
        if target != self.state["active"]:
            raise ValueError("Alias modificado fuera de la ingesta; requiere revisión")
        self.cleanup()

    def cleanup(self) -> None:
        protected = {self.state["active"], self.state["previous"]}
        for name in list(self.state["owned"]):
            if name not in protected and self.qdrant.delete_unpublished(name):
                self.state["owned"].remove(name)
                self.save()

    def publish(self, name: str, records: list[Payload], vectors: list[list[float]]) -> None:
        self.recover()
        if not GENERATION.fullmatch(name) or name in self.qdrant.collections():
            raise ValueError("Nombre de generación inválido o existente")
        old = self.state["active"]
        self.state["pending"] = {"candidate": name, "old": old}
        self.state["owned"].append(name)
        self.save()
        # Si cualquier operación falla, el diario conserva la recuperación pendiente.
        # Nunca limpiar a ciegas tras timeout de creación, escritura o cambio de alias.
        self.qdrant.create(name)
        self.qdrant.write(name, records, vectors)
        self.qdrant.verify(name, records, vectors)
        if self.qdrant.target() != old:
            raise ValueError("Alias cambió durante la carga")
        self.qdrant.switch(name, old)
        self.recover()
        if self.state["active"] != name:
            raise ValueError("La generación nueva no quedó publicada")
