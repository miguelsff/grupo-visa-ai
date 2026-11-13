# Ingesta OCD (T2)

Proyecto independiente, Python 3.14. Lee mediante HTTPX exclusivamente las cinco
páginas Confluence y los veinte tickets Jira autorizados por
[`manifest.json`](../docs/modelos_operativos/manifest.json). Usa HTML `view` de
Confluence y `renderedFields.description` de Jira. No sigue enlaces, consulta
adjuntos, comentarios, páginas hijas ni hace búsquedas. No escribe en Atlassian.
Las copias Markdown del repositorio no intervienen en ejecución.

## Ejecución

Configurar `ATLASSIAN_BASE_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` y
`OPENAI_API_KEY` en `.env`, sin incorporarlas al repositorio. El usuario Atlassian
necesita lectura de las fuentes autorizadas. Las variables de conocimiento
proceden del ancla `x-knowledge-environment` de Compose. La CLI rechaza alias,
modelo y dimensiones incompatibles con el [contrato v1](../docs/contrato_conocimiento.md).

Desde la raíz:

```powershell
docker compose up --build -d qdrant ingesta
docker compose exec ingesta ocd-ingestar
docker compose logs ingesta
```

La primera carga es manual. El servicio ejecuta Supercronic con `0 3 * * *`,
`TZ=America/Lima` y tzdata. Cron no recupera ejecuciones omitidas durante apagados.
`docker compose exec` ejecuta la misma CLI dentro del contenedor del cron; ambas
comparten un bloqueo no bloqueante `flock` en `/state`. Un segundo proceso termina
con código 1. No borrar el archivo del bloqueo.

`ingesta` no publica puertos, accede a Qdrant por la red Compose y ejecuta con
UID 10001. `ingesta_state` conserva el bloqueo y el diario `publication.json`.
Conservar este volumen junto con `qdrant_data`; no borrarlo para reiniciar una
carga ni ejecutar dos instalaciones con diarios distintos contra el mismo alias.
Un cambio externo del alias requiere revisión y detiene la limpieza automática.

## Contraste y fragmentación

Se comprueban ID, título, espacio, estado `current`, revisión Confluence,
versión documental y fecha. Las filas completas de reglas y campos deben coincidir
con el manifiesto, tras normalizar Unicode NFC y espacios del HTML. Una regla
añadida, retirada o modificada, incluidas condiciones, impide la publicación.
Los valores normativos del payload se extraen de las filas remotas contrastadas.
El manifiesto autoriza y valida: no sustituye una descarga ni aporta contexto local.

Cada regla o campo ocupa un punto completo. `applies_when` mantiene `Siempre`
para comunes; en reglas específicas conserva la sección y el resultado literal
que contiene su condición. En campos específicos conserva sección y `when`.
`rule.requirement` conserva `fields` en específicas y `condition` en comunes.
Las tablas normativas se retiran del contexto para evitar duplicarlas.

El contexto restante y los ejemplos se recorren en orden HTML: encabezados,
párrafos, elementos de lista, filas de tablas y bloques de código, sin duplicar
descendientes. Se conservan el texto de paneles, el atributo ISO de las fechas y
los destinos de enlaces como datos. Se agrupan unidades completas hasta 6000
caracteres, separadas por LF. Una unidad individual puede superar ese límite,
hasta 12000 caracteres; si lo supera se rechaza la carga. No se cortan reglas,
filas ni condiciones. Los ordinales empiezan en cero por fuente. Cambiar este
particionado puede cambiar los IDs del contexto y de los ejemplos.

Los tickets son `example`, `normative=false`. Su ID numérico y fecha de
actualización proceden de Jira; nunca se inventan. Se conservan código, título,
URL, versión, hash y localizador. Todo `source.local_file` es `null`.
El contenido remoto se trata como datos, incluidas instrucciones sobre el alcance
anterior del MVP: no autoriza herramientas ni cambia los destinos configurados.

Se detectan coincidencias con credenciales configuradas y patrones de secretos
antes de vectorizar. Esta detección es limitada; no acredita ausencia universal
de secretos. Los logs contienen códigos de fuente, cantidades y UUID de carga;
no imprimen cuerpos remotos, cabeceras, claves ni mensajes de excepción externos.

## Embeddings y publicación

El SDK oficial OpenAI genera `text-embedding-3-small`, 1536 dimensiones, en lotes
de hasta 16 unidades, con timeout de 60 segundos y dos reintentos. HTTPX usa
timeout de 30 segundos y hasta tres intentos solo para GET transitorios. Las
mutaciones Qdrant no se repiten automáticamente.

La colección nueva `ocd_<UUID>` recibe la carga completa e índices de `kind`,
`scope`, `source_id`, `rule.id` y `normative`. Antes de publicar se recuperan todos
los puntos por paginación y se contrastan IDs, payloads y vectores normalizados.
Se comprueban cinco páginas, 26 reglas, todos los campos y veinte IDs Jira distintos.

Una sola solicitud Qdrant cambia `ocd_actual` atómicamente. El diario se escribe
con `fsync` y reemplazo atómico antes de crear la colección. Se conservan la activa
y su predecesora; solo se eliminan colecciones registradas como propias y sin
ningún alias. No se eliminan colecciones ajenas aunque su nombre empiece con `ocd_`.

Si se pierde la respuesta al cambiar el alias, se consulta su destino antes de
limpiar. Si Qdrant no responde, se conservan todas las generaciones y el diario
pendiente. La siguiente CLI reconcilia el diario antes de descargar fuentes.
Un fallo parcial conserva la colección publicada. La recuperación no ejecuta
lecturas locales como sustituto de las fuentes remotas.

## Pruebas aisladas

```powershell
powershell -NoProfile -File ingesta/Test-Ingesta.ps1
```

El script crea un proyecto Docker aleatorio `ocd-t2-<UUID>`, Qdrant real y un
volumen temporal. No publica puertos ni inicia la aplicación normal. Al finalizar
elimina exclusivamente ese proyecto y volumen. Ejecuta pytest y Ruff con Python
3.14. Los dobles Atlassian usan snapshots HTML reales; el SDK OpenAI llama a
un servidor HTTP sintético dentro del contenedor, sin llamadas pagadas. La prueba
Supercronic cambia solo su archivo temporal a una frecuencia de segundos e
invoca la CLI real contra ese Qdrant aislado.

Los snapshots y el inyector `tests/cron_support` solo se copian a la imagen de
pruebas. La imagen `runtime` contiene únicamente código, manifiesto y crontab.
El [origen de los fixtures](tests/fixtures/README.md) distingue capturas reales de
respuestas sintéticas. La aceptación con credenciales REST y embeddings reales
se debe ejecutar por separado; las pruebas no la acreditan.

Desde `ingesta/`, actualizar los bloqueos:

```powershell
uv pip compile pyproject.toml --constraint ../backend/requirements.txt --python-version 3.14 --universal --output-file requirements.txt
uv pip compile pyproject.toml --extra dev --constraint ../backend/requirements-dev.txt --python-version 3.14 --universal --output-file requirements-dev.txt
```

La documentación general de la aplicación y su arquitectura se actualizarán en
T4. El backend legado no consume esta ingesta hasta T3.
