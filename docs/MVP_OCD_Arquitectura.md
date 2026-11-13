# MVP OCD — arquitectura básica

Fecha: 13 de noviembre de 2026. Versión: 0.4. Estado: Railway y SQLite seleccionados; despliegue pendiente.

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
| DEC-03 | Desplegar la demostración en Railway. Conservar la ejecución local para desarrollo y respaldo de la presentación. | Confirmado; sustituye el destino local de la versión 0.3 | Usuario, 13 de noviembre de 2026 |
| RES-02 | El equipo conoce Next.js y Python. | Confirmado | Usuario, 13 de noviembre de 2026 |
| DEC-04 | Usar Next.js App Router y TypeScript para el frontend; Python y FastAPI para el backend. | Confirmado | Aceptación del usuario, 13 de noviembre de 2026 |
| DEC-05 | Exportar el frontend estático y servirlo desde FastAPI durante la demostración. | Confirmado | Aceptación de la solución; DEC-03; S8, S10 |
| RES-03 | Conservar Docker Compose para ejecutar y comprobar la solución localmente. Railway construye el Dockerfile del mismo repositorio. | Confirmado para ejecución local; adaptado a DEC-03 | Usuario; S15 |
| RF-05 | Crear primero la estructura y un «Hola mundo» con los componentes locales conectados. | Confirmado | Usuario, 13 de noviembre de 2026 |
| DEC-06 | Mantener SQLite y FTS5. Guardar la base en `/data/ocd.sqlite3`, dentro de un volumen persistente de Railway. | Confirmado | Usuario; S14 |
| DEC-07 | Ejecutar un servicio Railway, una réplica y un worker Uvicorn. | Diseño del MVP | DEC-03, DEC-06 |
| DEC-08 | Empezar con la prueba gratuita si la cuenta tiene acceso completo a las API externas. | Propuesto; elegibilidad pendiente | Prioridad de costo mínimo; S18 |
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

| Componente | Responsabilidad | Tecnología seleccionada |
|---|---|---|
| Frontend | Chat, borrador del OCD, verificaciones, fuentes y enlace del ticket creado. | Next.js App Router, React, TypeScript y CSS Modules; una pantalla. |
| Backend | Servir la exportación del frontend, conservar la sesión y coordinar los módulos. | Python, FastAPI y Uvicorn; un worker en el servicio Railway. |
| Esquema y reglas | Definir el borrador estructurado y ejecutar las verificaciones condicionales. | Pydantic y reglas Python. |
| Agente | Interpretar el cambio, consultar conocimiento, solicitar datos y seleccionar herramientas. | SDK oficial de OpenAI, Responses API y `gpt-6-luna`. |
| Cargador | Leer tickets y páginas seleccionados antes de la demo. Conservar su origen y versión. | Módulo invocado mediante un comando manual. |
| Conector Atlassian | Leer Jira/Confluence y crear tickets. | HTTPX y API REST con token guardado en el backend. |
| Base de conocimiento | Guardar documentos, borradores y operaciones de creación. | SQLite + FTS5 en `/data/ocd.sqlite3`; volumen persistente del servicio. |
| Pruebas | Verificar reglas, conservación del borrador y creación sin duplicados. | pytest; los tres casos de aceptación del MVP. |

El agente, el cargador, las reglas y el conector son módulos del mismo backend.
El cargador mantiene una responsabilidad separada y comparte el conector con el agente.
Next.js permite exportar HTML, CSS y JavaScript estáticos mediante `output: 'export'` [S10].
FastAPI sirve esos archivos durante la demo [S8]. La separación de módulos evita desplegar servicios adicionales.
El conocimiento del equipo justifica usar Next.js para construir y mantener la interfaz.
La exportación mantiene la lógica de negocio y las integraciones en Python.

### Ejecución local con Docker Compose

| Etapa | Ejecución | Comunicación |
|---|---|---|
| Compilación | Docker construye Next.js y comprueba TypeScript en una etapa Node.js. | La carpeta `out` se copia a la imagen Python. |
| Ejecución | `docker compose up --build -d --wait` inicia el servicio `app`. | Uvicorn sirve la interfaz y `/api` desde `localhost:8000`. |
| Persistencia | El volumen `sqlite_data` se monta en `/data`. | SQLite conserva datos al recrear el contenedor. |
| Pruebas | El perfil `test` ejecuta pytest en un contenedor independiente. | Utiliza bases temporales y no monta el volumen de la aplicación. |

El chat usa componentes de cliente para manejar mensajes, formularios y estados [S11].
La compilación no consulta Jira, Confluence ni OpenAI; esas llamadas ocurren en el backend durante el uso.
Las rutas de API se registran antes de montar los archivos estáticos en la raíz.
Compose publica el puerto únicamente en `127.0.0.1`. Uvicorn escucha en `0.0.0.0` dentro del contenedor.
La primera compilación necesita Internet para obtener imágenes y dependencias.
La etapa 1 funciona sin conexión externa después de construir la imagen.
El MVP completo necesitará Internet para OpenAI y para crear tickets en Jira.

El compromiso de la exportación es prescindir de Server Actions y renderizado dinámico del servidor Next.js [S10].
Si una función futura necesita esas capacidades, se revisará DEC-05 y se añadirá un proceso Node.js.
CSS Modules permite mantener los estilos por componente [S12].
FTS5 realiza búsqueda textual [S13]; la evaluación comprobará consultas con vocabulario distinto y referencias recuperadas.
Los archivos `package-lock.json` y `requirements.txt` fijan las dependencias de la primera etapa.

### Despliegue del MVP en Railway

Railway aloja un servicio `app`, construido desde el Dockerfile del repositorio [S15].
La etapa Node.js compila Next.js. La imagen final contiene Python y la exportación en `/app/static`.
FastAPI sirve la interfaz y `/api` desde el mismo dominio HTTPS de Railway [S16].
El navegador ejecuta la interfaz. Las llamadas a OpenAI y Atlassian salen únicamente del backend.
SQLite funciona dentro del proceso Python. El archivo persistente reside en el volumen, separado de la imagen.

| Elemento | Configuración objetivo del MVP | Motivo |
|---|---|---|
| Fuente y compilación | Raíz del repositorio; `Dockerfile`; imagen final `runtime`. | Reutilizar la compilación local. |
| Aplicación | Un servicio `app`, una réplica y `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`. | Mantener una sola instancia con acceso a SQLite. |
| Puerto | Variable Railway `PORT=8000`; puerto de destino público `8000`. | Coincidir con el puerto fijo del Dockerfile actual y con el healthcheck [S17]. |
| Acceso | Dominio generado por Railway con HTTPS; autenticación de demostración en el backend. | Compartir el MVP con los participantes autorizados. |
| Volumen | Montaje en `/data`; capacidad inicial de 0.5 GB para Trial/Free [S19]. | Conservar conocimiento, borradores y registros de creación. |
| Base de datos | `DATABASE_PATH=/data/ocd.sqlite3`. | Evitar escribir la base en el sistema de archivos efímero. |
| Salud | Ruta `/api/health`; comprobar acceso a SQLite y disponibilidad de FTS5. | Detectar un arranque fallido antes de habilitar el despliegue. |
| Región | Una región disponible en la cuenta; registrar la elegida al desplegar. | Mantener aplicación y volumen juntos. |
| Suspensión por inactividad | Activar Serverless si está disponible; abrir y comprobar la aplicación antes de presentar [S20]. | Reducir consumo fuera de la demostración. |

Railway monta el volumen durante el arranque. La compilación y el comando de predespliegue no tienen acceso al volumen [S14].
La inicialización del esquema y la carga documental ocurren al arrancar, después de montar `/data`.
La inicialización conserva los registros existentes. La actualización del conocimiento no elimina borradores ni operaciones de creación.
La ingesta remota se ejecutará manualmente dentro del contenedor activo, con el mismo volumen y las mismas credenciales.
Una base creada durante la compilación no se utiliza como almacenamiento persistente.

Variables del servicio:

| Variable | Valor o finalidad | Estado |
|---|---|---|
| `PORT` | `8000`. | Configurar en Railway. |
| `DATABASE_PATH` | `/data/ocd.sqlite3`. | Utilizada por la estructura local. |
| `FRONTEND_DIR` | `/app/static`. | Utilizada por la imagen actual. |
| `KNOWLEDGE_DIR` | `/app/knowledge`. | Copias documentales incluidas en la imagen. |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Credencial del backend y modelo seleccionado. | Conexión real pendiente. |
| `ATLASSIAN_BASE_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` | Sitio y credenciales de la cuenta de demostración. | Conexión real pendiente. |
| `JIRA_PROJECT_KEY` | `SCRUM`; restringir las escrituras a este proyecto. | Aplicar al implementar el conector. |
| `DEMO_USERNAME`, `DEMO_PASSWORD` | Acceso compartido de demostración mediante HTTP Basic sobre HTTPS. | Propuesta; autenticación pendiente de implementar. |
| `RAILWAY_RUN_UID` | `0` para un entrypoint que ajuste permisos y después baje al UID `10001`. | Preparar el entrypoint antes de desplegar [S14]. |

El volumen Railway se monta como `root`; la imagen actual ejecuta la aplicación con UID `10001` [S14].
El entrypoint previsto ajusta la propiedad de `/data` y ejecuta Uvicorn como ese usuario mediante `exec`.
La aplicación falla al arrancar si no puede escribir en `/data`. No crea una base alternativa en un directorio temporal.
El Dockerfile actual necesita ese ajuste de arranque. La configuración Railway todavía no está creada ni probada.
La variable `PORT=8000` evita cambiar el puerto fijo de la imagen actual.
`APP_PORT` controla únicamente el puerto publicado por Docker Compose local.

### Persistencia, recuperación y operación

- Conservar en SQLite los borradores, las revisiones y las claves de operación antes de llamar a Jira.
- Usar transacciones cortas. Ejecutar las llamadas externas fuera de las transacciones de escritura.
- Mantener una réplica y un worker. Revisar esta decisión si aparecen bloqueos o se requiere escalar horizontalmente.
- Configurar un tiempo de espera limitado para bloqueos de SQLite y devolver un error recuperable cuando se agote.
- Si se activa WAL, conservar `ocd.sqlite3-wal` y `ocd.sqlite3-shm` en el mismo volumen [S22].
- Crear una copia consistente mediante la API de respaldo de SQLite antes de cada presentación o cambio de esquema [S21].
- Descargar esa copia fuera del volumen y comprobar su restauración en una base local temporal.
- Conservar el volumen al recrear el servicio. Exportar la base antes de eliminar recursos o terminar la prueba gratuita.
- Revertir el código a una imagen anterior compatible si falla un despliegue. La reversión del código no revierte la base.
- Antes de restaurar una copia antigua, detener escrituras y conciliar las operaciones con Jira para evitar creaciones duplicadas.

Los despliegues con volumen pueden producir una interrupción breve, incluso con healthcheck configurado [S17].
La ruta de salud no crea tickets ni llama al modelo. Su respuesta pública solo indica disponibilidad.
Railway consulta esa ruta durante el despliegue; no equivale a monitoreo continuo [S17].
Los logs salen por salida estándar e identifican fallos, duración y claves de operación sin exponer secretos.
El responsable de la demo revisa logs, espacio del volumen y crédito disponible antes de presentar.
Serverless puede retrasar la primera solicitud después de una suspensión; comprobar el arranque antes del recorrido [S20].
Los objetivos de recuperación y pérdida de datos aceptable quedan pendientes. Las copias manuales no garantizan recuperación continua.

### Primera etapa: estructura y «Hola mundo»

La primera etapa conecta el frontend, la API y SQLite mediante un saludo persistente.
Pydantic valida la entrada. El módulo `agent` coordina este caso local con una respuesta determinista.
La aplicación carga las cinco copias documentales del repositorio y permite buscarlas mediante FTS5.
La carga conserva código, título, versión y URL de cada documento; no consulta Confluence.
La interfaz muestra el estado local y distingue las integraciones pendientes de la configuración presente.
La presencia de credenciales no acredita una conexión real.

La imagen local ejecuta el backend sin privilegios de administrador. El arranque Railway debe conservar ese usuario después de preparar el volumen.
Los archivos de bloqueo fijan dependencias de frontend y backend.
El servicio incorpora una comprobación de salud sobre `/api/health`.
SQLite comparte el contenedor de la aplicación y utiliza un volumen persistente.

Aceptación de la etapa 1:

1. Iniciar la aplicación mediante Docker Compose.
2. Abrir el frontend y comprobar el estado de los componentes.
3. Enviar un nombre y recuperar el saludo guardado.
4. Buscar un modelo operativo y recuperar su fuente y versión.
5. Recrear el contenedor y comprobar que persiste el saludo.
6. Ejecutar las pruebas de integración en el perfil `test`.

Las llamadas a OpenAI, la ingesta remota y la creación Jira corresponden a las siguientes etapas.
El saludo local no representa un agente de IA funcionando.

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

- Usar HTTPS en Railway, una cuenta de demostración y contenido sintético. Conservar el acceso local en `127.0.0.1`.
- Exigir autenticación en la interfaz y las rutas de negocio. Excluir únicamente la comprobación de salud mínima.
- Vincular cada borrador a su sesión y comprobar esa relación en el backend antes de leerlo o modificarlo.
- Mantener las credenciales de OpenAI y Atlassian en variables del backend. El navegador y el contexto del modelo nunca reciben sus valores.
- Guardar secretos en Railway Variables. Excluirlos del repositorio, la imagen y las variables `NEXT_PUBLIC_*` del frontend.
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
Jira Free y Confluence Free conservan sus límites propios. El alojamiento Railway se suma al consumo de OpenAI.
El acceso a una cuenta API con el modelo habilitado queda pendiente de verificar.

### Alojamiento Railway

Precios consultados el 13 de noviembre de 2026, en USD. Región pendiente; importes sin impuestos ni conversión monetaria.

| Modalidad | Cargo y crédito | Condición para el MVP |
|---|---|---|
| Trial | USD 5 de crédito inicial; vence a los 30 días o al consumirse [S18]. | Costo de alojamiento cero mientras alcance el crédito. Verificar acceso completo a las API externas. |
| Free | USD 0 de suscripción; USD 1 de crédito mensual [S18–S19]. | Medir consumo antes de asumir que permite conservar el MVP disponible todo el mes. |
| Hobby | Mínimo USD 5/mes; incluye USD 5 de consumo [S19]. | Si el consumo supera USD 5, se paga la diferencia. |

El consumo incluye CPU, memoria, volumen y tráfico. La suspensión reduce cómputo; no elimina los cargos del almacenamiento [S19–S20].
El costo total suma Railway, la API de OpenAI y cualquier servicio que supere su plan gratuito.
La cuenta, el saldo inicial y el plan efectivo todavía no están verificados.
Railway documenta la eliminación de volúmenes Trial a los 30 días de vencer el crédito; exportar los datos antes [S18].

## 4. Plan orientativo y aceptación

Estimación para una persona con acceso a las API y contenido de demostración preparado.

| Minutos | Actividad | Responsable | Criterio de salida |
|---:|---|---|---|
| 45 | Preparar Railway, volumen y conexiones; probar lectura y creación en Jira. | Desarrollador | Aplicación accesible y un ticket real de prueba. |
| 45 | Cargar modelos operativos y ejemplos en SQLite. | Desarrollador | Fuentes consultables con sus referencias. |
| 90 | Implementar agente, esquema OCD, reglas y creación sin duplicados. | Desarrollador | Flujo completo desde un mensaje hasta un ticket. |
| 60 | Construir el chat, el borrador y los estados de verificaciones. | Desarrollador | Una pantalla operativa. |
| 60 | Desplegar en Railway, ejecutar tres casos y comprobar persistencia. | Desarrollador | Evidencias reproducibles y recorrido ensayado en la URL desplegada. |
| **300** | **Total de desarrollo.** | | **Cinco horas.** |
| 60 | Presentar el MVP. | Presentador | Hora adicional reservada por el usuario. |

La configuración inicial de Railway, Confluence y las credenciales puede consumir parte del primer bloque.
El plazo de cinco horas es una estimación original. La configuración y las comprobaciones de nube pueden exigir tiempo adicional.
Si faltan accesos, se conserva el borrador disponible y se identifica la creación real como aceptación pendiente.

| Caso | Entrada | Aceptación |
|---|---|---|
| Completo | Cambio con los datos requeridos de sus secciones activadas. | Ticket Jira real con las secciones, referencias y clave retornada. |
| Incompleto | Solicitud sin destino de red o alcance del permiso. | Preguntas precisas; faltantes visibles; borrador conservado. |
| Inconsistente | Puerto fuera de rango o ambientes incompatibles según la regla de demo. | Error reproducible; corrección conversacional; validación posterior. |

Aceptación adicional del despliegue:

1. Abrir la URL HTTPS y comprobar el frontend, la API y FTS5 con autenticación de demostración.
2. Comprobar que una solicitud anónima no accede a borradores ni crea tickets.
3. Guardar un saludo de la etapa 1 o un borrador del MVP completo y registrar su identificador.
4. Reiniciar y volver a desplegar el servicio conservando el volumen. Recuperar el mismo registro.
5. Recuperar una operación de creación tras reiniciar y comprobar que su reintento no crea otro ticket.
6. Crear una copia consistente, descargarla y restaurarla en una base temporal local.
7. Comprobar las conexiones reales a OpenAI, Jira y Confluence sin publicar sus credenciales.
8. Revisar crédito, logs y espacio del volumen antes de iniciar la presentación.

Medir tiempo manual y tiempo asistido sobre los mismos casos.
Registrar campos omitidos, interacciones necesarias y tickets duplicados. Los porcentajes de ahorro salen de estas mediciones.

Fuentes preparadas: proyecto Jira SCRUM, tipo Tarea, veinte tickets y cuatro modelos operativos publicados en Confluence DDS.
Confirmado el 13 de noviembre: el equipo conoce Next.js y Python; stack aceptado y ejecución local mediante Docker Compose.
Confirmado después: Railway será el destino del MVP y SQLite seguirá como base de datos.
La estructura y el «Hola mundo» constituyen la primera etapa de implementación.
Pendientes del MVP completo: acceso al modelo, número real de desarrolladores, agente, validaciones OCD e integraciones remotas.
Referencias de conocimiento: [modelos_operativos/README.md](modelos_operativos/README.md).
El diseño del MVP completo se implementa por etapas. El código de la primera etapa se encuentra en `frontend` y `backend`.
Las conexiones externas y la creación real de tickets todavía requieren implementación y pruebas.
Pendientes de nube: cuenta/plan, región, volumen, permisos de arranque, autenticación, configuración y aceptación en Railway.
Esta actualización define el despliegue. No acredita recursos creados ni pruebas ejecutadas en Railway.

## Fuentes

Consulta de S1–S9: 12 de noviembre de 2026. Consulta de S10–S13 y nueva consulta de S8: 13 de noviembre de 2026.
Consulta de S14–S22: 13 de noviembre de 2026. Las tarifas del modelo conservan la fecha indicada en la sección 3.

- S1: [Confluence Free y límites](https://www.atlassian.com/en/software/confluence/pricing).
- S2: [Agregar aplicaciones Atlassian al sitio existente](https://support.atlassian.com/jira-cloud-administration/docs/set-up-jira-products/).
- S3: [Autenticación de clientes privados y scripts Atlassian](https://developer.atlassian.com/developer-guide/auth/).
- S4: [Autenticación REST de Confluence](https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/).
- S5: [GPT-6 Luna: capacidades y tarifas](https://developers.openai.com/api/docs/models/gpt-6-luna).
- S6: [GPT-6.1 Sol: capacidades y tarifas](https://developers.openai.com/api/docs/models/gpt-6.1-sol).
- S7: [Identidad de aplicación y permisos de un service principal](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal).
- S8: [Archivos estáticos en FastAPI](https://fastapi.tiangolo.com/tutorial/static-files/).
- S9: [Crear tickets y consultar metadatos Jira](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/).
- S10: [Exportación estática y restricciones de Next.js](https://nextjs.org/docs/app/guides/static-exports).
- S11: [Componentes de servidor y cliente de Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components).
- S12: [CSS Modules en Next.js](https://nextjs.org/docs/app/getting-started/css#css-modules).
- S13: [Búsqueda de texto con SQLite FTS5](https://sqlite.org/fts5.html).
- S14: [Railway: volúmenes, disponibilidad y permisos](https://docs.railway.com/volumes).
- S15: [Railway: construcción desde Dockerfile](https://docs.railway.com/builds/dockerfiles).
- S16: [Railway: acceso público y HTTPS](https://docs.railway.com/networking/public-networking).
- S17: [Railway: healthchecks, puerto y despliegues con volumen](https://docs.railway.com/deployments/healthchecks).
- S18: [Railway: prueba gratuita, verificación y retención de datos](https://docs.railway.com/pricing/free-trial).
- S19: [Railway: planes, créditos y recursos](https://docs.railway.com/pricing/plans).
- S20: [Railway: suspensión Serverless y arranque](https://docs.railway.com/deployments/serverless).
- S21: [SQLite: API de respaldo consistente](https://sqlite.org/backup.html).
- S22: [SQLite: funcionamiento y archivos WAL](https://sqlite.org/wal.html).

Diagrama editable: [MVP_OCD_Arquitectura.drawio](MVP_OCD_Arquitectura.drawio).
Vistas: Contexto, Aplicaciones y Despliegue Railway.
Vista previa del despliegue: [MVP_OCD_Arquitectura.png](MVP_OCD_Arquitectura.png).
Validación documental: XML y referencias de las tres vistas comprobados; vistas renderizadas y revisadas visualmente con mxGraph.
La revisión visual no sustituye las pruebas de despliegue, persistencia ni integración en Railway.
