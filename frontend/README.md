# Interfaz NexoOPS

La interfaz permite consultar procedimientos y preparar un borrador OCD con sus
fuentes, preguntas y validaciones. Conserva un borrador real por sesión del
navegador y recupera su última revisión al recargar.

Los tickets de ejemplo, la agenda y la vista previa son demostraciones. El agente
no crea tickets, reserva recursos ni ejecuta infraestructura.

La imagen Docker utiliza Node.js 24 para compilar TypeScript y exportar Next.js.
FastAPI distribuye el directorio `out`; Node.js no interviene en la ejecución.
Los componentes usan CSS Modules y el cliente HTTP centralizado en `lib/api.ts`.

Para verificar con dependencias locales, desde `frontend/`:

```powershell
npm ci
npm run typecheck
npm run build
```

Para ejecutar la aplicación completa, utiliza Docker Compose según el
[README principal](../README.md). La [conexión con FastAPI](BACKEND.md) describe
las rutas y la autenticación.
