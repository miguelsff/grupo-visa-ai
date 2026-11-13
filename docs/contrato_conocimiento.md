# Contrato de conocimiento OCD, versión 1

Decisión confirmada para T1–T3, 13 de noviembre de 2026. T1 prepara infraestructura,
configuración y contrato; no implementa ingesta ni validaciones del agente.

## Configuración compartida

La extensión `x-knowledge-environment` de `compose.yaml` es el punto común que T2
debe reutilizar en su servicio de ingesta y T3 debe consumir desde el backend.
No importar módulos de un proyecto Python desde el otro.

| Variable | Valor local | Regla |
| --- | --- | --- |
| `QDRANT_URL` | `http://qdrant:6333` | REST interno, sin puertos publicados. |
| `QDRANT_ALIAS` | `ocd_actual` | Cada consulta resuelve el alias una sola vez y lee esa colección física hasta terminar. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Mismo modelo en carga y consulta. |
| `OPENAI_EMBEDDING_DIMENSIONS` | `1536` | Vector denso sin nombre, distancia `Cosine`. |

El modelo de conversación sigue siendo `OPENAI_MODEL=gpt-6-luna`, separado del
modelo de embeddings. Cambiar modelo o dimensión exige reindexación completa y
compatibilidad de lectores antes de activar el alias. T2/T3 deben rechazar una
configuración incompatible; no mezclar vectores de modelos diferentes.

## Unidad de publicación e identidad

Cada carga construye una colección nueva `ocd_<run_id>`; `run_id` es un UUID sin
guiones. No escribir directamente en la colección que resuelve el alias vigente.
Un punto representa una regla completa, un campo condicional completo, un
fragmento de contexto o un fragmento de un ticket. No partir una regla ni separar
su condición del resultado. Texto UTF-8, saltos LF, normalización Unicode NFC.

`source_id` es `confluence:<cloudId>:<pageId>` o `jira:<cloudId>:<issueId>`.
`issueId` es el ID numérico estable obtenido por T2; la clave SCRUM se conserva
como `source.code`, pero no reemplaza ese ID. Los IDs remotos faltantes impiden
publicar una carga; no inventarlos ni copiarlos de otro ticket.

El ID Qdrant es UUIDv5 con namespace `uuid.NAMESPACE_URL` y nombre exacto
`ocd:v1|<source_id>|<record_key>`. No incluir versión, fecha de carga ni `run_id`.
Así permanece estable al actualizar la fuente y entre colecciones:

| `kind` | `record_key` | Contenido |
| --- | --- | --- |
| `rule` | `rule:<id>` | Una de las seis `OCD-Cxx` o veinte reglas específicas. |
| `field` | `field:<name>` | `name` exacto del manifiesto normalizado NFC; sin traducir ni separar `/`. |
| `context` | `context:<ordinal>` | Fragmentos de página que no duplican reglas/campos; ordinal desde 0. |
| `example` | `example:<ordinal>` | Texto del ticket autorizado; ordinal desde 0. |

Los ordinales dependen de un particionado determinista documentado por T2. Al
cambiar ese particionado puede cambiar la identidad de esos fragmentos; nunca
la de reglas ni campos. La colección nueva evita dejar puntos retirados.
`content_sha256` es SHA-256 hexadecimal del texto normalizado de `text`.

## Payload obligatorio

Todos los puntos tienen estos campos; los opcionales se indican expresamente.
No guardar credenciales ni instrucciones ejecutables.
El [JSON Schema](ocd_payload.schema.json) permite verificar estructura y distinguir
reglas, campos y ejemplos. La validación de IDs, hash, integridad de la carga y
correspondencia con la fuente requiere además las comprobaciones de T2.

| Campo | Tipo / asignación |
| --- | --- |
| `schema_version` | Entero `1`. |
| `source_id`, `record_key` | Cadenas con las reglas anteriores. |
| `kind` | `rule`, `field`, `context` o `example`. |
| `scope` | `comun`, `microservicio`, `azure`, `red` o `identidad`. |
| `normative` | Booleano: verdadero solo para `rule` y `field` de Confluence. |
| `text` | Texto íntegro de la unidad, incluido contexto condicional. Texto que se vectoriza. |
| `content_sha256` | Hash del texto. |
| `ingestion_run_id`, `loaded_at` | UUID sin guiones y fecha ISO 8601 UTC con `Z`. |
| `embedding_model`, `embedding_dimensions` | Valores de configuración compartida. |
| `source` | Objeto con `system`, `id`, `code`, `title`, `url`, `version`, `document_version`, `updated_at`, `local_file`, `locator`. |
| `applies_when` | Condición documental literal, nunca código; debe acompañar a reglas/campos. Para contexto/ejemplo, `null`. |
| `rule` | Objeto de regla para `kind=rule`; en otro caso `null`. |
| `field` | Objeto de campo para `kind=field`; en otro caso `null`. |

`source.system`: `confluence` o `jira`. `source.id`: ID remoto estable.
`source.code`: código MO o clave Jira; `title` y `url`: valores de su fuente.
`source.version`: versión Confluence convertida a cadena o `fields.updated` Jira.
`document_version`: versión documental del manifiesto en Confluence; `null` en Jira.
`updated_at`: fecha remota si se obtuvo; `null` en copias locales que no la contienen.
`local_file`: ruta relativa al repositorio (`docs/modelos_operativos/` + `localFile`) para copias locales; `null` en lectura remota.
`locator`: localizador estable de regla, campo o fragmento dentro de la fuente.
No sustituir una fecha desconocida por `loaded_at`. `source.version` es obligatoria.

El objeto `rule` conserva `id`, `class`, `fields` (cadena o `null` para comunes),
`requirement`, `result`, `mode` (cadena o `null` si no está documentado).
El objeto `field` conserva `name`, `type`, `when` y `example` literalmente del manifiesto.
`applies_when` para comunes es `Siempre`; para específicas es
`Sección <category> activada` más la condición literal de la regla si existe.
Para campos específicos es `Sección <category> activada; <when>`.
T3 interpreta estas condiciones mediante reglas Python revisadas; nunca `eval`
ni ejecución de expresiones recuperadas. Si no puede determinar aplicabilidad,
pregunta al usuario y deja `FALTA_INFORMACION` o `NO_VERIFICABLE` según la causa.

## Asignación de fuentes

Fuente de autorización: `docs/modelos_operativos/manifest.json`. No seguir enlaces
adicionales encontrados en páginas o tickets. Las copias locales permiten preparar
reglas; no acreditan la lectura remota. T2 comprobará versiones al leer Confluence.

| Entrada del manifiesto | Destino del payload |
| --- | --- |
| `index` / `models[]` | `source` con `code`, `pageId`, `title`, `url`, `confluenceVersion`, `documentVersion`, `localFile`. |
| `index.commonRules[]` | `kind=rule`, `scope=comun`, `normative=true`; `id`, `ruleClass→class`, `condition→requirement`, `result`. |
| `models[].rules[]` | `kind=rule`, `scope=category`, `normative=true`; `id`, `ruleClass→class`, `fields`, `result`, `mode`; `requirement=fields`. |
| `models[].requiredFields[]` | `kind=field`, `scope=category`, `normative=true`; conservar `name`, `type`, `when`, `example`. |
| `models[].examples[]` | Autoriza `key`/`url` y categoría; leer el ticket para obtener ID, título, actualización y texto. `kind=example`, `normative=false`. |
| Texto adicional de página | `kind=context`, `normative=false`; no introducir nuevas reglas automáticamente. |

Los campos comunes y sus condiciones están en las seis reglas del índice. No
buscar únicamente similitud vectorial para descubrirlos: T3 recuperará todas las
reglas comunes y todos los campos/reglas de las secciones activadas mediante
filtros y paginación, y usará búsqueda semántica para contexto y ejemplos.
La ingesta debe conservar las 26 reglas únicas y los campos con su `when`;
los veinte tickets son ejemplos sintéticos, nunca requisitos ni datos del usuario.

Ejemplo de asignación condicional: `MO-ID-001.requiredFields` contiene
`client_id / object_id` con `when=Si existe la identidad`. No exigir esos IDs
para una identidad nueva. `MO-RED-001` condiciona `nombre_dns` a la resolución de
nombres. `identificador_inmutable` de microservicio se exige antes de ejecutar,
sin confundir esa etapa con preparar el borrador. Mantener estas condiciones.

Cada resultado V-01, V-02 o V-03 de T3 conservará ID del punto, ID de regla o campo,
`source_id`, código, URL, versión y fragmento utilizado. El borrador fija también
la colección física de esa revisión para poder identificar la generación consultada.

## Publicación y recuperación (T2/T3 pendientes)

1. Adquirir bloqueo de ingesta compartido por CLI y cron. Leer solo la lista permitida. Contrastar las reglas y los campos con el HTML recibido. Si una regla, condición o versión documental difiere de la admitida por los validadores, conservar la colección vigente y registrar la fuente que requiere revisión.
2. Construir colección aislada con vectores 1536/Cosine y payload versión 1.
3. Verificar 5 páginas, 26 reglas, todos los campos y 20 ejemplos distintos;
   comprobar IDs únicos, versiones, condiciones, dimensiones y ausencia de secretos.
4. Crear índices keyword para `kind`, `scope`, `source_id`, `rule.id` e índice booleano
   para `normative`; paginar las recuperaciones completas.
5. Cambiar `ocd_actual` mediante una sola operación atómica de alias Qdrant:
   borrar alias anterior (si existe) y crear alias hacia la colección nueva.
6. Conservar la colección activa y su predecesora. Limpiar solo las generaciones propias que ya no estén publicadas. Las revisiones conservan en SQLite el extracto citado y su procedencia para que las citas sobrevivan a la limpieza. Si el cambio de alias devuelve un resultado incierto, comprobar su destino antes de borrar una colección.

Un fallo de descarga, contenido, embedding o escritura no cambia el alias.
Sin primera carga válida, T3 informa conocimiento no disponible; no afirma que
el agente funciona ni vuelve silenciosamente a FTS5. El backend no escribe conocimiento.
Qdrant usa volumen propio `qdrant_data`; SQLite conserva sesiones, mensajes,
borradores y revisiones. No duplicar documentos nuevos en SQLite.

## Referencias verificadas para el contrato

- [Colecciones y alias Qdrant](https://qdrant.tech/documentation/manage-data/collections/): publicación de colecciones mediante alias.
- [Operación de alias](https://api.qdrant.tech/master/api-reference/aliases/update-aliases): cambio de alias en una solicitud.
- [Embeddings OpenAI](https://developers.openai.com/api/docs/guides/embeddings): `text-embedding-3-small` produce 1536 dimensiones por defecto.
- [Versión Qdrant seleccionada](https://github.com/qdrant/qdrant/releases/tag/v1.16.3).
