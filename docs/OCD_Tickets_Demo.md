# 20 tickets OCD creados en Jira

**Estado: 20 tickets creados en Jira mediante MCP, todos en Por hacer.**

## Tickets creados

| Borrador | Clave Jira | Caso | Estado |
|---|---|---|---|
| MIC-01 | [SCRUM-5](https://grupo-visai.atlassian.net/browse/SCRUM-5) | microservicio | Por hacer |
| MIC-02 | [SCRUM-6](https://grupo-visai.atlassian.net/browse/SCRUM-6) | microservicio | Por hacer |
| MIC-03 | [SCRUM-7](https://grupo-visai.atlassian.net/browse/SCRUM-7) | microservicio | Por hacer |
| MIC-04 | [SCRUM-8](https://grupo-visai.atlassian.net/browse/SCRUM-8) | microservicio | Por hacer |
| MIC-05 | [SCRUM-9](https://grupo-visai.atlassian.net/browse/SCRUM-9) | microservicio | Por hacer |
| AZ-01 | [SCRUM-10](https://grupo-visai.atlassian.net/browse/SCRUM-10) | azure | Por hacer |
| AZ-02 | [SCRUM-11](https://grupo-visai.atlassian.net/browse/SCRUM-11) | azure | Por hacer |
| AZ-03 | [SCRUM-12](https://grupo-visai.atlassian.net/browse/SCRUM-12) | azure | Por hacer |
| AZ-04 | [SCRUM-13](https://grupo-visai.atlassian.net/browse/SCRUM-13) | azure | Por hacer |
| AZ-05 | [SCRUM-14](https://grupo-visai.atlassian.net/browse/SCRUM-14) | azure | Por hacer |
| RED-01 | [SCRUM-15](https://grupo-visai.atlassian.net/browse/SCRUM-15) | red | Por hacer |
| RED-02 | [SCRUM-16](https://grupo-visai.atlassian.net/browse/SCRUM-16) | red | Por hacer |
| RED-03 | [SCRUM-17](https://grupo-visai.atlassian.net/browse/SCRUM-17) | red | Por hacer |
| RED-04 | [SCRUM-18](https://grupo-visai.atlassian.net/browse/SCRUM-18) | red | Por hacer |
| RED-05 | [SCRUM-19](https://grupo-visai.atlassian.net/browse/SCRUM-19) | red | Por hacer |
| ID-01 | [SCRUM-20](https://grupo-visai.atlassian.net/browse/SCRUM-20) | identidad | Por hacer |
| ID-02 | [SCRUM-21](https://grupo-visai.atlassian.net/browse/SCRUM-21) | identidad | Por hacer |
| ID-03 | [SCRUM-22](https://grupo-visai.atlassian.net/browse/SCRUM-22) | identidad | Por hacer |
| ID-04 | [SCRUM-23](https://grupo-visai.atlassian.net/browse/SCRUM-23) | identidad | Por hacer |
| ID-05 | [SCRUM-24](https://grupo-visai.atlassian.net/browse/SCRUM-24) | identidad | Por hacer |


Destino verificado mediante el MCP: Grupo VisAI (`SCRUM`), tipo `Tarea`, sitio https://grupo-visai.atlassian.net.

Estos borradores contienen exclusivamente datos sintéticos. El ejemplo del usuario no se utilizó como fuente de contenido.

Hay cinco tickets por caso: microservicios, configuración Azure, accesos de red e identidades Microsoft Entra ID.

Los identificadores MIC, AZ, RED e ID son referencias locales de borrador. No son claves de tickets Jira existentes.

## Parámetros comunes

- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Suscripción: SUB-OCD-DEMO; grupo de recursos: rg-ocd-demo-prod; región: East US.
- Ventana: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- La creación se realizaría en el estado inicial del proyecto. No se solicitaron asignaciones personales ni transiciones.
- Etiquetas: ocd-demo, datos-sinteticos, caso-<categoria> y ejemplo-<identificador>.
- Evidencias: Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.

## Índice

| Borrador | Caso | Resumen |
|---|---|---|
| MIC-01 | microservicio | Pase a producción de ms-demo-transferencias v1.3.1 |
| MIC-02 | microservicio | Pase a producción de ms-demo-saldos v1.2.0 |
| MIC-03 | microservicio | Pase a producción de ms-demo-notificaciones v1.0.0 |
| MIC-04 | microservicio | Pase a producción de ms-demo-comisiones v2.0.1 |
| MIC-05 | microservicio | Pase a producción de ms-demo-beneficiarios v1.5.0 |
| AZ-01 | azure | Configurar escalado de ca-demo-transferencias |
| AZ-02 | azure | Configurar telemetría de ms-demo-saldos en Application Insights |
| AZ-03 | azure | Configurar cola de notificaciones en Azure Service Bus |
| AZ-04 | azure | Activar configuración asíncrona de notificaciones en Azure App Configuration |
| AZ-05 | azure | Configurar referencias de secretos de ms-demo-beneficiarios con Azure Key Vault |
| RED-01 | red | Habilitar acceso de transferencias a SQL privado |
| RED-02 | red | Habilitar acceso de beneficiarios a Key Vault privado |
| RED-03 | red | Habilitar acceso de notificaciones a Service Bus privado |
| RED-04 | red | Habilitar acceso de transferencias a API interna de riesgo |
| RED-05 | red | Habilitar consultas al resolvedor DNS de demostración |
| ID-01 | identidad | Crear service principal de despliegue de transferencias |
| ID-02 | identidad | Crear service principal de lectura de secretos de beneficiarios |
| ID-03 | identidad | Crear service principal emisor de notificaciones |
| ID-04 | identidad | Crear service principal de carga de archivos sintéticos |
| ID-05 | identidad | Crear service principal consumidor de API interna de riesgo |

## Contenido enviado en cada descripción

### MIC-01: [DEMO][MIC-01] Pase a producción de ms-demo-transferencias v1.3.1

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-microservicio, ejemplo-mic-01.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: MIC-01.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Desarrollo y DevOps.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Evitar solicitudes duplicadas mediante una clave de idempotencia.

## Alcance técnico
Microservicio ms-demo-transferencias; versión actual 1.3.0; versión objetivo 1.3.1. Repositorio https://git.example/ocd/ms-demo-transferencias; artefacto acr-demo.example/ms-demo-transferencias:1.3.1.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 1.3.0 → 1.3.1; incorporar idempotencia.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Repetir una solicitud sintética con la misma clave y comprobar que conserva el mismo identificador de operación.

## Reversión
Volver al artefacto 1.3.0 y comprobar la operación básica.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### MIC-02: [DEMO][MIC-02] Pase a producción de ms-demo-saldos v1.2.0

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-microservicio, ejemplo-mic-02.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: MIC-02.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Desarrollo y DevOps.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir la consulta de varias cuentas sintéticas en una única solicitud.

## Alcance técnico
Microservicio ms-demo-saldos; versión actual 1.1.0; versión objetivo 1.2.0. Repositorio https://git.example/ocd/ms-demo-saldos; artefacto acr-demo.example/ms-demo-saldos:1.2.0.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 1.1.0 → 1.2.0; consulta de múltiples cuentas.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Consultar cuentas sintéticas existentes e inexistentes y comprobar respuestas separadas, sin mezclar titulares ficticios.

## Reversión
Volver al artefacto 1.1.0 y comprobar la consulta individual.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### MIC-03: [DEMO][MIC-03] Pase a producción de ms-demo-notificaciones v1.0.0

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-microservicio, ejemplo-mic-03.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: MIC-03.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Desarrollo y DevOps.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Procesar notificaciones ficticias de forma asíncrona.

## Alcance técnico
Microservicio ms-demo-notificaciones; versión actual 0.9.0; versión objetivo 1.0.0. Repositorio https://git.example/ocd/ms-demo-notificaciones; artefacto acr-demo.example/ms-demo-notificaciones:1.0.0.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 0.9.0 → 1.0.0; procesamiento asíncrono.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Enviar un evento ficticio, comprobar su recepción y simular un reintento controlado sin duplicar el efecto.

## Reversión
Pausar el consumidor nuevo, conservar mensajes pendientes y volver al artefacto 0.9.0.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### MIC-04: [DEMO][MIC-04] Pase a producción de ms-demo-comisiones v2.0.1

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-microservicio, ejemplo-mic-04.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: MIC-04.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Desarrollo y DevOps.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Corregir el redondeo de importes conforme a la regla ficticia definida para la demo.

## Alcance técnico
Microservicio ms-demo-comisiones; versión actual 2.0.0; versión objetivo 2.0.1. Repositorio https://git.example/ocd/ms-demo-comisiones; artefacto acr-demo.example/ms-demo-comisiones:2.0.1.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 2.0.0 → 2.0.1; corrección de redondeos.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Ejecutar casos sintéticos de cero, límites y decimales contra resultados esperados de la regla de demo.

## Reversión
Volver al artefacto 2.0.0 y ejecutar las comprobaciones de regresión previstas.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### MIC-05: [DEMO][MIC-05] Pase a producción de ms-demo-beneficiarios v1.5.0

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-microservicio, ejemplo-mic-05.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: MIC-05.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Desarrollo y DevOps.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Agregar búsqueda paginada sobre beneficiarios ficticios.

## Alcance técnico
Microservicio ms-demo-beneficiarios; versión actual 1.4.0; versión objetivo 1.5.0. Repositorio https://git.example/ocd/ms-demo-beneficiarios; artefacto acr-demo.example/ms-demo-beneficiarios:1.5.0.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 1.4.0 → 1.5.0; búsqueda paginada.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar primera página, última página, búsqueda vacía y conservación del orden con registros sintéticos.

## Reversión
Volver al artefacto 1.4.0 y verificar la consulta anterior.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### AZ-01: [DEMO][AZ-01] Configurar escalado de ca-demo-transferencias

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-azure, ejemplo-az-01.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: AZ-01.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Plataforma.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Ajustar las réplicas del microservicio de transferencias de demostración.

## Alcance técnico
Azure Container Apps; recurso ca-demo-transferencias; réplicas mínimas actuales 1; máximas actuales 1; mínimas propuestas 1; máximas propuestas 3.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: Container Apps: réplicas mínimas 1 y máximas 3.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Aplicar carga sintética y observar las réplicas dentro del rango configurado; retirar la carga y comprobar estabilización.

## Reversión
Restaurar el rango anterior de una réplica mínima y máxima.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### AZ-02: [DEMO][AZ-02] Configurar telemetría de ms-demo-saldos en Application Insights

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-azure, ejemplo-az-02.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: AZ-02.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Plataforma.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Registrar solicitudes y errores sintéticos con identificadores de correlación.

## Alcance técnico
Recurso Application Insights ai-demo-saldos; aplicación emisora ms-demo-saldos; configuración propuesta mediante referencia de conexión almacenada en el backend. El ticket no contiene valores de credenciales.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: Vincular ms-demo-saldos con ai-demo-saldos.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Ejecutar una solicitud correcta y un error sintético; comprobar correlación y ausencia de valores sensibles en la telemetría.

## Reversión
Restaurar la referencia de configuración anterior y comprobar que el servicio conserva su funcionamiento básico.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### AZ-03: [DEMO][AZ-03] Configurar cola de notificaciones en Azure Service Bus

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-azure, ejemplo-az-03.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: AZ-03.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Plataforma.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Definir el procesamiento controlado de notificaciones ficticias.

## Alcance técnico
Namespace sb-demo-mensajeria; cola q-demo-notificaciones; máximo de entregas actual 10 y propuesto 5. Se conserva la cola de mensajes no entregables.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: Service Bus: configurar máximo de entregas en 5.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Provocar fallos controlados de procesamiento y comprobar reintentos y traslado del mensaje a la cola de mensajes no entregables.

## Reversión
Restaurar el máximo anterior de 10 entregas y conservar los mensajes existentes.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### AZ-04: [DEMO][AZ-04] Activar configuración asíncrona de notificaciones en Azure App Configuration

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-azure, ejemplo-az-04.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: AZ-04.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Plataforma.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Habilitar el flujo asíncrono del entorno ficticio mediante una bandera de funcionalidad.

## Alcance técnico
Recurso Azure App Configuration appcfg-demo; bandera notificaciones-asincronas; estado actual desactivado; estado propuesto activado; etiqueta de configuración prod-demo.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: App Configuration: activar notificaciones-asincronas.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar la selección del flujo asíncrono al activar la bandera y del flujo anterior al desactivarla.

## Reversión
Desactivar notificaciones-asincronas y verificar el flujo previo.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### AZ-05: [DEMO][AZ-05] Configurar referencias de secretos de ms-demo-beneficiarios con Azure Key Vault

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-azure, ejemplo-az-05.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: AZ-05.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Plataforma.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Utilizar una referencia de secreto en la configuración del microservicio ficticio.

## Alcance técnico
Azure Key Vault kv-demo-beneficiarios; microservicio ms-demo-beneficiarios; nombre lógico del secreto conexion-demo. Se registran únicamente nombre y referencia, nunca su valor.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: Key Vault: utilizar referencia al secreto conexion-demo.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar resolución mediante la identidad autorizada y denegación para una identidad de prueba sin permisos.

## Reversión
Restaurar la referencia anterior y retirar únicamente la configuración agregada por este cambio.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### RED-01: [DEMO][RED-01] Habilitar acceso de transferencias a SQL privado

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-red, ejemplo-red-01.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: RED-01.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Redes.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir la conexión del servicio ficticio al endpoint privado de la base de datos.

## Alcance técnico
Origen 10.240.10.0/24, subred demo-transferencias; destino 10.240.20.10, endpoint SQL de demostración; protocolo TCP; puerto 1433; sentido de salida; regla demo-red-01.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 10.240.10.0/24 → 10.240.20.10; TCP/1433.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar conexión desde un origen permitido y bloqueo desde una subred de prueba excluida.

## Reversión
Retirar únicamente la regla demo-red-01 y restaurar la configuración anterior.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### RED-02: [DEMO][RED-02] Habilitar acceso de beneficiarios a Key Vault privado

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-red, ejemplo-red-02.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: RED-02.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Redes.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir tráfico HTTPS hacia el endpoint privado del almacén ficticio.

## Alcance técnico
Origen 10.240.11.0/24, subred demo-beneficiarios; destino 10.240.20.20, endpoint Key Vault de demostración; protocolo TCP; puerto 443; sentido de salida; regla demo-red-02.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 10.240.11.0/24 → 10.240.20.20; TCP/443.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar conectividad HTTPS desde el origen permitido. La autorización al secreto se comprueba por separado.

## Reversión
Retirar únicamente la regla demo-red-02 y restaurar la configuración anterior.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### RED-03: [DEMO][RED-03] Habilitar acceso de notificaciones a Service Bus privado

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-red, ejemplo-red-03.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: RED-03.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Redes.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir mensajería cifrada hacia el endpoint privado del servicio ficticio.

## Alcance técnico
Origen 10.240.12.0/24, subred demo-notificaciones; destino 10.240.20.30, endpoint Service Bus de demostración; protocolo TCP; puerto 5671; sentido de salida; regla demo-red-03.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 10.240.12.0/24 → 10.240.20.30; TCP/5671.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar establecimiento de conexión y envío de un mensaje sintético usando una identidad de prueba autorizada.

## Reversión
Retirar únicamente la regla demo-red-03 y conservar los mensajes del servicio.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### RED-04: [DEMO][RED-04] Habilitar acceso de transferencias a API interna de riesgo

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-red, ejemplo-red-04.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: RED-04.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Redes.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir consultas ficticias a una API interna de demostración.

## Alcance técnico
Origen 10.240.10.0/24, subred demo-transferencias; destino 10.240.30.10, api-riesgo.demo.example; protocolo TCP; puerto 443; sentido de salida; regla demo-red-04.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 10.240.10.0/24 → 10.240.30.10; TCP/443.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar resolución del nombre y conectividad HTTPS. Verificar la autorización de la API en una prueba separada.

## Reversión
Retirar únicamente la regla demo-red-04 y restaurar la configuración anterior.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### RED-05: [DEMO][RED-05] Habilitar consultas al resolvedor DNS de demostración

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-red, ejemplo-red-05.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: RED-05.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Redes.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Resolver los nombres privados usados por el escenario ficticio.

## Alcance técnico
Origen 10.240.10.0/24; destino 10.240.0.4, resolvedor DNS de demostración; protocolos UDP y TCP; puerto 53; sentido de salida; reglas demo-red-05-udp y demo-red-05-tcp; zona demo.example.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: 10.240.10.0/24 → 10.240.0.4; UDP y TCP/53.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Consultar api-riesgo.demo.example por el resolvedor previsto y comprobar consultas DNS mediante UDP y TCP.

## Reversión
Retirar únicamente las dos reglas agregadas y restaurar la configuración DNS previa.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### ID-01: [DEMO][ID-01] Crear service principal de despliegue de transferencias

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-identidad, ejemplo-id-01.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: ID-01.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Identidades.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Autenticar el pipeline ficticio y autorizar cambios únicamente sobre la aplicación objetivo.

## Alcance técnico
Microsoft Entra ID; tenant TENANT-DEMO; nombre solicitado sp-demo-deploy-transferencias; consumidor GitHub Actions del repositorio demo/ms-demo-transferencias; autenticación OIDC federada restringida al ambiente prod-demo; rol Azure RBAC Contributor sobre el recurso ca-demo-transferencias, sin alcance de suscripción.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: sp-demo-deploy-transferencias; Contributor sobre ca-demo-transferencias.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Obtener un token mediante la federación prevista; comprobar despliegue en la aplicación objetivo y rechazo fuera del recurso autorizado.

## Reversión
Revocar la asignación y la credencial federada agregadas; retirar la identidad nueva si no tiene dependencias.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### ID-02: [DEMO][ID-02] Crear service principal de lectura de secretos de beneficiarios

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-identidad, ejemplo-id-02.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: ID-02.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Identidades.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Autenticar el microservicio ficticio y permitir lectura en su almacén de secretos.

## Alcance técnico
Microsoft Entra ID; tenant TENANT-DEMO; nombre solicitado sp-demo-lector-beneficiarios; consumidor ms-demo-beneficiarios; autenticación mediante certificado, registrando solo su referencia; rol Azure RBAC Key Vault Secrets User sobre kv-demo-beneficiarios.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: sp-demo-lector-beneficiarios; Key Vault Secrets User sobre kv-demo-beneficiarios.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar lectura del secreto sintético permitido y denegación sobre otro almacén de demostración.

## Reversión
Revocar la asignación y la credencial agregadas; retirar la identidad nueva si no tiene dependencias.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### ID-03: [DEMO][ID-03] Crear service principal emisor de notificaciones

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-identidad, ejemplo-id-03.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: ID-03.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Identidades.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Permitir al productor ficticio enviar mensajes a una cola específica.

## Alcance técnico
Microsoft Entra ID; tenant TENANT-DEMO; nombre solicitado sp-demo-emisor-notificaciones; consumidor ms-demo-productor-notificaciones; autenticación mediante certificado, registrando solo su referencia; rol Azure Service Bus Data Sender sobre sb-demo-mensajeria/q-demo-notificaciones.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: sp-demo-emisor-notificaciones; Azure Service Bus Data Sender sobre q-demo-notificaciones.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar envío de un mensaje ficticio y denegación de recepción o administración con la misma identidad.

## Reversión
Revocar la asignación y la credencial agregadas; retirar la identidad nueva si no tiene dependencias.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### ID-04: [DEMO][ID-04] Crear service principal de carga de archivos sintéticos

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-identidad, ejemplo-id-04.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: ID-04.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Identidades.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Autorizar al proceso ficticio a trabajar únicamente en su contenedor de archivos.

## Alcance técnico
Microsoft Entra ID; tenant TENANT-DEMO; nombre solicitado sp-demo-carga-archivos; consumidor pipeline demo/carga-archivos; autenticación OIDC federada restringida al repositorio y ambiente de demostración; rol Storage Blob Data Contributor sobre el contenedor demo-entradas de stocddemo.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: sp-demo-carga-archivos; Storage Blob Data Contributor sobre demo-entradas.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar carga y lectura de un archivo ficticio y denegación sobre otro contenedor.

## Reversión
Revocar la asignación y la credencial federada agregadas; retirar la identidad nueva si no tiene dependencias.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

### ID-05: [DEMO][ID-05] Crear service principal consumidor de API interna de riesgo

**Proyecto:** SCRUM. **Tipo:** Tarea.

**Etiquetas:** ocd-demo, datos-sinteticos, caso-identidad, ejemplo-id-05.

## Naturaleza del ticket
Ejemplo OCD para el MVP del hackatón. Todos los nombres, recursos, direcciones y procedimientos son sintéticos.

## Datos generales
- Identificador de borrador: ID-05.
- Etapa: Solicitud de certificación previa al pase a producción.
- Ambientes: Producción de demostración (prod-demo). Validar previamente en certificación con recursos equivalentes de cert-demo.
- Responsable funcional ficticio: Equipo Demo de Identidades.
- Suscripción de referencia: SUB-OCD-DEMO.
- Grupo de recursos de referencia: rg-ocd-demo-prod.
- Región de referencia: East US.
- Ventana referencial: 20/11/2026, 22:00–23:00, America/Lima. Ventana ficticia de cada ejemplo independiente; no agendada.
- Impacto previsto: Posible interrupción del componente ficticio afectado durante el cambio; no representa una operación real.

## Objetivo
Autenticar al microservicio ficticio ante una API y autorizar una operación de consulta.

## Alcance técnico
Microsoft Entra ID; tenant TENANT-DEMO; nombre solicitado sp-demo-consumidor-riesgo; consumidor ms-demo-transferencias; API destino api-riesgo.demo.example; autenticación client credentials mediante certificado; permiso de aplicación/app role Riesgo.Consultar definido para la API ficticia. No es un rol Azure RBAC.
Los identificadores definitivos de recursos e identidades se completarían en una solicitud real. Los valores de este ejemplo no acreditan su existencia.

## Plan de ejecución propuesto
1. Registrar la configuración anterior y comprobar las dependencias del componente.
2. Validar el cambio en cert-demo con los recursos equivalentes.
3. Aplicar el cambio solicitado al componente ficticio de prod-demo: sp-demo-consumidor-riesgo; app role Riesgo.Consultar en api-riesgo.demo.example.
4. Ejecutar las comprobaciones previstas y registrar sus resultados.
5. Revertir el cambio si las comprobaciones no cumplen los criterios previstos.

## Comprobaciones previstas
Comprobar audiencia y rol del token; obtener respuesta permitida para consulta y denegación para operaciones sin autorización.

## Reversión
Revocar la asignación del app role y la credencial agregadas; retirar la identidad nueva si no tiene dependencias.

## Evidencias y estado de validación
Pendiente de ejecución. Las pruebas descritas son criterios previstos, no evidencias de pruebas realizadas.
La aprobación de certificación y los enlaces de evidencia permanecen pendientes. Este ticket no demuestra conectividad ni permisos efectivos.

## Datos de demostración
Los nombres de equipos describen roles ficticios. El borrador no asigna una persona de Jira.
Los dominios .example y las direcciones privadas representan infraestructura ficticia.
TENANT-DEMO y SUB-OCD-DEMO son marcadores; no son identificadores reales.

---

