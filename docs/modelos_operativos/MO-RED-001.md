# MO-RED-001 - Accesos de red [DEMO]

**Naturaleza:** modelo operativo sintético de demostración. No representa una política oficial de la empresa financiera.

**Código:** MO-RED-001. **Versión documental:** 1.0. **Revisión Confluence:** 1.
**Fecha:** 12 de noviembre de 2026.

**Publicado:** [MO-RED-001 - Accesos de red [DEMO]](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/98314/MO-RED-001+-+Accesos+de+red+DEMO).
**Reglas comunes:** [MO-OCD-000](https://grupo-visai.atlassian.net/wiki/spaces/DDS/pages/66048/DEMO+OCD+-+ndice+y+reglas+comunes).

## Objetivo

Preparar un OCD de conectividad con origen, destino, protocolo y puertos explícitos.

## Alcance

Aplica a RED-01 a RED-05. El MVP contempla TCP y UDP; otros protocolos requieren revisión técnica específica.

Las secciones aplicables se combinan cuando un cambio incluye varios casos.

## Campos específicos

| Campo | Tipo | Cuándo se requiere | Ejemplo o indicación |
| --- | --- | --- | --- |
| origen / ambiente_origen | IP, CIDR o referencia lógica y ambiente | Siempre | 10.240.10.0/24 / prod-demo |
| destino / ambiente_destino | IP o CIDR de regla y referencia del recurso | Siempre | 10.240.20.10 / SQL privado / prod-demo |
| nombre_dns | FQDN | Si se utiliza resolución de nombres | api-riesgo.demo.example |
| protocolo / puerto_destino | TCP o UDP; número o rango | Siempre | TCP / 1433 |
| puerto_origen | Puerto o efímero según el flujo | Al definir la regla ejecutable | Efímero; justificar comodines cuando correspondan |
| sentido / finalidad | Entrada o salida y necesidad del flujo | Siempre | Salida para consultar la base de datos |
| punto_control / regla | NSG, firewall u otro control; nombre de regla | Antes de ejecutar | demo-red-01; control específico pendiente |
| regla_anterior / reversion | Descripción y retirada del cambio concreto | Siempre | Retirar únicamente demo-red-01 |

## Precondiciones

- Identificar los ambientes y la necesidad funcional del acceso.
- Distinguir resolución DNS, rutas, filtrado y autorización del servicio.
- Identificar el control que aplicará la regla antes de ejecutarla.
- Conservar la configuración previa y el nombre exacto de las reglas que se agregarán.

## Procedimiento

| Responsable ficticio | Acción | Salida o evidencia esperada |
| --- | --- | --- |
| Solicitante | Completar el flujo de origen a destino y justificarlo. | Matriz de conectividad del OCD. |
| Redes | Revisar direcciones, rutas y reglas relacionadas sin ampliar el alcance solicitado. | Precondiciones y control objetivo. |
| Redes / QA | Comprobar el flujo equivalente en certificación. | Prueba positiva y, cuando corresponda, negativa. |
| Redes | Aplicar la regla precisa durante la ventana definida. | Nombre y configuración efectiva de la regla. |
| QA / Certificación | Comprobar conectividad desde el origen permitido. | Resultado fechado y punto desde el que se probó. |
| Responsable del cambio | Registrar el resultado y retirar la regla si se requiere reversión. | Estado final y configuración conservada. |

## Reglas verificables

| Regla | Clase | Campos o evidencia | Resultado esperado | Modo |
| --- | --- | --- | --- | --- |
| RED-R01 | Completitud | origen, destino, ambientes, protocolo, puerto y finalidad | FALTA_INFORMACION si no puede reconstruirse el flujo solicitado. | Documental automática |
| RED-R02 | Consistencia | IP/CIDR y puertos | ERROR ante IP/CIDR inválido, puerto fuera de 1–65535 o rango invertido. | Documental automática |
| RED-R03 | Consistencia | protocolo y DNS | El caso DNS de demo declara UDP y TCP/53. FALTA_INFORMACION si solo indica «abrir DNS». | Documental automática |
| RED-R04 | Trazabilidad | control, nombre de regla y reversión | FALTA_INFORMACION antes de ejecutar si no se identifica qué regla agregar y retirar. | Documental automática |
| RED-R05 | Ejecución | rutas, resolución, filtrado y alcance efectivo | NO_VERIFICABLE sin consulta o prueba técnica accesible. Un puerto escrito no demuestra conectividad. | Técnica mediante evidencia |

El backend debe ejecutar las comprobaciones reproducibles. El modelo de lenguaje identifica faltantes y explica resultados.
La implementación y ejecución de estas validaciones sigue pendiente en el backend del MVP.

## Evidencias previstas

- Matriz de conectividad solicitada y regla efectivamente aplicada.
- Origen y destino utilizados en la prueba.
- Resultados separados de DNS, transporte y autorización del servicio.
- Configuración restaurada si se retiró la regla.

Los resultados permanecen pendientes hasta ejecutarse las pruebas. La existencia del modelo o del ticket no demuestra aprobación de certificación.

## Reversión

Retirar solamente las reglas agregadas por el OCD. Restaurar rutas o configuración DNS únicamente si también formaron parte del cambio.

## Criterio para revertir

Revertir si no se logra el acceso previsto o se observa un alcance distinto del solicitado.

## Aceptación del baseline

El baseline describe el flujo y la regla propuesta. La conectividad efectiva permanece pendiente hasta obtener una prueba.

## Pregunta inicial sugerida

¿Desde qué origen y ambiente necesitas acceder, hacia qué destino y mediante qué protocolo y puerto?

## Tickets relacionados

- RED-01: [SCRUM-15](https://grupo-visai.atlassian.net/browse/SCRUM-15).
- RED-02: [SCRUM-16](https://grupo-visai.atlassian.net/browse/SCRUM-16).
- RED-03: [SCRUM-17](https://grupo-visai.atlassian.net/browse/SCRUM-17).
- RED-04: [SCRUM-18](https://grupo-visai.atlassian.net/browse/SCRUM-18).
- RED-05: [SCRUM-19](https://grupo-visai.atlassian.net/browse/SCRUM-19).

## Uso del material

- Conservar el código, la versión y la URL del modelo consultado.
- No sustituir datos faltantes con valores de otro ticket.
- Distinguir revisión documental de evidencia de ejecución.
- Excluir el ejemplo OCD mencionado por el usuario.
- Conservar valores de credenciales fuera del ticket, del chat y de los registros.

## Base técnica y fuentes

Un NSG identifica origen y destino mediante direcciones o constructos admitidos por Azure. Un FQDN lógico debe resolverse al destino apropiado del control. El rango 1–65535 y el conjunto TCP/UDP son reglas del MVP, no una descripción exhaustiva de Azure.
Las fuentes sustentan conceptos técnicos. Los campos y reglas son propuestas para el MVP.

- [Propiedades y evaluación de reglas NSG](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview).
