# Ejemplos de mensajes de error

## Fallo ambiguo

**Antes**

> Se ha producido un error inesperado durante el procesamiento de su solicitud debido a un posible problema con el formato de los datos o con la versión del cliente.

**Después**

> La solicitud falló. El formato de los datos no coincide con el esperado. Comprueba la versión del cliente.

Se mantiene: no inventar cuál de las dos causas es la real si ambas están en el origen. Si el origen no prioriza, no priorices tú.

## Mejor cuando las causas son alternativas

**Antes** (misma intención, ESTE más claro)

> La solicitud falló. Causas posibles: formato de datos incorrecto, o cliente desactualizado.

## Timeout

**Antes**

> El servicio no ha podido completar la operación en el tiempo esperado generando un timeout.

**Después**

> El servicio no completó la operación a tiempo. Ocurrió un timeout.
