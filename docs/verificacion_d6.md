# Verificación local de la demostración OCD

Fecha: 13 de noviembre de 2026. Base integrada: `d1e2aaa4ea292cab841e2a46ada5a79237af52a9`.

En `ocd-demo-preview`, puerto 3001, se reconstruyó solo `app` y se conservó el
corpus existente. En el navegador, con la configuración real, «Quiero un pase a
producción» produjo una pregunta por el microservicio y la versión. La respuesta
«Pedidos, versión 1.9.0. Corrige la duplicación de pedidos.» produjo la vista previa
de la Tarea SCRUM, con esos datos y cinco pendientes: ventana, responsable,
repositorio, pruebas y reversión. El detalle mostró 24 fuentes y 19 validaciones.
Se revisaron escritorio, móvil, barra izquierda y cierre del detalle con Escape y
retorno del foco. No se accionó la publicación real. No se cronometró este recorrido.

La aceptación aislada usa Qdrant, SQLite, MongoDB y aplicación reales en contenedores,
con Atlassian y OpenAI simulados. El doble Jira captura el POST: se comparan título
y descripción ADF con la vista previa, destino, clave y enlace simulados; se comprueba
que la repetición y la recuperación tras recrear `app` no crean otro ticket. Esto no
acredita credenciales, permisos ni escritura en Jira real. La evidencia anterior de
lectura real y citas permanece en [T4](verificacion_t4.md#ingesta-real-y-verificación-de-citas).
El enlace simulado se comprobó en la respuesta; no se abrió en un navegador.

La ejecución aislada pasó 106 pruebas de backend y Ruff; la prueba de ingesta pasó
36 pruebas y Ruff. TypeScript y la compilación estática pasaron en Docker. Las 13
pruebas de Gitflow pasaron en Node local.
