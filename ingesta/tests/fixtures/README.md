# Procedencia de los fixtures

Capturados el 13 de noviembre de 2026 mediante lecturas del conector Atlassian
en el sitio y cloudId del manifiesto. Solo se leyeron sus cinco páginas y veinte
tickets autorizados. No son copias convertidas desde los Markdown del repositorio.

`pages/*.json` conserva el HTML completo obtenido con `content_format=html`,
`detail=full`, revisión 1, título, ID, espacio, estado y fecha remota. Se retiraron
únicamente atributos `data-local-id` y datos de autor. El sobre se adapta al REST
v2 que consume la ingesta (`body.view.value`, `version.createdAt`). Se mantienen
tablas, paneles, enlaces y etiquetas `time datetime`.

`tickets/*.json` conserva ID numérico, clave, título, actualización y descripción
HTML reales. El sobre del conector se adapta a REST Jira
`fields.summary`, `fields.updated` y `renderedFields.description`. No se conservan
metadatos de cuenta ni de la invocación MCP.

La adaptación del sobre no acredita que se haya ejecutado la CLI con credenciales
REST. Los tests comprueban solicitudes HTTPX mediante MockTransport. Las respuestas
de embeddings son sintéticas y se sirven por HTTP local al SDK oficial.

Estos archivos solo son datos de prueba. La imagen de producción no los contiene
y no existe opción de CLI para ingerirlos. Las páginas conservan texto del alcance
anterior que menciona creación Jira: sigue siendo contexto no normativo y no
modifica el alcance local T1–T3.
