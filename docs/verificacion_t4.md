# Aceptación T4 del flujo OCD local

Fecha: 13 de noviembre de 2026. Rama `feature/t4-aceptacion-ocd`.
Base comprobada: `ee42926`, misma revisión que `feature/estructura-backend-ingestor`,
con T1 y los commits `1da168c` (T2) y `ec236e5` (T3) integrados. Checkout inicial
limpio y separado del principal. No se modifica el frontend ni el esquema SQLite.

## Entorno y reproducción

Desde la raíz, con Docker Desktop Linux:

```powershell
powershell -NoProfile -File scripts/Test-Aceptacion.ps1
powershell -NoProfile -File ingesta/Test-Ingesta.ps1
docker compose config --quiet
```

`Test-Aceptacion.ps1` combina Compose normal con `scripts/acceptance/compose.yaml`.
Genera `ocd-t4-<UUID>`, asigna un puerto libre en `127.0.0.1` y conserva todos los
volúmenes dentro de ese proyecto temporal. Un archivo de entorno temporal evita
cargar `.env`; el override fija claves ficticias y endpoints sintéticos. Solo al
terminar elimina su proyecto/volúmenes. No utiliza el volumen principal.
La posible carrera por el puerto libre se informa como fallo de arranque, sin
seleccionar ni modificar otro contenedor. No se publica Qdrant ni los servidores dobles.

El servidor doble HTTPS usa el nombre autorizado de Atlassian como alias de red
Compose, un certificado efímero generado al arrancar y snapshots de T2. La CLI
usa HTTPX real, autenticación ficticia y validación TLS con ese certificado. No
se desactiva TLS ni se sustituye el transporte HTTPX en esta aceptación E2E.
El doble OpenAI REST recibe al SDK oficial para embeddings y Responses; devuelve
extracción, llamadas de herramientas y vectores sintéticos. La extracción del
doble admite entradas deterministas `seccion.campo=valor`; no prueba interpretación
semántica de lenguaje natural. El ejemplo de dos turnos reales está en el README.

## Comprobaciones del escenario E2E

| Comprobación | Evidencia observable |
| --- | --- |
| Primera carga CLI | 83 puntos, cinco fuentes Confluence, veinte fuentes Jira y 26 reglas. Cada punto se admite por el contrato del consumidor. |
| Repetición | Otra colección física, mismos 83 UUIDv5; sin duplicados en el corpus activo. Cada payload coincide con el `ingestion_run_id` físico. |
| Dos turnos HTTP | Misma cookie HttpOnly/SameSite=strict y revisiones 1 y 2; conserva título y añade versión objetivo/zona. |
| Completitud normativa | Cuatro categorías activas: las 26 reglas recuperadas y resultados con faltantes/preguntas. |
| Citas | ID, URL, versión y extracto contrastados contra los puntos efectivamente publicados por la CLI, sin usar `backend/tests/fixtures/points.json`. |
| Atlassian apagado | Nueva carga CLI falla; alias no cambia. Búsqueda y revisión 3 siguen disponibles. |
| OpenAI apagado | Nuevo turno responde 503/`unavailable`, conserva hechos y deja extracción pendiente. La revisión 3 validada continúa consultable por número. |
| Recreación | App y Qdrant recreados con los mismos volúmenes temporales; cookie, revisiones, citas y alias conservados. |
| Reanudación | Siguiente turno crea revisión 5 y procesa el hecho pendiente del turno fallido. |
| Salud local | HTTP desde host al puerto aislado y desde contenedor; SQLite, backend y frontend disponibles. No consulta servicios externos. |

Los marcadores `ACEPTADO first`, `ACEPTADO chat`, `ACEPTADO offline` y
`ACEPTADO resume` aparecen solo después de sus aserciones. El script además
construye y ejecuta pytest/Ruff del backend con bases temporales.

## Defectos corregidos y regresión

- T2 publica las condiciones específicas con resultado literal; las firmas y el
  fixture T3 esperaban solo la sección. Se ajustaron las veinte firmas y se
  regeneró el corpus backend mediante `collect` sobre los snapshots de T2.
- Timeout después del cambio de alias: consultar el destino permite éxito si la
  candidata ya está activa. Si el alias no se puede consultar, se conservan diario
  y generaciones; no se repite una mutación incierta.
- El productor y consumidor exigen `ocd_<ingestion_run_id>` coherente. El consumidor
  rechaza payloads malformados, modelo/dimensión incompatibles y devuelve 503.
- La fixture `QDRANT_TEST_URL` conserva colecciones/alias preexistentes y omite
  pruebas si `ocd_actual` ya existe. Dos regresiones comprueban ambas protecciones.
- Los mensajes de una sesión se serializan en el backend único. La combinación
  filtra IDs procesados y protege correcciones nuevas ante lotes solapados, sin
  duplicar revisiones. Las llamadas externas permanecen fuera de transacciones SQLite.
- El usuario puede retirar una categoría con evidencia literal; se retiran sus
  hechos del borrador activo y sus reglas dejan de aplicarse. El histórico se conserva.
- Zonas IANA con rutas absolutas o `..` generan un error documental V-02, sin 500.
- La última revisión validada se conserva por número ante fallos posteriores. Se
  eliminó la llamada OpenAI final que solo confirmaba una revisión Python ya terminada.
- Compose no entrega credenciales Atlassian al backend. `/api/integrations` informa
  presencia de configuración local y explica que no inspecciona el estado de ingesta.
- Se corrigió la prueba temporal del cron a siete campos. Con seis campos, los
  éxitos anteriores podían coincidir con el cambio de minuto; no probaban segundos.
  El log se escribe en archivo temporal y se espera también cierre del diario.
  El horario de producción de cinco campos sigue intacto. Véase el
  [ejemplo oficial de Supercronic 0.2.41](https://github.com/aptible/supercronic/blob/v0.2.41/README.md#crontab-format).

## Resultado de las verificaciones

Resultados ejecutados en este checkout:

- `Test-Aceptacion.ps1`: aprobado, proyecto `ocd-t4-5c04af61fa464ad5af269749df812ef4`,
  puerto local temporal 64134. Los cuatro marcadores E2E, salud desde host,
  59 pruebas backend y Ruff aprobados. Proyecto y sus cuatro volúmenes eliminados.
- `Test-Ingesta.ps1`: 34 pruebas y Ruff aprobados, proyecto
  `ocd-t2-b1b6027a7e7c45948dec518824ae4959`, Qdrant real; proyecto y volumen eliminados.
  Incluye el cron temporal real, bloqueo entre procesos, alias incierto confirmado,
  fallo de recuperación, carga parcial y protección de recursos preexistentes.
- `npm run typecheck` y `npm run build`: ejecutados nuevamente dentro de la etapa
  Docker frontend del checkout actual, con Node.js 24. Exportación estática aprobada.
- Compose normal y override de aceptación: `config --quiet` aprobado.
- Parser PowerShell del script de aceptación: sin errores. Ruff adicional sobre
  servidores/sonda E2E y renderer: aprobado. Enlaces locales Markdown sin faltantes.
- Diff sin cambios frontend; histórico `docs/verificacion_t1.md` conservado.
  No se ejecutó la aplicación principal ni se modificaron sus volúmenes.

El Dockerfile normal utiliza la caché de capas correspondiente a las fuentes
frontend sin cambios. No se copió una exportación del checkout principal. Para
repetir explícitamente TypeScript y Next.js sobre la etapa actual:

```powershell
docker build --target frontend -t ocd-t4-frontend .
docker run --rm ocd-t4-frontend sh -c 'npm run typecheck && npm run build'
```

Las tres vistas del drawio se actualizaron y la vista PNG se inspeccionó visualmente:
textos legibles, flechas y nodos sin recortes. Para regenerarla en Windows:

```powershell
uv run --no-project --with pillow python scripts/render_architecture.py
```

## Alcance de la prueba automatizada con dobles

Qdrant, SQLite, Docker, Supercronic, SDK OpenAI, HTTPX y HTTP de la aplicación son
reales en estas pruebas. Atlassian/OpenAI son servidores dobles y las credenciales
son ficticias. Los snapshots proceden de lecturas documentales anteriores; su
procedencia se conserva en `ingesta/tests/fixtures/README.md`.

No se verificó acceso REST autenticado a servicios reales, generación pagada de
embeddings, calidad semántica real, disparo a las 03:00 en un día real, interfaz
visual de chat, creación Jira, ejecución de procedimientos, permisos reales ni
Railway. El cron observado es temporal y la revisión es documental.

## Verificación final en la rama de integración

Se repitió el recorrido completo en un proyecto Compose aislado después de cubrir
la pérdida de conexión durante la publicación y verificar el esquema JSON enviado
por el SDK de OpenAI. Pasaron 59 pruebas del backend, 36 de ingesta y Ruff en ambos.

Antes del cambio de esquema se creó una copia consistente mediante la API de respaldo
de SQLite en `/data/backups/pre-ocd-20261113T154826Z.sqlite3`. Su restauración en
memoria pasó `PRAGMA integrity_check` y conservó los registros de las tablas anteriores.
Después de ejecutar `docker compose up --build -d --wait` en el proyecto principal,
se comprobaron nuevamente la integridad del volumen y los saludos previos.
La API local y Qdrant respondieron a sus comprobaciones de disponibilidad.
Antes de la primera carga, la consulta documental del proyecto principal devolvió HTTP 503.

## Ingesta real y verificación de citas

El 13 de noviembre de 2026 se ejecutó `docker compose exec -T ingesta ocd-ingestar`
en el proyecto Compose principal con el código de `a19ceed`. La CLI leyó cinco páginas
de Confluence y veinte tickets de Jira por REST, y obtuvo los embeddings de OpenAI.
Terminó con código de salida `0` y registró:

```text
INFO Carga publicada run=16c4db78e62040a59ad06825ea8e7db1 puntos=83
```

Al terminar la carga, el alias `ocd_actual` apuntaba a `ocd_16c4db78e62040a59ad06825ea8e7db1`.
La colección contenía 26 reglas, 32 campos, 20 ejemplos y 5 fragmentos de contexto.

**Consulta al agente.** Se envió a `POST /api/chat` una solicitud para publicar
`pedidos-demo` de la versión 1.0 a la 2.0 en producción. Con OpenAI Responses API,
el backend devolvió HTTP `200`, revisión `1` y estado `reviewed`. El borrador pidió,
entre otros datos, el repositorio. De las 19 validaciones aplicables, 13 devolvieron
`FALTA_INFORMACION`, 4 devolvieron `CUMPLE` y 2 devolvieron `NO_VERIFICABLE`.

**Comprobación de procedencia.** La respuesta identificó la misma colección física que el alias.
Se leyó cada punto por su `point_id` en esa colección y se comparó el extracto con `payload.text`.
También se compararon el ID de la fuente, la clave del registro, el código documental o de ticket, la URL y la versión.
Coincidieron **24 de 24 citas** de `sources` y **19 de 19 referencias** de `validations`.
Las citas correspondieron a siete fuentes: el índice común, el modelo de microservicios y los cinco ejemplos de `SCRUM-5` a `SCRUM-9`.

| Regla | Fuente y versión en Confluence | `point_id` en Qdrant | Resultado |
| --- | --- | --- | --- |
| `OCD-C01` | [MO-OCD-000, v1](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/66048/DEMO+OCD+-+ndice+y+reglas+comunes) | `aaf42080-a1b4-54a2-847c-93a5f7774605` | `FALTA_INFORMACION` |
| `MIC-R01` | [MO-MIC-001, v1](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/294922/MO-MIC-001+-+Pase+a+producci+n+de+microservicios+DEMO) | `df10f269-b18b-5bf5-b85d-3a650ee4fa14` | `FALTA_INFORMACION` |

La coincidencia acredita la procedencia de las citas en este caso. Siguen pendientes la
evaluación de relevancia con varias consultas y la observación del cron real a las 03:00 de Lima.
