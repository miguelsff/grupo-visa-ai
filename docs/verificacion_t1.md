# Evidencia de T1

Fecha: 13 de noviembre de 2026. Base: `cb9d9fcb21ab89f8512ce2b4929195eb6ce15f5c`.
Worktree independiente: `C:/Users/mact1/.codex/worktrees/cee3/grupo-visa-ai`.
Se comprobó estado limpio antes de crear `feature/t1-contrato-ocd` desde esa base.
La identidad Git configurada se conservó. No se publicaron cambios.

| Verificación | Resultado |
| --- | --- |
| `docker compose config --format json` | Correcto; sin puertos publicados por Qdrant y con alias/modelo/dimensión esperados. |
| `powershell -NoProfile -File scripts/Test-QdrantPersistence.ps1` | Correcto; dos mensajes PASS antes y después de recrear Qdrant. |
| Qdrant real | Imagen `qdrant/qdrant:v1.16.3`, fijada también por digest `sha256:0425e3e03e7fd9b3dc95c4214546afe19de2eb2e28ca621441a56663ac6e1f46`. |
| Aislamiento de persistencia | Proyecto `ocd-t1-1864ed5856bb`; volumen propio creado y eliminado al finalizar. No se modificó la aplicación existente. |
| Contenido recuperado tras recreación | Alias `ocd_actual`, UUIDv5, payload completo y consulta vectorial 1536/Cosine. Vector sintético sin llamada OpenAI. |
| Regresión backend | 3 pruebas aprobadas en Python 3.14 con la imagen de pruebas existente y `backend/app`, `backend/tests`, `backend/pyproject.toml` y documentos actuales montados en modo lectura. |
| Estilo | Ruff correcto sobre `app`, `tests` y `scripts` en esa imagen; también `uvx --from ruff==0.17.5 ruff check --no-cache scripts`. |
| Contrato | JSON Schema Draft 2020-12 válido; payload de la sonda aceptado; variantes con normativa, campo o dimensión incompatibles rechazadas. |
| Documentación | Enlaces locales comprobados; tres vistas XML con IDs y referencias válidos; vistas renderizadas y revisadas visualmente. PNG actualizado con servicios locales. |
| Dependencias | Bloqueos regenerados con `uv`; versiones backend sin cambios; versiones comunes de ingesta iguales a las del backend; ambos proyectos limitados a Python 3.14. |

La recompilación completa con
`docker compose -p ocd-t1-regression --profile test run --build --rm tests`
se detuvo después de más de cinco minutos sin avance en `npm ci`.
No se afirma una compilación nueva de frontend ni de la imagen completa en T1.
Las pruebas del backend se ejecutaron usando la imagen existente con los archivos
actuales montados; no sustituyen esa compilación. La red temporal de esa ejecución
también se eliminó. No se cambiaron archivos del frontend ni el Dockerfile.

Pendientes por alcance: lectura remota, embeddings reales, CLI, Supercronic,
agente y V-01/02/03. Corresponden a T2/T3. Railway y creación Jira quedan fuera.
