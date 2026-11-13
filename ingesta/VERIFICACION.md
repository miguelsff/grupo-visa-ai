# Verificación T2

Fecha: 13 de noviembre de 2026. Base: `05d094c`. Rama: `feature/t2-ingesta-ocd`.

Nota T4: la prueba original del cron usaba seis campos, que cronexpr interpreta
como minutos hasta año, no como segundos. Por tanto, el éxito anterior no prueba
la frecuencia declarada de segundos. T4 corrige exclusivamente el horario temporal
de prueba a siete campos (`*/2 * * * * * *`), captura el log sin bloquear el proceso
y espera publicación y diario completos. El horario productivo de cinco campos
`0 3 * * *` se conserva. La nueva evidencia está en `docs/verificacion_t4.md`.

## Evidencia ejecutada

- Lectura real de las cinco páginas en HTML y los veinte tickets autorizados,
  mediante el conector Atlassian. Capturas y adaptación del sobre documentadas
  en [fixtures](tests/fixtures/README.md).
- `powershell -NoProfile -File ingesta/Test-Ingesta.ps1`: 31 pruebas aprobadas
  con Python 3.14 y Qdrant 1.16.3 real, más Ruff aprobado. Proyecto temporal
  `ocd-t2-37cc4d9754554c13a81ff3e5d25f791a`, eliminado junto con su volumen al terminar.
- Contrato JSON Schema validado sobre todos los payloads de la carga completa.
  IDs estables entre ejecuciones; 26 reglas, condiciones de campos y veinte
  identidades Jira distintas conservadas. Texto de paneles, tablas y fechas comprobado.
- Fuentes remotas alteradas, versiones distintas y condiciones cambiadas rechazadas.
  Sin lectura local de respaldo ni seguimiento de enlaces encontrados en el contenido.
- SDK oficial OpenAI probado por lotes contra un servidor sintético HTTP local.
  Fallo OpenAI conservó el alias publicado.
- CLI ejecutada como proceso real. Bloqueo comprobado entre procesos independientes.
- Supercronic ejecutó la misma CLI con horario temporal de segundos y zona Lima.
  El archivo de producción se comprobó sin modificar: `0 3 * * *`.
- Repetición con Qdrant real conservó activa y predecesora. Escritura parcial y
  verificación incompleta no publicaron. Se probaron respuestas de alias perdidas
  con y sin cambio aplicado, indisponibilidad al reconciliar y recuperación posterior.
  Colecciones ajenas o referenciadas por otros alias quedaron protegidas.
- Imagen `runtime` construida; CLI instalada mediante `project.scripts`.
  UID 10001, escritura en `/state`, ausencia de fixtures y crontab válido comprobados.
- `docker compose config --quiet` y configuración Compose de pruebas aprobados.
  Ninguna prueba publicó puertos ni utilizó los volúmenes de la aplicación normal.

## Límites

Durante T2, la CLI utilizó dobles para Atlassian y OpenAI. La
[verificación posterior con servicios reales](../docs/verificacion_t4.md#ingesta-real-y-verificación-de-citas)
registró la colección publicada y las citas verificadas.
Las capturas reales de Atlassian acreditan el contraste documental; la adaptación
de su sobre no acredita una conexión HTTPX autenticada en producción. Los tests
de OpenAI acreditan el uso del SDK y del contrato, no la calidad semántica real.

La imagen construida se verificó en Linux amd64; el binario arm64 está configurado
con checksum oficial, pero no se ejecutó en esa arquitectura. Cron a las 03:00 Lima
queda configurado y validado; se observó el disparo del horario temporal de pruebas.
La detección de secretos es limitada. Un fallo al consultar el destino del alias
pospone la limpieza hasta recuperar Qdrant; prioriza conservar cargas válidas.

No se modificaron backend, frontend, esquema SQLite ni documentación general.
T3 conectará el consumidor y T4 actualizará el estado documental de la aplicación.
