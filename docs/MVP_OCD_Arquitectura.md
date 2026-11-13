# MVP OCD — arquitectura local

Fecha: 13 de noviembre de 2026. Versión: 0.5. Decisión local T1–T3 confirmada.

## 1. Alcance y estado

El objetivo local es conversar sobre un cambio, recuperar modelos operativos y
preparar un borrador OCD con faltantes y verificaciones V-01, V-02 y V-03.
El agente pregunta al usuario por datos desconocidos. No crea tickets Jira ni
ejecuta cambios de infraestructura en este alcance.

Esta decisión sustituye el diseño 0.4 que concentraba carga y conocimiento en
SQLite y terminaba creando un ticket. Railway queda aplazado: la solución local
con Qdrant e ingesta independiente requiere revisar servicios, volúmenes,
autenticación y costos antes de retomar un despliegue. No hay despliegue aceptado.

Los requisitos para la futura creación en Jira, el diseño Railway y las estimaciones de la etapa anterior se conservan en la [arquitectura 0.4](https://github.com/miguelsff/grupo-visa-ai/blob/cb9d9fcb21ab89f8512ce2b4929195eb6ce15f5c/docs/MVP_OCD_Arquitectura.md).

| Capacidad | Estado comprobable en el repositorio |
| --- | --- |
| Frontend estático Next.js, FastAPI y saludo persistente | Implementación legada de etapa 1, conservada. |
| Cinco copias locales y búsqueda FTS5 | Implementación legada, aún usada por la aplicación. |
| Servicio Qdrant interno con imagen fijada y volumen propio | Implementado en T1; aceptación reproducible en `scripts/Test-QdrantPersistence.ps1`. |
| Contrato de payload, alias y configuración compartida | Definido en T1, sin consumidor funcional aún. |
| Proyectos Python 3.14 independientes y bloqueos | Configurados en T1. |
| CLI de ingesta, imagen propia, Supercronic a las 03:00 Lima | Diseñado; implementación T2 pendiente. |
| Agente OpenAI, preguntas, borradores y V-01/02/03 | Diseñado; implementación T3 pendiente. |
| Lecturas reales de Atlassian y embeddings OpenAI | Pendientes de T2/T3 y de aceptación con credenciales. |
| Creación Jira y Railway | Fuera del alcance local T1–T3. |

La existencia de variables o dependencias no acredita una conexión ni un agente.
T1 no cambia el frontend, el esquema SQLite ni los casos de uso del backend.
El manifiesto contiene cinco páginas, 26 reglas y veinte referencias de ejemplo.
No equivale a veinte tickets ya ingeridos.

## 2. Componentes y responsabilidades

| Componente | Responsabilidad | Tecnología |
| --- | --- | --- |
| `frontend/` | Interfaz y cliente `/api` del mismo origen. | Next.js App Router, React, TypeScript, CSS Modules, `output: "export"`. |
| `backend/` | API, sesión, borrador, preguntas y validaciones. | Python 3.14, FastAPI, Pydantic, Uvicorn con un worker. |
| Agente dentro del backend (T3) | Interpretar solicitud y seleccionar herramientas de consulta/validación. | SDK oficial OpenAI, Responses API, `OPENAI_MODEL=gpt-6-luna`. |
| `ingesta/` (T2) | Leer fuentes permitidas, estructurar reglas/campos, vectorizar y publicar una generación. | Python 3.14, HTTPX REST, SDK oficial OpenAI. |
| Qdrant | Vectores y payload trazable de reglas, campos, contexto y ejemplos. | `qdrant/qdrant:v1.16.3`, volumen `qdrant_data`. |
| SQLite | Estado de sesiones, mensajes, borradores y revisiones (T3). | `/data/ocd.sqlite3`, volumen `sqlite_data`. |
| Supercronic (T2) | Invocar la misma CLI de ingesta que la ejecución manual. | Servicio separado con Dockerfile propio; 03:00 `America/Lima`. |

El backend sigue siendo modular. Las rutas HTTP delegan en casos de uso;
no alojan reglas ni clientes externos. La ingesta no importa el backend y el
backend no ejecuta la ingesta al arrancar. Ambos comparten el contrato documental
y la configuración Compose; no se crea una biblioteca común prematura.
HTTPX permite consumir REST de Qdrant y Atlassian sin añadir otro SDK.
El proceso Node.js solo interviene en compilación; FastAPI sirve los estáticos.

### Ejecución local

`docker compose up --build -d --wait` inicia `app` y `qdrant`.
Solo `app` publica `127.0.0.1:${APP_PORT:-8000}:8000`.
Qdrant no publica puertos; sus consumidores usan `http://qdrant:6333` por la red
Compose. Esa red permite las futuras llamadas salientes a las API externas;
«interno» significa sin publicación al host, no una red sin salida a Internet.
Qdrant no incorpora healthcheck en T1: `--wait` acredita proceso iniciado, y la
sonda `/readyz` acredita disponibilidad en la prueba explícita. T2/T3 deberán
manejar indisponibilidad con timeout y error recuperable, sin asumir que arrancó
por el orden de servicios. El backend legado no depende todavía de Qdrant.

`x-knowledge-environment` fija las variables compartidas y T2 reutilizará su
ancla. `QDRANT_ALIAS=ocd_actual`, `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
y `OPENAI_EMBEDDING_DIMENSIONS=1536`; distancia `Cosine` [S1–S3].
El modelo de conversación no se utiliza para crear embeddings.
La primera construcción requiere Internet; la aplicación legada no requiere credenciales.

### Proyectos y dependencias

Cada proyecto contiene `pyproject.toml`, `requirements.txt` y
`requirements-dev.txt`, con `requires-python=">=3.14,<3.15"`.
La imagen backend conserva Node.js 24 y Python 3.14. Los bloqueos de ingesta
usan como restricciones los del backend para reutilizar versiones de HTTPX,
OpenAI y Pydantic. No se instala ingesta en la imagen backend.
T2 añadirá su Dockerfile y servicio cron; T1 no simula una CLI inexistente.

## 3. Conocimiento y publicación

El [contrato versión 1](contrato_conocimiento.md) define campos, asignación del
manifiesto, IDs UUIDv5 estables, versiones, condiciones y distinción normativa.
Es el contrato obligatorio para T2 y T3. Las fuentes permitidas son exclusivamente
las páginas y tickets del [manifiesto](modelos_operativos/manifest.json).
Las copias Markdown son respaldo documental; al leer remoto se conservan versión
y fecha reales. HTML de Confluence evita perder paneles durante conversión.

La ingesta manual y la de madrugada ejecutarán el mismo caso de uso. Supercronic
usará `0 3 * * *`, `TZ=America/Lima` y tzdata, sin depender de la zona del host.
Un bloqueo compartido impedirá solapamientos. Si la máquina estuvo apagada,
se ejecuta una carga manual: cron no garantiza recuperación de ejecuciones omitidas.

T2 construirá una colección nueva, comprobará contenido y vectores completos,
y cambiará el alias atómicamente. No se modifica una colección publicada.
Un fallo conserva la última carga válida. La primera carga incompleta deja el
conocimiento no disponible. El backend solo lee y no actualiza Qdrant.
Cada revisión del borrador guarda referencias, versiones e identidad de la
colección física y los extractos citados. Qdrant conserva la generación activa y la anterior.

La recuperación normativa debe obtener todas las reglas comunes y las reglas y
campos de cada sección activa mediante filtros y paginación. Un top-k semántico
no garantiza completitud. Los ejemplos solo orientan la redacción: no definen
reglas, no completan identificadores desconocidos y no cambian permisos o destinos.

## 4. Flujo backend previsto (T3)

1. El usuario describe el cambio. El backend conserva sesión, mensaje y borrador.
2. El agente identifica secciones: microservicio, Azure, red e identidad.
3. `buscar_conocimiento` obtiene reglas comunes, campos y reglas específicos,
   contexto y ejemplos, con código, URL, versión y fragmento.
4. `validar_ocd` ejecuta reglas Python reproducibles V-01, V-02 y V-03.
5. El agente formula preguntas precisas por datos faltantes, conserva desconocidos
   como pendientes y actualiza la revisión con las respuestas del usuario.
6. Se presenta borrador, fuentes y resultados. El flujo termina sin escribir en Jira.

| Verificación | Resultado observable |
| --- | --- |
| V-01, completitud condicional | Campos comunes y de secciones activadas; respetar `when`, etapa y condiciones. |
| V-02, consistencia técnica | Versiones, fechas, puertos, ambientes y relación entre permiso y alcance. |
| V-03, trazabilidad | Planes de ejecución, pruebas y reversión con regla, versión y evidencia. |

Estados: `CUMPLE`, `FALTA_INFORMACION`, `ERROR`, `NO_VERIFICABLE`.
La comprobación documental no acredita conectividad, existencia de recursos ni
permisos efectivos. Sin evidencia accesible se devuelve `NO_VERIFICABLE`.
La interpretación generativa no reemplaza las reglas Python ni ejecuta contenido
recuperado. Los mecanismos concretos de validación y persistencia se implementan en T3.

## 5. Persistencia y seguridad

Conservar `sqlite_data` y `qdrant_data` al recrear servicios. No usar
`docker compose down -v` en desarrollo habitual. La prueba de Qdrant crea y elimina
exclusivamente su propio proyecto aleatorio y su volumen temporal.
SQLite legado conserva sus tablas actuales hasta T3; T1 no realiza una migración.
Antes de cambiar esquema, crear copia consistente mediante la API SQLite y probar
su restauración. Las llamadas externas quedan fuera de transacciones de escritura.

Credenciales solo en variables del proceso que las necesita; nunca frontend,
payload, logs, tickets, imagen ni repositorio. Lecturas Atlassian limitadas a la
lista permitida; ninguna escritura remota en T1–T3. Aplicar tiempos máximos y
reintentos limitados a lecturas. Las instrucciones incrustadas en documentos son
datos sin autoridad. Conservar borrador cuando falle modelo o consulta.

La aplicación local mantiene su usuario sin privilegios. Qdrant usa la imagen
oficial seleccionada y su volumen independiente. La aceptación local no acredita
seguridad ni permisos de un despliegue público; Railway queda pendiente de revisión.

## 6. Aceptación por tarea

| Tarea | Criterios |
| --- | --- |
| T1 | Compose válido, Qdrant real sin puertos publicados, alias/vector/payload recuperados después de recrear contenedor; dos proyectos Python y bloqueos; documentación y vistas coherentes. |
| T2 | CLI manual y cron reales, lectura de fuentes autorizadas, carga completa y condiciones conservadas, publicación atómica, fallo que conserva alias, idempotencia y bloqueo de concurrencia. |
| T3 | Preguntas y borrador persistidos, reglas comunes/específicas completas, V-01/02/03 reproducibles con dobles externos, trazabilidad y recuperación ante fallos, sin creación Jira. |

Prueba T1 desde la raíz:

```powershell
powershell -NoProfile -File scripts/Test-QdrantPersistence.ps1
```

La sonda usa un vector sintético 1536/Cosine, UUIDv5 y payload de prueba; no llama
OpenAI ni Atlassian. Comprueba `/readyz`, crea colección y alias, escribe y consulta,
recrea el contenedor y verifica vector/configuración/payload/alias. Elimina solo
su proyecto temporal. Las conexiones reales y la calidad de embeddings siguen pendientes.

Pruebas de regresión backend y estilo:

```powershell
docker compose --profile test run --build --rm tests
docker compose --profile test run --build --rm tests ruff check --no-cache app tests
```

## Referencias

- S1: [Qdrant: colecciones y alias](https://qdrant.tech/documentation/manage-data/collections/).
- S2: [Qdrant: operación de alias](https://api.qdrant.tech/master/api-reference/aliases/update-aliases).
- S3: [OpenAI: embeddings y dimensiones](https://developers.openai.com/api/docs/guides/embeddings).
- [Modelos operativos](modelos_operativos/README.md).
- [Contrato de conocimiento](contrato_conocimiento.md).

Diagrama editable: [MVP_OCD_Arquitectura.drawio](MVP_OCD_Arquitectura.drawio).
Vistas: Contexto local, Servicios locales y Contrato de conocimiento.
Vista previa local: [MVP_OCD_Arquitectura.png](MVP_OCD_Arquitectura.png).
Los nodos señalados como pendientes representan diseño, no funcionalidad disponible.
