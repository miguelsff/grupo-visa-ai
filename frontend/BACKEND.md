# Conexión de chat

Crear .env.local en front (ignorado por Git):

    OCD_API_URL=https://app-production-b27a3c5e.up.railway.app
    OCD_DEMO_USERNAME=demo
    OCD_DEMO_PASSWORD=

Completar la contraseña y reiniciar Next.js. Nunca usar NEXT_PUBLIC para estas credenciales.
El navegador envía message y conversationId al proxy /api/chat. El proxy envía únicamente message al backend y mantiene una cookie HttpOnly por conversación para ocd_session.
Las respuestas incluyen answer, questions, draft, sources, validations, revision, status y error. reviewed indica revisión ejecutada, no aprobación del pase.
La integración autenticada debe verificarse cuando estén disponibles las credenciales.
