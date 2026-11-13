# Casos de regresión de ESTE — v0.1

Úsalos como comprobación manual al cambiar reglas o el prompt de la skill.
Modo esperado: Strict.

| ID   | Entrada (fragmento)                                | Debe corregir             | Debe conservar              |
| ---- | -------------------------------------------------- | ------------------------- | --------------------------- |
| T001 | `Se procede a reiniciar el servicio.`              | ESTE-009 actor explícito  | acción = reiniciar servicio |
| T002 | `realiza la verificación del estado`               | ESTE-004 verbo            | verificar estado            |
| T003 | `puede haber fallado`                              | no convertir en `falló`   | matiz ESTE-005              |
| T004 | `fallando generando un timeout`                    | ESTE-010                  | ambas ideas                 |
| T005 | `usuario` y luego `cliente` mismo actor            | ESTE-001                  | un solo término             |
| T006 | `usuario actual` (= current user)                  | ESTE-016                  | referente = este usuario    |
| T007 | `eventualmente se reinicia` (= sometimes/possibly) | no leer como _eventually_ | modalidad                   |
| T008 | instrucción + condición en 40 palabras             | ESTE-006 / ESTE-003       | condición intacta           |
| T009 | `Pulse` mezclado con `pulsa`                       | ESTE-017                  | una forma de trato          |
| T010 | causa no dicha en el origen                        | ESTE-025                  | no inventar causa           |

## Criterios de OK

- El texto reescrito conserva todos los hechos y matices de duda del original
- Las reglas nombradas en una tabla antes/después coinciden con las infracciones corregidas
- No se introducen adjetivos de marketing
- La salida por defecto es solo el texto reescrito
