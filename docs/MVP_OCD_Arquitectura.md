# Arquitectura MVP OCD — Compose y Railway

Versión 0.6. Fecha: 13 de noviembre de 2026. Estado T1–T4.

## 1. Alcance y estado

La solución prepara un borrador OCD, solicita datos desconocidos y ejecuta
V-01/02/03 con fuentes y versiones. No crea tickets Jira ni ejecuta infraestructura.
En la red privada de Railway se verificó la carga de 83 puntos y la coincidencia
de las 24 citas y 19 referencias de una consulta. El entorno incorpora aplicación,
ingesta, Qdrant y MongoDB, con cuatro volúmenes persistentes.
El [diseño 0.4 histórico](https://github.com/miguelsff/grupo-visa-ai/blob/cb9d9fcb21ab89f8512ce2b4929195eb6ce15f5c/docs/MVP_OCD_Arquitectura.md)
conserva las propuestas anteriores de creación Jira y Railway.

| Capacidad | Estado en el código |
| --- | --- |
| Next.js estático y FastAPI | NexoOPS muestra conversación y búsqueda de procedimientos, con un borrador real por sesión. Los tickets de ejemplo y la agenda son demostraciones. |
| Cinco copias Markdown y cargador FTS5 | Legado sin uso en rutas HTTP de conocimiento. |
| Qdrant interno y contrato v1 | Implementado T1; persistencia histórica documentada por separado. |
| CLI, HTTPX Atlassian, embeddings y publicación atómica | Implementado T2. |
| Supercronic 03:00 America/Lima y bloqueo compartido | Implementado T2; disparo probado con horario temporal. |
| Responses API, herramientas, preguntas, sesiones y V-01/02/03 | Implementado T3; acceso al chat por HTTP y desde la interfaz estática. |
| Aceptación integrada | T4: Qdrant real y REST dobles; evidencia en `docs/verificacion_t4.md`. |
| Servicios externos autenticados | Lectura REST de Confluence y Jira, embeddings y Responses API verificados en Compose local. |
| Procedencia y relevancia | Las citas de una consulta coinciden con Qdrant. La evaluación general de relevancia sigue pendiente. |
| Creación Jira y ejecución de cambios de infraestructura desde el agente | Fuera del alcance del MVP. |

T4 identificó y corrigió la diferencia entre las condiciones publicadas por T2
y las firmas de reglas/fixtures del consumidor T3. La aceptación usa el índice
producido por la CLI: cinco páginas, 26 reglas y veinte tickets de ejemplo.

## 2. Componentes y ejecución

| Componente | Responsabilidad |
| --- | --- |
| `frontend/` | Next.js App Router, React, TypeScript y CSS Modules; `output: "export"`. |
| `backend/app/main.py` | FastAPI, rutas delgadas, ciclo de vida y estáticos; un worker Uvicorn. |
| `backend/app/agent/` | Casos de uso, hechos con evidencia, categorías, condiciones, V-01/02/03 y revisiones. |
| `backend/app/integrations/` | SDK oficial OpenAI, Responses API y estado de configuración. |
| `backend/app/knowledge/` | Cliente HTTPX Qdrant; paginación normativa y búsqueda semántica con referencias. |
| `ingesta/` | Proyecto Python independiente; HTTPX REST Atlassian/Qdrant, SDK OpenAI, CLI y publicación. |
| Qdrant | Vectores 1536/Cosine y payload trazable; imagen fijada `qdrant/qdrant:v1.16.3`. |
| SQLite | `/data/ocd.sqlite3`: saludos, sesiones, mensajes y revisiones; no se usa como conocimiento. |
| MongoDB | `ocd.preguntas` registra los mensajes del chat con fecha UTC, antes de procesarlos. Tiene volumen propio y acceso por red privada. |
| Supercronic | Mismo caso de uso `ocd-ingestar` manual/cron; 03:00 `America/Lima`. |

`docker compose up --build -d --wait` inicia app, Qdrant e ingesta. Solo app publica
`127.0.0.1:${APP_PORT:-8000}:8000`. Qdrant usa `http://qdrant:6333` dentro de Compose;
no publica 6333/6334. La red permite llamadas salientes. Node.js 24 interviene solo
en compilación; Python 3.14 ejecuta ambos proyectos independientes, con sus bloqueos.
HTTPX evita un SDK Qdrant adicional. Backend e ingesta no importan código entre sí.

El backend no descarga Atlassian ni ejecuta ingesta al arrancar. Compose entrega las
credenciales Atlassian exclusivamente a ingesta. La API `/api/integrations` describe
solo configuración del backend: los estados Jira/Confluence no inspeccionan ingesta,
no prueban conectividad y no deben interpretarse como estado de su carga.
`/api/health` verifica SQLite y estáticos sin llamadas externas ni datos de negocio.
Qdrant no tiene healthcheck propio en Compose; `--wait` no acredita corpus listo.

El ancla `x-knowledge-environment` se reutiliza en app e ingesta:
`QDRANT_ALIAS=ocd_actual`, `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`,
`OPENAI_EMBEDDING_DIMENSIONS=1536`. El modelo de conversación se obtiene de
`OPENAI_MODEL`, con decisión actual `gpt-6-luna`. No se usa para embeddings.

## 3. Conocimiento y publicación

El [contrato v1](contrato_conocimiento.md) define payload, UUIDv5 estables,
condiciones y procedencia. El [manifiesto](modelos_operativos/manifest.json)
limita lecturas a cinco páginas y veinte tickets. La ingesta contrasta reglas y
campos remotos con el manifiesto; conserva HTML, fechas y versiones. No sigue
instrucciones ni enlaces recuperados. Los Markdown son respaldo documental,
no sustitutos de las fuentes remotas. Los ejemplos son `normative=false`.

La primera carga es manual. CLI y cron usan `flock` compartido en `/state` para
impedir solapamientos. Cron usa `0 3 * * *`, `TZ=America/Lima` y tzdata; no recupera
ejecuciones omitidas durante apagados. Cada carga crea `ocd_<UUID>`, escribe e
inspecciona todos los puntos, índices y vectores antes de cambiar `ocd_actual`
mediante una solicitud atómica [S1, S2]. No sobrescribe una generación publicada.

El diario `/state/publication.json` registra propiedad, activa, anterior y candidata
con fsync y reemplazo atómico. Se conservan la activa y su predecesora. La limpieza
solo elimina colecciones propias sin alias. Ante respuesta perdida de la mutación,
se consulta su destino: confirmar la candidata activa permite devolver éxito;
no poder reconciliar conserva todo para el siguiente intento. Un cambio externo
inesperado del alias requiere revisión. Un fallo de carga conserva la última válida;
sin primera carga el consumidor responde indisponibilidad. No borrar el diario.

El backend resuelve el alias una vez por revisión, fija la colección física y
pagina todas las reglas comunes y campos/reglas de las categorías activas. Un
top-k no sustituye completitud. Los cinco resultados semánticos añaden apoyo.
Se validan hash, firma normativa, URL autorizada, UUID, modelo, dimensiones y
coherencia `ocd_<ingestion_run_id>`. Un payload malformado produce 503.

Cada revisión guarda colección física, referencias, versiones y extractos; puede
consultarse aunque la generación anterior ya no exista. Atlassian apagado no
impide consulta/chat del corpus publicado si Qdrant y OpenAI siguen disponibles.

## 4. Flujo implementado

1. Una cookie opaca HttpOnly/SameSite=strict identifica la sesión. SQLite conserva su hash.
2. El backend registra el texto del turno en MongoDB tras omitir los patrones de secretos conocidos. Si falla el registro, responde 503 antes de modificar el borrador.
3. El orquestador distingue saludos, temas ajenos, consultas de información y cambios al borrador. En un cambio, Responses API extrae hechos y categorías con cita literal e ID del mensaje.
4. La combinación transaccional admite mensajes no procesados, conserva hechos
   más recientes y permite retirar explícitamente categorías. No ejecuta red dentro de escrituras SQLite.
5. Para revisar un borrador, el agente recupera conocimiento de Qdrant y Python ejecuta V-01, V-02 y V-03. El agente arma la respuesta con lo declarado por el solicitante y la evidencia disponible. Una consulta sin respaldo recibe una respuesta de información insuficiente.
6. La API devuelve `answer` en el contrato habitual. Los turnos informativos conservan la revisión del borrador. Los cambios al borrador y sus validaciones se conservan en SQLite.

El único proceso backend serializa mensajes de una misma sesión; sesiones distintas
pueden progresar de forma independiente. Lotes extraídos solapados se filtran por
IDs no procesados en una transacción corta; no repiten revisión ni revierten correcciones.
Las revisiones numeradas conservan su resultado incluso ante fallos posteriores.
Un turno fallido genera estado `unavailable` y HTTP 503; GET permite consultar el
histórico. Mensajes cuya extracción falló quedan pendientes para el siguiente turno.

| Verificación | Comprobación |
| --- | --- |
| V-01 | Completitud común/específica según sección, condiciones `when` y etapa. |
| V-02 | Fechas/zona, versiones, artefactos, puertos, ambientes y alcance de permisos. |
| V-03 | Planes de ejecución, pruebas y reversión; regla, versión y evidencia. |

Estados: `CUMPLE`, `FALTA_INFORMACION`, `ERROR`, `NO_VERIFICABLE`.
Una revisión documental no acredita conectividad, recursos ni permisos efectivos.
Se mantienen desconocidos como pendientes, sin copiar datos de otros tickets.
Las zonas IANA con rutas inválidas se rechazan como datos, sin error HTTP 500.

## 5. Persistencia y seguridad

Conservar `sqlite_data`, `qdrant_data` e `ingesta_state`. No usar `down -v` en el
proyecto normal. Las pruebas crean y eliminan exclusivamente proyectos aleatorios.
El esquema SQLite existente conserva saludos y tablas legadas; T4 no cambia el esquema.
La copia/restauración anterior se documenta en la [evidencia T1](verificacion_t1.md).
Antes de otra migración, crear y restaurar una copia consistente.

Credenciales solo en variables de los procesos responsables; nunca frontend,
payload, logs, imagen ni Git. Las instrucciones recuperadas son datos sin autoridad.
Timeouts y reintentos son limitados; mutaciones Qdrant no se repiten automáticamente.
La detección de secretos es limitada. Backend e ingesta ejecutan como UID 10001.
En Railway, el dominio de `app` recibe HTTPS y dirige las solicitudes al puerto
8000. El backend exige autenticación HTTP Basic con el usuario de demostración
`demo` y la variable `OCD_DEMO_PASSWORD` de `app`. La comprobación de salud
`GET /api/health` es pública. La cookie `ocd_session` vincula cada borrador
a su sesión. Qdrant e ingesta usan la red privada del entorno.

## 6. Aceptación y límites

| Tarea | Evidencia |
| --- | --- |
| T1 | Qdrant real, alias/vector/payload persistidos al recrear; histórico `docs/verificacion_t1.md`. |
| T2 | pytest/Ruff, CLI, cron temporal, carga íntegra, bloqueo, idempotencia y fallos; `ingesta/VERIFICACION.md`. |
| T3/T4 | Dos turnos HTTP con cookie, 26 reglas/25 fuentes, citas reales del índice, fallos y recreación; `docs/verificacion_t4.md`. |
| Prueba con servicios externos reales | [Ingesta manual de 83 puntos y cotejo de 24 citas y 19 referencias de validación](verificacion_t4.md#ingesta-real-y-verificación-de-citas). |

Comandos reproducibles desde raíz:

```powershell
powershell -NoProfile -File scripts/Test-Aceptacion.ps1
powershell -NoProfile -File ingesta/Test-Ingesta.ps1
docker compose --profile test run --build --rm tests
docker compose --profile test run --build --rm tests ruff check --no-cache app tests
```

La prueba automatizada T4 usa Qdrant real y servidores de prueba para Atlassian y OpenAI.
La prueba posterior utilizó las API externas reales para la carga manual y un turno de chat HTTP.
La interfaz usa `POST /api/chat` para enviar mensajes y `GET /api/chat` para
recuperar la última revisión al abrir la página. La observación del cron de las 03:00 de Lima sigue pendiente.

## Referencias

- S1: [Qdrant: colecciones y alias](https://qdrant.tech/documentation/manage-data/collections/).
- S2: [Qdrant: operación de alias](https://api.qdrant.tech/master/api-reference/aliases/update-aliases).
- S3: [OpenAI: embeddings y dimensiones](https://developers.openai.com/api/docs/guides/embeddings).
- [Modelos operativos](modelos_operativos/README.md).
- [Contrato de conocimiento](contrato_conocimiento.md).

Diagrama editable: [MVP_OCD_Arquitectura.drawio](MVP_OCD_Arquitectura.drawio).
Vistas: Contexto local, Servicios locales y Contrato de conocimiento.
Vista previa: [MVP_OCD_Arquitectura.png](MVP_OCD_Arquitectura.png).
El amarillo identifica los servicios externos.

Regenerar la vista PNG en Windows con `uv run --no-project --with pillow python scripts/render_architecture.py`.
