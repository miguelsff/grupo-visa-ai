import argparse
import fcntl
import logging
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
from openai import OpenAI

from .config import Config
from .content import collect, load_manifest
from .embeddings import OpenAIEmbedder
from .publication import Publisher
from .qdrant import Qdrant
from .remote import Atlassian
from .safety import check_secrets

logger = logging.getLogger("ocd.ingesta")


@contextmanager
def ingestion_lock(state_dir: Path):
    state_dir.mkdir(parents=True, exist_ok=True)
    # El archivo nunca se elimina: todos los procesos bloquean el mismo inode.
    with (state_dir / "ingestion.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Ya existe una ingesta en ejecución") from error
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def run(config: Config) -> str:
    with ingestion_lock(config.state_dir):
        manifest = load_manifest(config.manifest, config.base_url)
        with httpx.Client(base_url=config.qdrant_url, timeout=30, follow_redirects=False) as qc:
            publisher = Publisher(Qdrant(qc, config.alias), config.state_dir)
            publisher.recover()
            run_id = uuid4().hex
            loaded_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
            with httpx.Client(
                base_url=config.base_url,
                auth=(config.email, config.token),
                timeout=30,
                follow_redirects=False,
            ) as ac:
                records = collect(Atlassian(ac, manifest), manifest, run_id, loaded_at)
            check_secrets(records, (config.token, config.openai_key, config.email))
            with OpenAI(api_key=config.openai_key, timeout=60, max_retries=2) as client:
                vectors = OpenAIEmbedder(client).embed(records)
            try:
                publisher.publish("ocd_" + run_id, records, vectors)
            except Exception:
                # Reconciliar también al fallar; si no se puede leer el alias,
                # conservar todo y dejar el diario para la próxima ejecución.
                try:
                    publisher.recover()
                except Exception:
                    logger.error("Recuperación pendiente; se conservaron las generaciones")
                raise
            logger.info("Carga publicada run=%s puntos=%d", run_id, len(records))
            return run_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Publicar conocimiento OCD desde fuentes remotas")
    parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    # Los clientes no deben registrar URL, cabeceras ni cuerpos remotos.
    for name in ("httpx", "httpcore", "httpx2", "httpcore2", "openai"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    try:
        run(Config.from_env())
    except Exception as error:
        # Mensajes de librerías pueden contener cuerpos o credenciales: solo clase.
        logger.error(
            "Ingesta fallida (%s); revisar configuración o fuente autorizada", type(error).__name__
        )
        return 1
    return 0
