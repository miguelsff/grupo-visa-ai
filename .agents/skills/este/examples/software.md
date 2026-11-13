# Ejemplos de documentación de software

## Instalación en README

**Antes**

> Para llevar a cabo la instalación del paquete será necesario realizar la ejecución del comando de instalación de dependencias y, posteriormente, proceder con el build.

**Después**

> 1. Instala las dependencias.
> 2. Ejecuta el build.

## Nota de API

**Antes**

> Si se envía un payload inválido el endpoint podrá eventualmente responder con un error 400 indicando que algo ha ido mal con los datos.

**Después**

> Si el payload no es válido, el endpoint responde `400`. El cuerpo del error describe el campo incorrecto.
