# Disciplina terminológica

## Objetivo

El lector no debe preguntarse si dos palabras nombran una cosa o dos.

## Flujo de trabajo

1. Lista los conceptos recurrentes del texto (actores, objetos, acciones, estados).
2. Asigna un término preferido por concepto (`spec/vocabulary.yml` + glosario del proyecto).
3. Sustituye las rotaciones de sinónimos.
4. En el primer uso de un término de dominio, defínelo si no es español común.
5. Reutiliza después la forma exacta (incluidos artículos y modificadores si forman parte del término).

## Plantilla de entrada de glosario

```markdown
**token de acceso**: clave temporal que autoriza una solicitud a la API.
```

O en proyectos con YAML:

```yaml
- id: token_acceso
  term: token de acceso
  definition: Clave temporal que autoriza una solicitud a la API.
  avoid: [token, access token, clave]
```

## Resolución de conflictos

| Conflicto                                        | Resolución                                          |
| ------------------------------------------------ | --------------------------------------------------- |
| Glosario del proyecto vs vocabulario ESTE        | Gana el glosario del proyecto en ese repo           |
| Etiqueta de UI vs término de docs                | Alinea docs a la etiqueta publicada, o cambia ambos |
| Término inglés de dominio vs equivalente español | Elige uno; documéntalo; no alternes                 |

## Reglas relacionadas

- ESTE-001 Un concepto, un término
- ESTE-013 Define los términos de dominio una vez
- ESTE-014 Prefiere español claro y compartido
- ESTE-016 Evita falsos amigos
- ESTE-019 Un verbo para una acción
