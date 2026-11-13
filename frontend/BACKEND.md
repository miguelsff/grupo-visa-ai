# Conexión del frontend con FastAPI

Next.js exporta archivos estáticos. FastAPI los distribuye desde el mismo origen
que `/api`. El navegador usa el cliente de `lib/api.ts` y conserva la cookie
`ocd_session`. No hay un proxy ni un proceso Next.js durante la ejecución.

`POST /api/chat` recibe únicamente `message`. La respuesta incluye `answer`,
`questions`, `draft`, `sources`, `validations`, `revision`, `status` y `error`.
`GET /api/chat` recupera la última revisión de la misma sesión.

La aplicación mantiene una conversación real por sesión. Los ejemplos de tickets
son vistas de demostración y no cambian el borrador. `reviewed` indica una revisión
documental, no una autorización ni la ejecución del pase.

Las credenciales se configuran en el backend. En Railway, el navegador autentica
al usuario `demo` mediante HTTP Basic. No crear `.env.local` con credenciales ni
publicar valores sensibles mediante `NEXT_PUBLIC_*`.
