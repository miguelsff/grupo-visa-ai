# MO-MIC-001 - Pase a producción de microservicios [DEMO]

**Naturaleza:** modelo operativo sintético de demostración. No representa una política oficial de la empresa financiera.

**Código:** MO-MIC-001. **Versión documental:** 1.0. **Revisión Confluence:** 1.
**Fecha:** 12 de noviembre de 2026.

**Publicado:** [MO-MIC-001 - Pase a producción de microservicios [DEMO]](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/294922/MO-MIC-001+-+Pase+a+producci+n+de+microservicios+DEMO).
**Reglas comunes:** [MO-OCD-000](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/66048/DEMO+OCD+-+ndice+y+reglas+comunes).

## Objetivo

Preparar y verificar el baseline de un OCD para certificar una nueva versión de un microservicio.

## Alcance

Aplica a MIC-01 a MIC-05. El procedimiento describe el pase posterior; el agente del MVP genera la solicitud y registra pendientes.

Las secciones aplicables se combinan cuando un cambio incluye varios casos.

## Campos específicos

| Campo | Tipo | Cuándo se requiere | Ejemplo o indicación |
| --- | --- | --- | --- |
| microservicio | Texto | Siempre | ms-demo-transferencias |
| repositorio | URL o referencia | Siempre | https://git.example/ocd/ms-demo-transferencias |
| version_actual / version_objetivo | Texto | Siempre | 1.3.0 / 1.3.1 |
| artefacto | Referencia de imagen o paquete | Siempre | acr-demo.example/ms-demo-transferencias:1.3.1 |
| identificador_inmutable | Digest, hash o ID de compilación | Antes de ejecutar el despliegue | PENDIENTE si todavía no está disponible |
| dependencias | Lista o NO_APLICA justificado | Siempre | Base de datos, cola o API dependiente |
| cambio_datos / compatibilidad | Sí/no y explicación | Si cambia un contrato o datos | Sin migración de datos para los ejemplos |
| pruebas_y_reversion | Pasos y criterios observables | Siempre | Idempotencia y recuperación de la versión anterior |

## Precondiciones

- Identificar la versión que funciona actualmente y conservar su referencia.
- Utilizar en certificación el artefacto que se propone promover.
- Describir dependencias y cambios de contrato que afecten la reversión.
- Definir las comprobaciones funcionales antes de solicitar la ejecución.

## Procedimiento

| Responsable ficticio | Acción | Salida o evidencia esperada |
| --- | --- | --- |
| Solicitante | Completar los campos y describir el cambio funcional. | Borrador del OCD con versión y artefacto. |
| Desarrollo / DevOps | Validar la versión en certificación y registrar el resultado. | Evidencia fechada de pruebas; pendiente hasta ejecutarlas. |
| DevOps | Registrar versión anterior y comprobar la preparación de la reversión. | Referencia de recuperación y dependencias conocidas. |
| DevOps | Promover el artefacto indicado durante la ventana autorizada por el proceso existente. | Registro de versión, inicio y resultado del despliegue. |
| QA / Certificación | Comprobar salud y comportamiento funcional del cambio. | Resultado esperado frente a resultado obtenido. |
| Responsable del cambio | Registrar éxito o activar la reversión definida. | Resultado final y enlaces a evidencias. |

## Reglas verificables

| Regla | Clase | Campos o evidencia | Resultado esperado | Modo |
| --- | --- | --- | --- | --- |
| MIC-R01 | Completitud | microservicio, repositorio, versiones, artefacto | FALTA_INFORMACION si falta un dato obligatorio del baseline. | Documental automática |
| MIC-R02 | Consistencia | version_actual y version_objetivo | ERROR si son iguales y el cambio afirma publicar una versión diferente. | Documental automática |
| MIC-R03 | Consistencia | artefacto y version_objetivo | ERROR si el tag o la referencia del artefacto contradice la versión declarada. | Documental automática |
| MIC-R04 | Trazabilidad | pruebas y reversión | FALTA_INFORMACION si no existe un criterio funcional o una versión/configuración recuperable. | Documental automática |
| MIC-R05 | Ejecución | salud y pruebas de negocio | NO_VERIFICABLE sin ejecución o evidencia accesible del ambiente objetivo. | Técnica mediante evidencia |

El backend debe ejecutar las comprobaciones reproducibles. El modelo de lenguaje identifica faltantes y explica resultados.
La implementación y ejecución de estas validaciones sigue pendiente en el backend del MVP.

## Evidencias previstas

- Referencia del artefacto probado y del artefacto publicado.
- Resultados de pruebas funcionales y de regresión.
- Registro de salud y errores antes y después del cambio.
- Resultado de la reversión, únicamente si se ejecutó.

Los resultados permanecen pendientes hasta ejecutarse las pruebas. La existencia del modelo o del ticket no demuestra aprobación de certificación.

## Reversión

Recuperar la versión anterior y sus referencias de configuración. Verificar compatibilidad de datos antes de revertir. Conservar mensajes pendientes en escenarios asíncronos.

## Criterio para revertir

Activar la reversión si falla la comprobación funcional o el criterio de salud definido en el ticket.

## Aceptación del baseline

El baseline identifica versión, artefacto, dependencias, pruebas, reversión y pendientes. La aptitud técnica exige evidencias ejecutadas.

## Pregunta inicial sugerida

¿Qué versión y artefacto quieres certificar y qué versión debemos recuperar si falla?

## Tickets relacionados

- MIC-01: [SCRUM-5](https://grupo-visai.atlassian.net/browse/SCRUM-5).
- MIC-02: [SCRUM-6](https://grupo-visai.atlassian.net/browse/SCRUM-6).
- MIC-03: [SCRUM-7](https://grupo-visai.atlassian.net/browse/SCRUM-7).
- MIC-04: [SCRUM-8](https://grupo-visai.atlassian.net/browse/SCRUM-8).
- MIC-05: [SCRUM-9](https://grupo-visai.atlassian.net/browse/SCRUM-9).

## Uso del material

- Conservar el código, la versión y la URL del modelo consultado.
- No sustituir datos faltantes con valores de otro ticket.
- Distinguir revisión documental de evidencia de ejecución.
- Excluir el ejemplo OCD mencionado por el usuario.
- Conservar valores de credenciales fuera del ticket, del chat y de los registros.

## Base técnica y fuentes

Microsoft recomienda despliegues graduales con comprobaciones de salud y recuperación ante fallos. Las reglas MIC-R01 a MIC-R05 son propuestas del MVP.
Las fuentes sustentan conceptos técnicos. Los campos y reglas son propuestas para el MVP.

- [Despliegues seguros y controles de salud](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments).
