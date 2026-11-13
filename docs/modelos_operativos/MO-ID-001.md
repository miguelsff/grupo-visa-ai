# MO-ID-001 - Identidades de servicio con Microsoft Entra ID [DEMO]

**Naturaleza:** modelo operativo sintético de demostración. No representa una política oficial de la empresa financiera.

**Código:** MO-ID-001. **Versión documental:** 1.0. **Revisión Confluence:** 1.
**Fecha:** 12 de noviembre de 2026.

**Publicado:** [MO-ID-001 - Identidades de servicio con Microsoft Entra ID [DEMO]](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/294943/MO-ID-001+-+Identidades+de+servicio+con+Microsoft+Entra+ID+DEMO).
**Reglas comunes:** [MO-OCD-000](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/66048/DEMO+OCD+-+ndice+y+reglas+comunes).

## Objetivo

Preparar un OCD que diferencie identidad, autenticación y autorización de un servicio.

## Alcance

Aplica a ID-01 a ID-05: pipelines, lectura de secretos, mensajería, archivos y consumo de una API.

Las secciones aplicables se combinan cuando un cambio incluye varios casos.

## Campos específicos

| Campo | Tipo | Cuándo se requiere | Ejemplo o indicación |
| --- | --- | --- | --- |
| tenant / nombre_identidad | Identificador o marcador de demo y nombre solicitado | Siempre | TENANT-DEMO / sp-demo-emisor-notificaciones |
| consumidor / finalidad | Aplicación o pipeline y uso esperado | Siempre | ms-demo-productor-notificaciones / enviar mensajes |
| identidad_nueva / existente | Selección y referencia | Siempre | Nueva; todavía sin client ID ni object ID |
| client_id / object_id | Identificadores diferenciados | Si existe la identidad | Registrar los valores reales solo al disponer de ellos |
| mecanismo_autenticacion | Federación o certificado en los casos de demo | Siempre | OIDC o referencia de certificado |
| confianza_o_certificado | Emisor, sujeto y audiencia; o referencia y vigencia | Según el mecanismo | Pipeline y ambiente concretos; sin claves privadas |
| destino / tipo_autorizacion | Recurso Azure o API y mecanismo | Siempre | Cola Service Bus / Azure RBAC |
| rol_y_alcance | Rol y recurso; o app role y API | Siempre | Azure Service Bus Data Sender / cola concreta |
| pruebas / revocacion | Prueba permitida, denegación y retirada | Siempre | Enviar un mensaje y denegar recepción |

## Precondiciones

- Identificar si se crea una identidad o se reutiliza una existente.
- Definir el destino y las operaciones necesarias antes de seleccionar permisos.
- Evaluar identidad administrada cuando sea compatible; conservar la justificación si se solicita un service principal.
- Registrar referencias y metadatos de credenciales, nunca sus valores.
- Utilizar un alcance concreto y distinguir administración del recurso de acceso a sus datos.

## Procedimiento

| Responsable ficticio | Acción | Salida o evidencia esperada |
| --- | --- | --- |
| Solicitante | Describir el consumidor, el destino y las operaciones necesarias. | Identidad y permisos solicitados en el OCD. |
| Identidades | Comprobar tenant, identidad y mecanismo de autenticación propuesto. | Identificadores existentes o estado pendiente de creación. |
| Identidades / Plataforma | Preparar autenticación y asignaciones en certificación. | Referencias de confianza o certificado y permisos específicos. |
| QA / Certificación | Comprobar una operación permitida y otra no autorizada. | Resultados de token y autorización sin exponer tokens. |
| Identidades / Plataforma | Crear o configurar la identidad objetivo mediante el proceso autorizado. | Client ID, object ID, asignaciones y metadatos de credencial. |
| Responsable del cambio | Registrar evidencia y procedimiento de revocación. | Estado final y componentes nuevos identificados. |

## Reglas verificables

| Regla | Clase | Campos o evidencia | Resultado esperado | Modo |
| --- | --- | --- | --- | --- |
| ID-R01 | Completitud | tenant, identidad, consumidor, destino y finalidad | FALTA_INFORMACION si no se conoce quién accede a qué y para qué. | Documental automática |
| ID-R02 | Consistencia | autenticación y referencias | ERROR si incluye una clave privada, contraseña o token como contenido del ticket; los identificadores públicos no son secretos. | Documental con detección limitada |
| ID-R03 | Consistencia | tipo de autorización, rol y alcance | FALTA_INFORMACION si un rol Azure RBAC carece de alcance o un app role carece de API destino. | Documental automática |
| ID-R04 | Trazabilidad | pruebas positiva/negativa y revocación | FALTA_INFORMACION si no describe acceso permitido, denegación y retirada de asignaciones nuevas. | Documental automática |
| ID-R05 | Ejecución | confianza, token y permiso efectivo | NO_VERIFICABLE sin evidencia de autenticación y operación en el destino. Leer un token no prueba su validez. | Técnica mediante evidencia |

El backend debe ejecutar las comprobaciones reproducibles. El modelo de lenguaje identifica faltantes y explica resultados.
La implementación y ejecución de estas validaciones sigue pendiente en el backend del MVP.

## Evidencias previstas

- Tenant, client ID y object ID de la identidad creada o existente.
- Referencias de confianza federada o certificado y su vigencia.
- Rol y alcance, o app role y API destino, efectivamente asignados.
- Resultado de pruebas permitidas y denegadas, sin tokens ni credenciales.
- Registro de revocación si se utilizó la reversión.

Los resultados permanecen pendientes hasta ejecutarse las pruebas. La existencia del modelo o del ticket no demuestra aprobación de certificación.

## Reversión

Revocar las asignaciones y credenciales agregadas. Retirar una identidad nueva solo después de comprobar sus dependencias. Conservar las identidades preexistentes.

## Criterio para revertir

Revertir si falla el acceso previsto o se detectan operaciones permitidas fuera del alcance documentado.

## Aceptación del baseline

El baseline identifica consumidor, autenticación, destino, autorización y revocación. No declara un acceso efectivo sin pruebas.

## Pregunta inicial sugerida

¿Qué servicio necesita autenticarse, contra qué destino, con qué mecanismo y para realizar qué operaciones?

## Tickets relacionados

- ID-01: [SCRUM-20](https://grupo-visai.atlassian.net/browse/SCRUM-20).
- ID-02: [SCRUM-21](https://grupo-visai.atlassian.net/browse/SCRUM-21).
- ID-03: [SCRUM-22](https://grupo-visai.atlassian.net/browse/SCRUM-22).
- ID-04: [SCRUM-23](https://grupo-visai.atlassian.net/browse/SCRUM-23).
- ID-05: [SCRUM-24](https://grupo-visai.atlassian.net/browse/SCRUM-24).

## Uso del material

- Conservar el código, la versión y la URL del modelo consultado.
- No sustituir datos faltantes con valores de otro ticket.
- Distinguir revisión documental de evidencia de ejecución.
- Excluir el ejemplo OCD mencionado por el usuario.
- Conservar valores de credenciales fuera del ticket, del chat y de los registros.

## Base técnica y fuentes

El service principal representa una aplicación en un tenant. La autenticación obtiene una identidad verificable; el recurso aplica la autorización. Azure RBAC y los app roles de una API tienen ámbitos diferentes.
Las fuentes sustentan conceptos técnicos. Los campos y reglas son propuestas para el MVP.

- [Objetos de aplicación y service principals](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals).
- [Autenticación servicio a servicio](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow).
- [Mínimo privilegio y alcance Azure RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices).
- [Elección y permisos de identidades administradas](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/managed-identity-best-practice-recommendations).
