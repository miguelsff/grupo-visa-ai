# Patrones propios del español para ESTE

La claridad estructural no basta en español. Estos patrones crean doble
lectura incluso en oraciones cortas.

## 1. _Se_ impersonal y pasivo

El _se_ español puede ser impersonal, pasivo o reflexivo. En instrucciones,
esa ambigüedad oculta al actor.

| Prefiere                            | Evita cuando el actor importa                                          |
| ----------------------------------- | ---------------------------------------------------------------------- |
| `El operador reinicia el servicio.` | `Se reinicia el servicio.`                                             |
| `El sistema guarda el archivo.`     | `Se guarda el archivo.`                                                |
| `Ocurrió un error de red.`          | `Se ha producido un error de red.` (aceptable si el foco es el evento) |

Regla: ESTE-009.

## 2. Gerundio de consecuencia

En español técnico, a menudo se cuelga un gerundio con sentido de resultado:

- Mal: `El job termina generando un informe.`
- Lecturas: modo durante el cierre, o resultado tras el cierre.

Corrección:

- `El job termina y genera un informe.`
- `El job termina. Entonces genera un informe.`

Regla: ESTE-010.

## 3. Falsos amigos

| Palabra         | Lectura arriesgada          | Prefiere                                    |
| --------------- | --------------------------- | ------------------------------------------- |
| `actual`        | inglés _current_            | `este`, `vigente`, `en sesión`              |
| `eventualmente` | inglés _eventually_         | `al final`, `a veces`, `en algún caso`      |
| `soportar`      | support / withstand / allow | `ser compatible con`, `admitir`, `resistir` |
| `realizar`      | do/perform (vago)           | verbo concreto                              |
| `aplicar`       | apply patch vs solicitar    | nombra el objeto                            |

Regla: ESTE-016.

## 4. Formalismos vacíos

Elimina o sustituye:

- `se procede a`
- `llevar a cabo`
- `es importante señalar que`
- `cabe destacar que`
- `de cara a`
- `a la hora de`
- `en base a` → `según` / `a partir de`

## 5. Niebla de pronombres / determinantes

`dicho`, `referido`, `el mismo`, `la mencionada` obligan a buscar hacia atrás.

Prefiere repetir el sustantivo: `el servicio`, `el token`, `el usuario`.

## 6. Cambio de trato

Instrucciones que mezclan `tú`, `usted` e impersonal parecen distintos
hablantes. Elige uno (ESTE-017).

## 7. Anglicismos

Conserva términos ingleses de dominio si el glosario del equipo ya los fijó
(`commit`, `endpoint`, `webhook`). Si no, prefiere español compartido
(`desplegar`, `versión`, `solicitud`).

No mezcles ambas formas para un mismo concepto en el mismo documento
(ESTE-001, ESTE-014).
