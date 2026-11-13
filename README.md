# Grupo VISA AI

Base local del asistente para preparar tickets OCD.

La etapa 1 conecta Next.js, FastAPI, Pydantic y SQLite mediante un «Hola mundo» persistente.
También carga cinco documentos locales y permite buscarlos mediante FTS5.

## Ejecutar con Docker Compose

Requisito: Docker Desktop iniciado con contenedores Linux y Docker Compose disponible.
La primera compilación necesita Internet para descargar imágenes y dependencias.
La etapa 1 funciona sin credenciales de OpenAI o Atlassian.

Desde la raíz del repositorio:

```powershell
docker compose up --build -d --wait
```

Abre [la aplicación local](http://localhost:8000).
La documentación de la API está en [Swagger UI](http://localhost:8000/docs).

Para cambiar el puerto, copia `.env.example` a `.env` y ajusta `APP_PORT`.
Las variables de integraciones externas se reservan para las siguientes etapas.
La interfaz muestra su configuración como pendiente o por verificar.

```powershell
docker compose ps
docker compose logs -f app
docker compose down
```

`docker compose down` conserva el volumen `sqlite_data` y los saludos guardados.

## Comprobar la etapa 1

1. Comprueba que los tres componentes muestran «Disponible».
2. Escribe un nombre y pulsa «Enviar saludo».
3. Comprueba la respuesta y el saludo guardado.
4. Busca «microservicios» en los modelos operativos.
5. Recrea el contenedor y comprueba que el saludo continúa disponible.

```powershell
docker compose up -d --force-recreate --wait
```

Ejecuta las pruebas de integración en un contenedor independiente:

```powershell
docker compose --profile test run --build --rm tests
```

Las pruebas usan una base temporal. No modifican el volumen de la aplicación.

## Componentes

| Componente | Implementación de la etapa 1 |
|---|---|
| Frontend | Next.js App Router, React, TypeScript y CSS Modules. Exportación estática. |
| Backend | FastAPI y Uvicorn. API JSON y distribución del frontend. |
| Validación | Pydantic valida el nombre antes de guardarlo. |
| Persistencia | SQLite en el volumen Docker `sqlite_data`. |
| Conocimiento | Cinco copias documentales del repositorio, cargadas al arrancar. Búsqueda FTS5. |
| Caso de uso | Saludo local reproducible, separado en el módulo `agent`. |
| Integraciones | Configuración de OpenAI, Jira y Confluence. Conexiones pendientes. |

Docker compila Next.js y copia su exportación en la imagen Python.
Durante la ejecución existe un servicio `app`, publicado únicamente en `127.0.0.1`.
SQLite funciona dentro del proceso Python y no necesita un servidor independiente.
El puerto interno escucha en `0.0.0.0` para recibir el tráfico publicado por Docker.

La etapa 1 utiliza un saludo determinista. No ejecuta inferencias ni crea tickets Jira.
El SDK de OpenAI y HTTPX están instalados para las siguientes integraciones.

## Estructura

```text
grupo-visa-ai/
├── compose.yaml
├── Dockerfile
├── .env.example
├── frontend/
│   ├── app/                 # Pantalla y estilos
│   ├── lib/                 # Contratos y cliente de la API
│   ├── package.json
│   └── package-lock.json
├── backend/
│   ├── app/
│   │   ├── agent/           # Casos de uso; futura orquestación
│   │   ├── integrations/    # Estado de configuración externa
│   │   ├── knowledge/       # Carga de documentos locales
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── requirements-dev.txt
└── docs/
    ├── MVP_OCD_Arquitectura.md
    └── modelos_operativos/
```

## API de la etapa 1

| Método y ruta | Resultado |
|---|---|
| `GET /api/health` | Estado local, búsqueda FTS5 y cantidades de documentos y saludos. |
| `GET /api/hello` | Mensaje del backend y los últimos cinco saludos. |
| `POST /api/hello` | Valida y guarda un saludo. Cuerpo: `{"name": "Equipo VISA"}`. |
| `GET /api/knowledge?q=microservicios` | Documentos con código, versión, fuente y fragmento. |
| `GET /api/integrations` | Presencia de configuración; no acredita conexión ni expone credenciales. |

## Desarrollo

Las dependencias están fijadas en los archivos de bloqueo.
El Dockerfile comprueba TypeScript antes de compilar el frontend.

La compilación utiliza Python 3.14 y Node.js 24 dentro de Docker.
Después de cambiar el código, ejecuta de nuevo `docker compose up --build -d --wait`.

Para actualizar los bloqueos Python con `uv`, ejecuta desde `backend`:

```powershell
uv pip compile pyproject.toml --python-version 3.14 --universal --output-file requirements.txt
uv pip compile pyproject.toml --extra dev --python-version 3.14 --universal --output-file requirements-dev.txt
```

Consulta el [diseño de la solución](docs/MVP_OCD_Arquitectura.md) para las siguientes etapas.

## Verificación realizada

Comprobaciones del 13 de noviembre de 2026:

- Compilación de Next.js y comprobación TypeScript correctas dentro de Docker.
- Servicio `app` saludable después de ejecutar el comando de arranque documentado.
- Frontend y nueve recursos estáticos con respuesta HTTP 200.
- Saludo guardado y recuperado después de recrear el contenedor.
- Cinco documentos locales cargados; búsqueda de microservicios con fuente y versión.
- Tres pruebas de integración aprobadas dentro de Docker con Python 3.14.
- Revisión de estilo Python aprobada mediante Ruff.

La revisión visual quedó pendiente porque Computer Use no pudo verificar la URL de Chrome.
Las llamadas reales a OpenAI, Jira y Confluence corresponden a las siguientes etapas.
