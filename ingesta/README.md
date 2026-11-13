# Proyecto de ingesta (T2 pendiente)

T1 fija el proyecto Python 3.14 y sus dependencias, independientes del backend.
No existe todavía CLI, Dockerfile, servicio cron ni lectura remota implementada.
HTTPX permite usar REST de Atlassian y Qdrant; el SDK oficial OpenAI calcula embeddings.
No se añade otro cliente Qdrant ni un framework de agentes.

Contrato obligatorio: [payload y publicación](../docs/contrato_conocimiento.md).
Fuentes permitidas: [manifiesto](../docs/modelos_operativos/manifest.json).

T2 implementará un único comando idempotente para la ejecución manual y Supercronic.
El horario será `0 3 * * *`, con `TZ=America/Lima` y tzdata en su propia imagen.
No se inicia la ingesta desde FastAPI. Un bloqueo impide solapar ejecuciones manuales y cron.
Los fallos conservan el alias publicado; una colección incompleta no se activa.
La primera carga requiere ejecución manual: cron no recupera ejecuciones perdidas.

Desde `ingesta/`, actualizar los bloqueos conservando versiones comunes del backend:

```powershell
uv pip compile pyproject.toml --constraint ../backend/requirements.txt --python-version 3.14 --universal --output-file requirements.txt
uv pip compile pyproject.toml --extra dev --constraint ../backend/requirements-dev.txt --python-version 3.14 --universal --output-file requirements-dev.txt
```

La imagen y los tests propios se implementan en T2. Este proyecto no se instala en la imagen del backend.
