# Backend OCD local: T3

Implementación sobre T1 `05d094c`. El backend prepara un borrador y ejecuta
comprobaciones documentales. No crea tickets ni llama a Atlassian o Azure.
El saludo existente conserva su contrato y sus registros.

## API

| Método y ruta | Contrato |
| --- | --- |
| `POST /api/chat` | Cuerpo `{"message":"Describe aquí el cambio"}`. Devuelve borrador, revisión, preguntas, resultados y fuentes. |
| `GET /api/chat` | Recupera la última revisión de la sesión. No ejecuta llamadas externas. |
| `GET /api/chat/revisions/{revision}` | Recupera una revisión de la sesión con sus extractos originales. Devuelve 404 si no pertenece a esa sesión. |
| `GET /api/knowledge?q=texto` | Conserva la lista de `code`, `title`, `url`, `version`, `excerpt`. Consulta Qdrant y embeddings. |
| `GET /api/health` | Estado local mínimo: `status`, `backend`, `sqlite`, `frontend`. No consulta servicios externos ni devuelve recuentos. |

La cookie `ocd_session` es opaca, aleatoria y `HttpOnly`, con `SameSite=strict`
y ruta `/api/chat`. Usa `Secure` al recibir HTTPS. SQLite almacena su hash,
no el token. El cliente no puede seleccionar sesión o borrador en el cuerpo.
Debe conservar la cookie entre mensajes y al recuperar revisiones.

`ChatResponse.status` distingue `pending`, `reviewed` y `unavailable`.
`reviewed` significa que terminó la revisión documental. Cada resultado conserva
su propio estado: `CUMPLE`, `FALTA_INFORMACION`, `ERROR` o `NO_VERIFICABLE`.
Una revisión completada puede contener faltantes, contradicciones y preguntas.
Las preguntas figuran en `questions`; `draft.facts` conserva el valor, la cita literal
y el mensaje del solicitante que sustenta cada hecho.

Cuando falla una dependencia, `POST /api/chat` devuelve 503 con el borrador guardado.
Los mensajes que no pudieron interpretarse permanecen pendientes para el siguiente
turno. `GET /api/chat` permite recuperarlo incluso después del fallo.
`GET /api/knowledge` devuelve 503 si falta el alias, falla el servicio o el contrato
es incompatible. No existe recuperación silenciosa desde FTS5.

## Flujo y responsabilidades

1. Guardar el mensaje, después de aplicar una detección limitada de secretos.
2. Extraer hechos mediante el SDK oficial y Responses API, con `store=False`.
3. Admitir únicamente valores con cita literal de un mensaje del solicitante.
4. Combinar el parche con el último borrador dentro de una transacción corta.
5. Ejecutar `buscar_conocimiento` en el backend. Resolver el alias una sola vez.
6. Paginar todas las reglas comunes y los campos/reglas de cada sección activa.
7. Recuperar contexto y ejemplos mediante vector, siempre en la misma colección física.
8. Ejecutar `validar_ocd` en Python y guardar los resultados y extractos en la revisión.

Cada revisión tiene su propia instantánea. La última revisión se identifica mediante
un contador por sesión. Una respuesta tardía completa exclusivamente su revisión.
La combinación de hechos utiliza el orden de los mensajes: una extracción antigua
no puede reemplazar una corrección más reciente del mismo campo.
Las llamadas externas no mantienen transacciones de escritura abiertas.

La adaptación de `agent-scratch` conserva la separación entre caso de uso,
modelo, recuperación y persistencia, así como la construcción de citas desde
resultados reales. T3 sustituye el almacén en memoria de esa referencia por SQLite,
usa Responses y añade recuperación normativa exhaustiva y validación Python.

## Conocimiento y límites

`QDRANT_URL`, `QDRANT_ALIAS`, `OPENAI_EMBEDDING_MODEL` y
`OPENAI_EMBEDDING_DIMENSIONS` consumen la configuración compartida de T1.
Se admiten `text-embedding-3-small`, 1536 dimensiones y Cosine.
`OPENAI_MODEL` conserva el valor predeterminado `gpt-6-luna`.
`EXTERNAL_TIMEOUT_SECONDS` permite ajustar el tiempo máximo por llamada (30 s por defecto).
OpenAI tiene un reintento adicional. Qdrant limita los fallos de transporte a dos intentos.

La fuente documental única es Qdrant. `agent/catalog.py` contiene nombres,
condiciones y firmas del contrato revisado 1.0; no contiene documentos ni sustituye
su recuperación. Una generación incompleta, desconocida o incompatible impide
completar la revisión. Las fuentes no cambian permisos ni herramientas.
Los ejemplos nunca completan hechos del solicitante.

V-01 conserva las condiciones del corpus: IDs de identidad existente, DNS,
cambios de contrato/datos, credenciales y requisitos previos a la ejecución.
Si la condición no puede decidirse, el backend pregunta.
V-02 contrasta fechas, ambientes, versiones/tags, réplicas, booleanos,
IP/CIDR, puertos y presencia del alcance de autorización.
V-03 exige planes y criterios, conserva referencias y mantiene pendientes las
comprobaciones técnicas. Una afirmación o URL escrita por el usuario no verifica
una ejecución, conectividad, existencia ni permisos efectivos.
La coherencia funcional de configuraciones arbitrarias requiere revisión técnica.

La detección de secretos es limitada. Los valores detectados se omiten antes de
persistir o enviar contenido al modelo. La ausencia de detecciones no garantiza
ausencia de secretos. Los identificadores públicos no se tratan como credenciales.

El arranque solo inicializa SQLite y no carga documentos. Conserva las tablas
legadas existentes, sin leerlas ni alterarlas. El Dockerfile deja de copiar el corpus.
No modifica las dependencias ni sus bloqueos.

## Verificación e integración

Las pruebas usan bases temporales y dobles de OpenAI/Qdrant, sin llamadas remotas.
Incluyen las 26 reglas, condiciones, caso válido, faltantes, contradicciones,
aislamiento, recuperación, concurrencia, filtros/paginación, rotación del alias
y transporte simulado del SDK oficial.

Desde la raíz:

```powershell
docker compose -p ocd-t3-test --profile test run --build --rm tests
docker compose -p ocd-t3-test --profile test run --rm tests ruff check --no-cache app tests
```

Las pruebas de persistencia de contenedores deben usar un volumen temporal propio.
La copia/restauración del volumen principal fue comprobada antes de T3, según la
instrucción recibida. T3 no ejecuta una migración sobre ese volumen durante sus pruebas.

La [prueba posterior con OpenAI y Qdrant](../docs/verificacion_t4.md#ingesta-real-y-verificación-de-citas) verificó las citas y las referencias de validación del chat HTTP.
Esta tarea no cambia frontend, Compose ni la documentación general.
La integración debe actualizar las vistas de arquitectura y el estado documentado.
El frontend debe consumir el chat y adaptar los tipos/indicadores de salud al contrato
mínimo; los campos FTS5 y los recuentos se retiraron deliberadamente de la API.

Verificaciones ejecutadas el 13 de noviembre de 2026:

- 47 pruebas aprobadas en Docker, con Python 3.14 y los bloqueos existentes.
- Imagen `runtime` construida. La compilación incluye la exportación estática y TypeScript.
- Contenedor ejecutado como UID 10001, sin `/app/knowledge`.
- Saludo, sesión, revisión fallida y mensaje recuperados al recrear dos contenedores
  sobre un volumen temporal propio. El volumen temporal se eliminó al terminar.
- T3 ejercitó la API mediante dobles. La interfaz de chat quedó fuera de estas pruebas.
