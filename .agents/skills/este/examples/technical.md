# Ejemplos de documentación técnica

## Paso de runbook

**Antes**

> A continuación se deberá proceder, una vez comprobado que el nodo se encuentra en estado healthy, a la rotación del certificado, teniendo en cuenta que el servicio podría verse afectado durante el proceso.

**Después**

> 1. Verifica que el nodo está en estado `healthy`.
> 2. Rota el certificado.
> 3. Ten en cuenta: el servicio puede interrumpirse durante la rotación.

## Nota de arquitectura (ESTE-flavored)

**Antes**

> El componente de orquestación es responsable de llevar a cabo la coordinación de los distintos workers involucrados en el procesamiento de los jobs entrantes.

**Después**

> El orquestador coordina los workers que procesan los jobs entrantes.
