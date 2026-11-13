# Grupo VISA AI

El repositorio utiliza [Gitflow automático](docs/gitflow_automatico.md): crea e
integra PR de funcionalidades, releases y hotfix sin aprobaciones ni checks
obligatorios. La publicación en Railway requiere verificar la entrega.

Asistente local para preparar un borrador OCD mediante conversación, conocimiento
Qdrant y validaciones Python V-01, V-02 y V-03. Permite publicar una vista previa
confirmada como Tarea Jira; no ejecuta cambios de infraestructura.

T1 integra Qdrant y el contrato; T2 implementa ingesta independiente, CLI y cron;
T3 implementa sesiones, extracción mediante Responses API y revisión persistente.
T4 reúne la aceptación de extremo a extremo y corrige los fallos de integración.
El 13 de noviembre de 2026, la ingesta real publicó 83 puntos en Qdrant a partir de cinco páginas de Confluence y veinte tickets de Jira.
En una consulta de microservicios coincidieron las 24 citas del agente y las referencias de sus 19 validaciones con los puntos publicados.
Consulta la [evidencia de la ingesta real y el cotejo de citas](docs/verificacion_t4.md#ingesta-real-y-verificación-de-citas).
La interfaz NexoOPS permite conversar con el agente y buscar procedimientos.
Mantiene un borrador real por sesión. Los tickets de ejemplo y la agenda son demostraciones.
La vista previa del chat corresponde a la revisión guardada y permite publicarla.

## Configurar y ejecutar

Requisitos: Docker Desktop con contenedores Linux, Compose y acceso a Internet
para construir las imágenes. Copia `.env.example` a `.env`. Configura:

| Variable | Uso |
| --- | --- |
| `APP_PORT` | Puerto local publicado solo en `127.0.0.1`; por defecto 8000. |
| `OCD_DEMO_USERNAME` | Usuario Basic de demostración de `app`; por defecto `demo`. |
| `OCD_DEMO_PASSWORD` | Contraseña Basic de demostración de `app`. Obligatoria en Railway y opcional en Compose local. |
| `MONGODB_URI` | Conexión privada de `app` para registrar cada mensaje aceptado en `ocd.preguntas`. Compose usa su servicio MongoDB y Railway usa una credencial propia de la aplicación. |
| `OPENAI_API_KEY` | Embeddings de ingesta/consulta e inferencia del backend. |
| `OPENAI_MODEL` | Modelo de conversación; decisión actual `gpt-6-luna`. |
| `ATLASSIAN_BASE_URL` | Origen HTTPS autorizado: `https://grupo-visai.atlassian.net`. |
| `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` | Solo ingesta; permiso de lectura sobre las 25 fuentes autorizadas. |
| `JIRA_BASE_URL` | Destino autorizado `https://grupo-visai.atlassian.net`. |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | Credenciales de publicación del backend; Compose recurre a las credenciales de ingesta si se omiten. |
| `JIRA_PROJECT_KEY`, `JIRA_ISSUE_TYPE_ID` | Destino fijado a `SCRUM` y tipo Tarea `10003`. |
| `QDRANT_ALIAS` | Contrato v1: `ocd_actual`. |
| `OPENAI_EMBEDDING_MODEL` | Contrato v1: `text-embedding-3-small`, 1536 dimensiones/Cosine. |

No guardar credenciales en Git ni usar `NEXT_PUBLIC_*`. El backend consulta el
corpus ya publicado y usa credenciales Jira para publicar. Sin clave OpenAI o sin
primera carga válida, chat/búsqueda devuelven 503; salud y saludo siguen disponibles.

Desde la raíz:

```powershell
docker compose up --build -d --wait
docker compose exec ingesta ocd-ingestar
docker compose logs ingesta
docker compose ps
```

Abre [la aplicación local](http://127.0.0.1:8000) y
[Swagger UI](http://127.0.0.1:8000/docs). La primera carga es manual; después,
Supercronic ejecuta `ocd-ingestar` cada día a las 03:00 `America/Lima`.
El bloqueo compartido evita cargas solapadas. Una máquina apagada no recupera
horarios omitidos: ejecuta la CLI manualmente. Consulta la [guía de ingesta](ingesta/README.md).

Para revisar la candidata integrada en el proyecto local de demostración, con el
archivo de entorno ya configurado y sin ejecutar una ingesta adicional:

```powershell
$env:APP_PORT = '3001'
docker compose -p ocd-demo-preview --env-file C:/Desarrollo/grupo-visa-ai/.env up -d --build --wait app
```

Abre [la candidata](http://localhost:3001). Escribe «Quiero hacer un pase a producción de mi microservicio.»;
cuando pregunte por servicio y versión, responde «Pedidos, versión 1.9.0. Corrige
la duplicación de pedidos.». Revisa la vista previa y los pendientes antes de decidir
si publicas. El botón de publicación usa las credenciales Jira configuradas en `app`.

```powershell
docker compose up -d --force-recreate --wait
docker compose down
```

Estos comandos conservan `sqlite_data`, `qdrant_data`, `mongo_data` e `ingesta_state`.
No usar `down -v` en el proyecto de aplicación. Qdrant no publica puertos al host.
`--wait` comprueba la salud local del backend y el proceso Qdrant; no verifica
conexiones externas ni que exista una generación publicada.

## Chat en dos turnos HTTP

En Railway, abre el dominio HTTPS de `app` e inicia sesión con el usuario
el usuario de `OCD_DEMO_USERNAME` y la contraseña de `OCD_DEMO_PASSWORD`. Escribe la consulta en el chat.
La página envía `POST /api/chat` al mismo dominio y conserva la cookie del
borrador. También puedes usar Swagger en `/docs`. En un cliente HTTP configura autenticación Basic y conserva
la cookie `ocd_session` entre turnos para continuar el mismo borrador.
`GET /api/health` permite comprobar la disponibilidad sin credenciales.

Ejemplo PowerShell. El modelo interpreta lenguaje natural; los datos desconocidos
permanecen pendientes. Conservar la misma cookie para continuar la sesión:

```powershell
$api = 'http://127.0.0.1:8000'
$turno1 = @{ message = 'Necesito publicar el microservicio de pedidos de la versión 1.0 a la 2.0 en producción. El título es Actualizar pedidos.' } | ConvertTo-Json
$r1 = Invoke-RestMethod "$api/api/chat" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($turno1)) -SessionVariable sesion
$r1.questions
$turno2 = @{ message = 'El artefacto es registry/pedidos:2.0. La ventana es del 2026-11-14T10:00:00-05:00 al 2026-11-14T11:00:00-05:00, zona America/Lima.' } | ConvertTo-Json
$r2 = Invoke-RestMethod "$api/api/chat" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($turno2)) -WebSession $sesion
$r2.draft
$r2.questions
$r2.validations
Invoke-RestMethod "$api/api/chat/revisions/1" -WebSession $sesion
```

En `POST /api/chat`, el campo `answer` contiene la respuesta que debe mostrar el cliente.
Un saludo presenta al asistente. Una pregunta sobre otro tema recibe una indicación
de su alcance. Ante una pregunta sobre una OCD, el agente consulta la evidencia y
explica qué puede confirmar. Si las fuentes y el borrador no contienen el dato,
lo indica. Por ejemplo, conocer la regla que exige registrar un responsable no
permite deducir quién es el responsable de un cambio concreto.

Solo los turnos que preparan o modifican una OCD crean una revisión del borrador. Los
mensajes de una sesión se procesan en orden dentro del único backend. Las citas
incluyen punto, código, URL, versión y extracto; cada revisión fija su colección
física. Se puede corregir un dato o retirar explícitamente una categoría del alcance.
No se reutilizan identificadores ni evidencias de tickets históricos como datos del usuario.

## API y recuperación

| Método y ruta | Semántica |
| --- | --- |
| `GET /api/health` | Disponibilidad local: SQLite, backend y archivos estáticos. No llama a servicios externos ni expone cantidades de negocio. |
| `GET/POST /api/hello` | Saludo persistente legado. POST recibe `{"name":"Equipo VISA"}`. |
| `GET /api/knowledge?q=microservicios` | Consulta Qdrant con embedding OpenAI; 503 sin conocimiento compatible o sin proveedor disponible. |
| `POST /api/chat` | Recibe `{"message":"..."}` y devuelve `answer`, el borrador y la evidencia aplicable al turno. Un fallo al registrar la pregunta o consultar una dependencia puede devolver 503. |
| `GET /api/chat` | Última revisión de la sesión, incluida una revisión indisponible. |
| `GET /api/chat/revisions/{revision}` | Revisión histórica de la misma sesión, conservada aunque fallen servicios o cambie el alias. |
| `POST /api/chat/revisions/{revision}/publish` | Publica la vista previa vigente de la sesión como Tarea SCRUM; devuelve clave y enlace. Una repetición confirmada recupera el resultado. |
| `GET /api/integrations` | Presencia de configuración del proceso backend; no prueba conexiones ni inspecciona el entorno de ingesta. |

Si falla Atlassian, la consulta y el chat siguen usando la última colección válida,
siempre que Qdrant y OpenAI estén disponibles. La ingesta fallida no sustituye el alias.
Si se pierde la respuesta al intercambio de alias, la CLI reconcilia su destino:
si la nueva colección está activa, informa éxito; si no puede confirmarlo, conserva
las generaciones y el diario para la siguiente ejecución. No editar ni borrar el diario.

Si falla OpenAI o Qdrant, el nuevo turno informa indisponibilidad y conserva el borrador.
Las revisiones ya validadas siguen consultables por número; tras recuperar el servicio,
envía otro mensaje con la misma cookie para reanudar. Recrear contenedores conserva
mensajes, revisiones y corpus. Perder la cookie impide recuperar la sesión desde el cliente.

## Componentes y límites

| Ruta | Responsabilidad |
| --- | --- |
| `frontend/` | Next.js App Router, React, TypeScript, CSS Modules; `output: "export"`. |
| `backend/app/main.py` | FastAPI, rutas delgadas y entrega de estáticos. |
| `backend/app/agent/` | Borrador, hechos con evidencia, condiciones y V-01/02/03. |
| `backend/app/knowledge/` | Recuperación exhaustiva normativa y búsqueda semántica Qdrant; FTS5 queda como código legado sin uso HTTP. |
| `backend/app/integrations/` | SDK oficial OpenAI y estado de configuración. |
| `backend/app/database.py` | SQLite `/data/ocd.sqlite3`: saludos, sesiones, mensajes y revisiones. |
| `ingesta/` | Proyecto Python independiente, HTTPX Atlassian/Qdrant, embeddings, publicación atómica, CLI y Supercronic. |
| `docs/contrato_conocimiento.md` | Payload, UUIDv5 estables, condiciones y generaciones. |

Un backend modular con un worker; Node.js 24 solo compila. Python 3.14 en ambos
proyectos. Qdrant real, ingesta y backend son procesos separados. Las cinco copias
Markdown documentan la demostración: la ingesta no las utiliza como sustituto remoto.
Las 26 reglas son sintéticas; los veinte tickets son ejemplos sin autoridad normativa.
`CUMPLE`, `FALTA_INFORMACION`, `ERROR` y `NO_VERIFICABLE` expresan comprobaciones
documentales, no permisos efectivos ni ejecución real. La búsqueda semántica usa
cinco resultados de apoyo; la recuperación normativa pagina todas las reglas y campos aplicables.
En la red privada de Railway se verificaron los tres servicios, la ingesta de
83 puntos y las citas de una consulta. La evaluación general de relevancia sigue pendiente.

## Verificación reproducible

Para probar la conversación y comprobar los registros en MongoDB contra la
instancia local ya iniciada, ejecuta el siguiente comando. Genera cinco mensajes
de demostración y hace llamadas reales al proveedor configurado.

```powershell
docker compose exec -T -e OCD_TEST_URL=http://127.0.0.1:8000 app python /opt/ocd/verify_conversation.py
```

```powershell
# E2E aislado: proyecto aleatorio, puerto libre, volúmenes temporales y dobles REST.
powershell -NoProfile -File scripts/Test-Aceptacion.ps1
# Ingesta, cron temporal, fallos y publicación contra Qdrant real aislado.
powershell -NoProfile -File ingesta/Test-Ingesta.ps1
# Regresión backend y estilo; sin usar volúmenes de la aplicación.
docker compose --profile test run --build --rm tests
docker compose --profile test run --build --rm tests ruff check --no-cache app tests
# Persistencia histórica T1, también aislada.
powershell -NoProfile -File scripts/Test-QdrantPersistence.ps1
```

La aceptación T4 no requiere credenciales reales: HTTPS Atlassian usa un certificado
y snapshots de prueba; OpenAI usa respuestas y vectores sintéticos. Qdrant, la CLI,
Responses SDK, FastAPI, cookies, SQLite y recreación de contenedores sí se ejecutan.
El mismo proyecto aislado comprueba el pase de Pedidos 1.9.0 y la publicación
HTTP contra Jira simulado, con credenciales y certificado ficticios. Comprueba el
contenido ADF, la clave, el enlace y la recuperación sin duplicar el POST. No verifica
la escritura ni los permisos del Jira real.
El script elimina exclusivamente su propio proyecto `ocd-t4-<UUID>` y sus volúmenes.
El frontend se construye mediante el Dockerfile normal con TypeScript y Next.js;
no se copian archivos compilados del proyecto principal.

Para dependencias frontend locales: `npm run typecheck` y `npm run build` desde `frontend/`.
Los bloqueos Python se actualizan desde `backend/`:

```powershell
uv pip compile pyproject.toml --python-version 3.14 --universal --output-file requirements.txt
uv pip compile pyproject.toml --extra dev --python-version 3.14 --universal --output-file requirements-dev.txt
```

Ingesta mantiene sus [bloqueos y restricciones](ingesta/README.md). Consulta la
[arquitectura](docs/MVP_OCD_Arquitectura.md), el [histórico T1](docs/verificacion_t1.md),
la [evidencia T2](ingesta/VERIFICACION.md) y la [aceptación T4](docs/verificacion_t4.md).
