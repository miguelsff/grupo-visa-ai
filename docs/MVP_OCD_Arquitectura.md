# MVP OCD — arquitectura básica

Fecha: 12 de noviembre de 2026. Versión: 0.1. Estado: propuesta para revisión.

## 1. Alcance y requisitos

El MVP prepara un ticket OCD para certificación, previo al pase a producción.
El usuario describe el cambio mediante un chat. El agente consulta conocimiento, identifica faltantes y crea el ticket en Jira.

| ID | Requisito o decisión | Estado | Fuente |
|---|---|---|---|
| RF-01 | Conversar para generar tickets OCD. | Confirmado | Usuario |
| RF-02 | Crear el ticket en Jira Cloud Free. | Confirmado | Usuario |
| RF-03 | Consultar tickets anteriores y modelos operativos. | Confirmado | Usuario |
| RF-04 | Cubrir microservicios, configuración Azure, red e identidades Microsoft Entra ID. | Confirmado | Usuario |
| RES-01 | Desarrollar durante cinco horas y reservar una hora para presentar. | Confirmado | Usuario |
| DEC-01 | Usar Confluence Free para los modelos operativos. Confluence está activo y las páginas están publicadas; falta verificar el plan de la cuenta. | Seleccionado por condición del usuario | Usuario; S1–S2 |
| DEC-02 | Usar un OCD con cuatro secciones activables según el cambio. | Propuesto | Reducción del alcance |
| DEC-03 | Ejecutar la aplicación localmente, con una cuenta de demostración. | Propuesto | Plazo disponible |
| SUP-01 | Estimar el desarrollo para una persona, con acceso a las API y datos de demostración disponibles. | Supuesto | Validar antes de implementar |

La demostración principal combina los cuatro casos en el pase de un microservicio.
Los casos también pueden activar una sola sección. El agente solicita únicamente los datos aplicables.
La creación del OCD registra la solicitud. La certificación y el pase siguen sus procesos existentes.

### Campos propuestos

| Sección | Campos |
|---|---|
| Común | Título, objetivo, solicitante, responsable, etapa solicitada, ambientes, ventana con zona horaria, impacto y dependencias. |
| Microservicio | Nombre, repositorio, versión actual, versión objetivo, artefacto, pasos de despliegue y pruebas disponibles. |
| Azure | Servicio, suscripción, grupo de recursos, región, recurso y configuración actual/propuesta. |
| Red | Origen, destino, protocolo, puerto o rango, sentido, finalidad y ambiente de cada extremo. |
| Identidad | Nombre solicitado, tenant, aplicación consumidora, recurso/API destino, mecanismo de autenticación y permisos requeridos. |
| Autorización | Rol y alcance Azure RBAC, o permisos de aplicación/app roles para la API destino, según corresponda. |
| Recuperación | Pasos de reversión, versión/configuración anterior y criterio para revertir. |
| Evidencias | Enlaces a pruebas, tickets relacionados y páginas/versiones de los modelos operativos consultados. |

Los identificadores de identidades existentes son opcionales según el caso. Una identidad nueva se describe por su nombre y finalidad.
Los campos describen mecanismos de autenticación; nunca contienen contraseñas, certificados privados ni valores de tokens.
Microsoft distingue la identidad de aplicación y los roles que habilitan su acceso [S7].

### Tres verificaciones implementables

| ID | Verificación | Implementación | Resultado observable |
|---|---|---|---|
| V-01 | Completitud condicional. | Validar campos comunes y campos de las secciones activadas. | Lista exacta de faltantes y pregunta correspondiente. |
| V-02 | Consistencia técnica. | Validar versiones, fechas, puertos y correspondencia de ambientes. Verificar destino, permiso y alcance de la identidad. | Errores asociados a campos concretos. |
| V-03 | Trazabilidad del procedimiento. | Comprobar que existen despliegue, reversión y evidencias requeridas por el modelo operativo seleccionado. | Fuente, versión y fragmento que sustenta cada requisito. |

El backend ejecuta las reglas reproducibles. El modelo interpreta la solicitud y redacta el contenido.
Los ejemplos históricos orientan la redacción. Los modelos operativos seleccionados definen las reglas de la demostración.
El agente conserva los datos desconocidos como pendientes; nunca copia identificadores de otro ticket para completarlos.

Estados de cada verificación: `CUMPLE`, `FALTA_INFORMACION`, `ERROR` o `NO_VERIFICABLE`.
Una comprobación documental no demuestra conectividad, existencia de recursos ni permisos efectivos en Azure.
Las verificaciones reales de infraestructura quedan identificadas como `NO_VERIFICABLE` cuando requieren una conexión ausente.

## 2. Diseño de alto nivel

### Componentes y tecnología

| Componente | Responsabilidad | Tecnología propuesta |
|---|---|---|
| Frontend | Chat, borrador del OCD, verificaciones, fuentes y enlace del ticket creado. | HTML, CSS y JavaScript; una pantalla. |
| Backend | Servir el frontend, conservar la sesión y coordinar los módulos. | Python y FastAPI; un proceso local. |
| Agente | Interpretar el cambio, consultar conocimiento, solicitar datos y seleccionar herramientas. | OpenAI Responses API; `gpt-6-luna`. |
| Cargador | Leer tickets y páginas seleccionados antes de la demo. Conservar su origen y versión. | Módulo invocado mediante un comando manual. |
| Conector Atlassian | Leer Jira/Confluence y crear tickets. | API REST con token guardado en el backend. |
| Base de conocimiento | Guardar documentos, borradores y operaciones de creación. | SQLite; un archivo local. |

El agente, el cargador, las reglas y el conector son módulos del mismo backend.
El cargador mantiene una responsabilidad separada y comparte el conector con el agente.
FastAPI puede servir archivos estáticos [S8]. La separación de módulos evita desplegar servicios adicionales durante la demo.

Para estas cinco horas, se propone REST directo en lugar de la conexión MCP sugerida inicialmente.
La autenticación directa mediante token está documentada para scripts y clientes privados [S3–S4].
El compromiso es implementar tres herramientas específicas. MCP se reconsideraría si una integración ya estuviera configurada y probada.

Herramientas del agente:

1. `buscar_conocimiento`: recuperar reglas y ejemplos aplicables desde SQLite.
2. `validar_ocd`: ejecutar V-01, V-02 y V-03 sobre el borrador estructurado.
3. `crear_ticket`: verificar el borrador vigente y crear un único ticket en el proyecto permitido.

### Conocimiento de la demostración

- Una página índice en Confluence y cuatro páginas de modelos operativos: microservicios, Azure, red e identidad.
- Veinte tickets sintéticos de ejemplo: cinco por cada caso, según la ampliación solicitada por el usuario.
- El ejemplo OCD aportado por el usuario sirve únicamente como referencia visual; su contenido queda excluido de los tickets y del conocimiento.
- Cada documento conserva ID, título, tipo, URL, versión o fecha de actualización y fecha de carga.
- El cargador consulta una lista explícita de tickets y páginas. No recorre toda la organización.
- La recuperación selecciona reglas por sección y ejemplos por palabras del cambio.
- La carga ocurre antes de la demo. Una actualización manual sustituye la versión anterior y conserva la última carga válida.

Confluence tiene un plan Free independiente, con hasta diez usuarios y 2 GB de archivos [S1].
Se agrega al sitio Atlassian existente como otra aplicación [S2]. Su disponibilidad no confirma que ya esté activado.

### Flujo principal

1. El cargador obtiene los ejemplos y los modelos operativos autorizados para la demo.
2. El usuario describe el cambio en el chat.
3. El agente consulta el conocimiento e inicia el borrador estructurado.
4. El backend ejecuta las tres verificaciones.
5. El agente pregunta por los datos pendientes y actualiza el borrador con las respuestas.
6. El frontend muestra el borrador, las fuentes y los resultados.
7. Cuando el usuario solicita crear el ticket, el backend revalida el borrador vigente.
8. El conector crea el ticket y devuelve su clave y URL reales.

La interfaz admite el comando «crear ticket» y una acción equivalente en pantalla.
Las acciones y los resultados de herramientas son visibles. El sistema no necesita mostrar razonamiento interno del modelo.

### Representación en Jira

Se propone utilizar un tipo de ticket existente, como `Task`, con la etiqueta `ocd-demo`.
La descripción contiene las secciones del OCD y los resultados de verificación.
El resumen identifica el microservicio y el cambio solicitado.
Los campos obligatorios reales dependen del proyecto y del tipo de ticket [S9].
El conector comprueba esos metadatos antes de implementar la creación.
El tipo de ticket y el proyecto definitivos quedan configurados mediante variables.

Estados internos: `BORRADOR`, `FALTAN_DATOS`, `LISTO`, `CREADO` y `ERROR_CREACION`.
Estos estados pertenecen al MVP; no requieren personalizar el flujo de Jira.

### Datos mínimos

| Entidad | Datos esenciales |
|---|---|
| Documento | Origen, ID externo, título, URL, versión/fecha, contenido y secciones aplicables. |
| Borrador | ID, sesión, revisión, datos del OCD, verificaciones y referencias. |
| Creación | Clave de operación, borrador/revisión, estado, clave Jira, URL y fecha. |

La clave de operación evita duplicar la creación de la misma revisión desde el chat o un doble clic.
Después de una respuesta ambigua de Jira, el backend consulta el marcador del ticket antes de repetir la escritura.
Si no puede determinar el resultado, conserva el estado pendiente de comprobar y evita repetir automáticamente la creación.

### Seguridad y fallos relevantes

- Ejecutar el servidor en `localhost` con una cuenta de demostración y contenido sintético.
- Mantener las credenciales en variables del backend. El navegador y el contexto del modelo nunca reciben sus valores.
- Limitar lecturas a páginas/tickets configurados y escrituras al proyecto Jira de demostración.
- Tratar el contenido de páginas y tickets como datos. Las instrucciones del agente y las reglas ejecutables provienen de la aplicación.
- Vincular cada regla a su fuente y versión. Un ticket histórico no sustituye un modelo operativo vigente.
- Aplicar tiempos máximos a llamadas externas y reintentos limitados para lecturas.
- Conservar el borrador ante errores de Jira o del modelo. Mostrar el fallo y permitir reanudar.
- Registrar duración, herramientas utilizadas, validaciones y resultado de creación, con datos sensibles omitidos.

Los cuatro casos describen cambios solicitados en el OCD. La demo termina al crear el ticket.
La ejecución de despliegues, reglas de red e identidades Azure requiere otra integración y otro alcance.

## 3. Modelo y costo propuesto

Se recomienda empezar con `gpt-6-luna`, mediante Responses API y llamadas a herramientas.
Soporta function calling y salidas estructuradas [S5]. Su costo resulta adecuado para esta tarea acotada y validada mediante reglas.
La calidad para este proceso se comprobará con los tres casos de aceptación. No se afirma una superioridad universal.

Tarifas públicas estándar consultadas el 12 de noviembre de 2026. USD por un millón de tokens; entrada sin caché [S5–S6].

| Modelo | Entrada | Salida | Uso propuesto |
|---|---:|---:|---|
| `gpt-6-luna` | 0.10 | 0.50 | Modelo inicial del MVP. |
| `gpt-6.1-sol` | 2.00 | 10.00 | Alternativa si el modelo inicial falla los casos de aceptación. |

Ejemplo ilustrativo: cien flujos, cada uno con diez mil tokens de entrada y dos mil de salida.
El consumo incluye todas las rondas y las herramientas del flujo. Los tokens de razonamiento facturables forman parte de la salida.

`Costo Luna = 1,000,000 / 1,000,000 × 0.10 + 200,000 / 1,000,000 × 0.50 = USD 0.20`.

El ejemplo supone contexto corto y procesamiento estándar. Excluye impuestos, caché explícita y herramientas alojadas con cargos propios.
La aplicación local, Jira Free y Confluence Free no añaden una suscripción de cómputo a esta estimación.
El acceso a una cuenta API con el modelo habilitado queda pendiente de verificar.

## 4. Plan orientativo y aceptación

Estimación para una persona con acceso a las API y contenido de demostración preparado.

| Minutos | Actividad | Responsable | Criterio de salida |
|---:|---|---|---|
| 45 | Preparar conexiones y probar lectura y creación en Jira. | Desarrollador | Un ticket de prueba real y lectura de Confluence. |
| 45 | Cargar modelos operativos y ejemplos en SQLite. | Desarrollador | Fuentes consultables con sus referencias. |
| 90 | Implementar agente, esquema OCD, reglas y creación sin duplicados. | Desarrollador | Flujo completo desde un mensaje hasta un ticket. |
| 60 | Construir el chat, el borrador y los estados de verificaciones. | Desarrollador | Una pantalla operativa. |
| 60 | Ejecutar tres casos, corregir fallos y preparar la demo. | Desarrollador | Evidencias reproducibles y recorrido ensayado. |
| **300** | **Total de desarrollo.** | | **Cinco horas.** |
| 60 | Presentar el MVP. | Presentador | Hora adicional reservada por el usuario. |

La configuración inicial de Confluence y de las credenciales puede consumir parte del primer bloque.
Si esos accesos faltan, se conserva un borrador local y se identifica la creación real como aceptación pendiente.

| Caso | Entrada | Aceptación |
|---|---|---|
| Completo | Cambio con los datos requeridos de sus secciones activadas. | Ticket Jira real con las secciones, referencias y clave retornada. |
| Incompleto | Solicitud sin destino de red o alcance del permiso. | Preguntas precisas; faltantes visibles; borrador conservado. |
| Inconsistente | Puerto fuera de rango o ambientes incompatibles según la regla de demo. | Error reproducible; corrección conversacional; validación posterior. |

Medir tiempo manual y tiempo asistido sobre los mismos casos.
Registrar campos omitidos, interacciones necesarias y tickets duplicados. Los porcentajes de ahorro salen de estas mediciones.

Fuentes preparadas: proyecto Jira SCRUM, tipo Tarea, veinte tickets y cuatro modelos operativos publicados en Confluence DDS.
Pendientes de implementación: acceso al modelo, número real de desarrolladores, frontend, backend e ingesta del conocimiento.
Referencias de conocimiento: [modelos_operativos/README.md](modelos_operativos/README.md).
El documento y el diagrama representan diseño. Todavía no existen código del MVP ni pruebas ejecutadas de las integraciones.

## Fuentes

Consulta: 12 de noviembre de 2026.

- S1: [Confluence Free y límites](https://www.atlassian.com/en/software/confluence/pricing).
- S2: [Agregar aplicaciones Atlassian al sitio existente](https://support.atlassian.com/jira-cloud-administration/docs/set-up-jira-products/).
- S3: [Autenticación de clientes privados y scripts Atlassian](https://developer.atlassian.com/developer-guide/auth/).
- S4: [Autenticación REST de Confluence](https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/).
- S5: [GPT-6 Luna: capacidades y tarifas](https://developers.openai.com/api/docs/models/gpt-6-luna).
- S6: [GPT-6.1 Sol: capacidades y tarifas](https://developers.openai.com/api/docs/models/gpt-6.1-sol).
- S7: [Identidad de aplicación y permisos de un service principal](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal).
- S8: [Archivos estáticos en FastAPI](https://fastapi.tiangolo.com/tutorial/static-files/).
- S9: [Crear tickets y consultar metadatos Jira](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/).

Diagrama editable: [MVP_OCD_Arquitectura.drawio](MVP_OCD_Arquitectura.drawio).
