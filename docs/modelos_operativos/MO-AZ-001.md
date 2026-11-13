# MO-AZ-001 - Configuración de componentes Azure [DEMO]

**Naturaleza:** modelo operativo sintético de demostración. No representa una política oficial de la empresa financiera.

**Código:** MO-AZ-001. **Versión documental:** 1.0. **Revisión Confluence:** 1.
**Fecha:** 12 de noviembre de 2026.

**Publicado:** [MO-AZ-001 - Configuración de componentes Azure [DEMO]](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/131339/MO-AZ-001+-+Configuraci+n+de+componentes+Azure+DEMO).
**Reglas comunes:** [MO-OCD-000](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/66048/DEMO+OCD+-+ndice+y+reglas+comunes).

## Objetivo

Preparar un OCD que describa un cambio de configuración Azure y permita revisar su efecto y su reversión.

## Alcance

Aplica a AZ-01 a AZ-05: Container Apps, Application Insights, Service Bus, App Configuration y referencias de Key Vault.

Las secciones aplicables se combinan cuando un cambio incluye varios casos.

## Campos específicos

| Campo | Tipo | Cuándo se requiere | Ejemplo o indicación |
| --- | --- | --- | --- |
| tipo_servicio / recurso | Texto | Siempre | Container Apps / ca-demo-transferencias |
| suscripcion / grupo_recursos / region | Identificadores o marcadores de demo | Siempre | SUB-OCD-DEMO / rg-ocd-demo-prod / East US |
| configuracion_actual | Valores o explicación de inexistencia | Siempre | Réplicas mínimas 1 y máximas 1 |
| configuracion_propuesta | Valores y unidades | Siempre | Réplicas mínimas 1 y máximas 3 |
| dependencias / efecto | Lista y explicación | Siempre | Reinicio, conectividad o mensajes pendientes |
| referencias_credenciales | Nombre o referencia; nunca valor | Si intervienen secretos o certificados | kv-demo-beneficiarios / conexion-demo |
| criterio_prueba | Acción y resultado esperado | Siempre | Réplicas observadas dentro del rango previsto |

## Precondiciones

- Identificar el recurso y el ambiente al que corresponde la configuración.
- Registrar los valores anteriores y la forma de recuperarlos.
- Describir dependencias y posibles interrupciones del componente.
- Separar referencias de secretos y valores de configuración ordinaria.

## Procedimiento

| Responsable ficticio | Acción | Salida o evidencia esperada |
| --- | --- | --- |
| Solicitante | Documentar el estado actual y el estado propuesto. | Comparación concreta de configuración. |
| Plataforma | Comprobar identificadores, dependencias y compatibilidad del recurso. | Lista de precondiciones y pendientes. |
| Plataforma / QA | Aplicar y comprobar el cambio equivalente en certificación. | Resultados de las pruebas previstas. |
| Plataforma | Aplicar únicamente la configuración descrita en la ventana definida. | Registro del cambio y valores efectivos. |
| QA / Certificación | Comprobar funcionamiento y ausencia de cambios ajenos al alcance. | Comparación del resultado con el criterio previsto. |
| Responsable del cambio | Registrar el resultado o restaurar la configuración anterior. | Evidencias y estado final. |

## Reglas verificables

| Regla | Clase | Campos o evidencia | Resultado esperado | Modo |
| --- | --- | --- | --- | --- |
| AZ-R01 | Completitud | servicio, recurso, suscripción, grupo y región | FALTA_INFORMACION si falta el contexto del recurso objetivo. | Documental automática |
| AZ-R02 | Consistencia | configuración actual y propuesta | ERROR si no existe una diferencia coherente con el objetivo declarado. | Documental automática |
| AZ-R03 | Consistencia | réplicas o bandera de funcionalidad | Para los casos de demo: ERROR si mínimas supera máximas o la bandera no es un booleano. | Documental automática |
| AZ-R04 | Trazabilidad | configuración anterior, prueba y reversión | FALTA_INFORMACION si la solicitud no indica cómo comprobar y recuperar el cambio. | Documental automática |
| AZ-R05 | Ejecución | existencia, compatibilidad y valores efectivos | NO_VERIFICABLE sin lectura Azure o evidencias accesibles. No inferir cuotas ni disponibilidad. | Técnica mediante evidencia |

El backend debe ejecutar las comprobaciones reproducibles. El modelo de lenguaje identifica faltantes y explica resultados.
La implementación y ejecución de estas validaciones sigue pendiente en el backend del MVP.

## Evidencias previstas

- Comparación de configuración antes y después, con valores sensibles omitidos.
- Identificador del recurso y fecha del cambio.
- Resultado de la prueba específica del componente.
- Comprobación de recuperación si se utilizó la reversión.

Los resultados permanecen pendientes hasta ejecutarse las pruebas. La existencia del modelo o del ticket no demuestra aprobación de certificación.

## Reversión

Restaurar los valores anteriores y comprobar el servicio. En mensajería, conservar los mensajes. En Key Vault, restaurar referencias sin divulgar valores.

## Criterio para revertir

Revertir si falla el criterio funcional o aparece una dependencia no contemplada en el ticket.

## Aceptación del baseline

El baseline permite identificar el recurso, el cambio concreto, sus dependencias, la prueba y la recuperación.

## Pregunta inicial sugerida

¿Qué recurso cambia, cuáles son sus valores actuales y qué valores propones aplicar?

## Tickets relacionados

- AZ-01: [SCRUM-10](https://grupo-visai.atlassian.net/browse/SCRUM-10).
- AZ-02: [SCRUM-11](https://grupo-visai.atlassian.net/browse/SCRUM-11).
- AZ-03: [SCRUM-12](https://grupo-visai.atlassian.net/browse/SCRUM-12).
- AZ-04: [SCRUM-13](https://grupo-visai.atlassian.net/browse/SCRUM-13).
- AZ-05: [SCRUM-14](https://grupo-visai.atlassian.net/browse/SCRUM-14).

## Uso del material

- Conservar el código, la versión y la URL del modelo consultado.
- No sustituir datos faltantes con valores de otro ticket.
- Distinguir revisión documental de evidencia de ejecución.
- Excluir el ejemplo OCD mencionado por el usuario.
- Conservar valores de credenciales fuera del ticket, del chat y de los registros.

## Base técnica y fuentes

Microsoft incluye los cambios de configuración y de infraestructura dentro de los despliegues que requieren controles de salud. Las reglas AZ-R01 a AZ-R05 son propuestas del MVP.
Las fuentes sustentan conceptos técnicos. Los campos y reglas son propuestas para el MVP.

- [Configuración y despliegues seguros](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments).
- [Permisos y alcance de acceso a recursos](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices).
