# Corpus de pruebas del consumidor

`points.json` contiene los 83 registros producidos por `ocd_ingesta.content.collect`
con los snapshots HTML de `ingesta/tests/fixtures/`, run sintético `a` repetido
32 veces y fecha `2026-11-13T12:00:00Z`. No se obtienen de un índice manual distinto.
Los snapshots y sus sobres adaptados se describen en el README de fixtures de ingesta.

T4 corrigió las firmas de las veinte reglas específicas: `applies_when` conserva
la sección y el resultado condicional completo de T2, según el contrato v1.
Las seis reglas comunes mantienen `Siempre`. Los campos y modelos conservan
los nombres publicados por la CLI. Los vectores de las pruebas son sintéticos.

La aceptación integrada no depende de este archivo: ejecuta la CLI, recorre Qdrant
y compara las referencias devueltas con los puntos realmente publicados.
