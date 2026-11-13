---
name: este
description: >
  Apply ESTE (Español Técnico Simplificado) to write, review, and rewrite
  clear, precise, consistent Spanish. Aplica ESTE para escribir, revisar y
  reescribir español técnico claro, preciso y sin ambigüedad. Use for
  technical docs, software docs, UI text, error messages, instructions,
  prompts, and agent-facing content in Spanish. Triggers: ESTE, español
  técnico simplificado, lenguaje claro técnico, reescribe en español claro,
  desambigua este texto, simplify Spanish, plain-language Spanish rewrite.
  Not for creative or marketing copy.
version: 0.1.0
---

# ESTE — Español Técnico Simplificado

ESTE es una skill de lenguaje controlado para español técnico. Combina la
disciplina estructural de ASD-STE100, los principios de lenguaje claro de
UNE-ISO 24495-1 y patrones de ambigüedad propios del español.

Objetivo: un significado por oración, un término por concepto, sin que el
lector (humano o agente) tenga que adivinar.

## Cuándo usarla

- Documentación técnica, README, runbooks, notas de API en español
- Textos de UI, estados vacíos, confirmaciones, onboarding
- Mensajes de error, logs para operadores, informes de estado
- Prompts, descripciones de tools e instrucciones entre agentes en español
- Español denso, con rodeos, sinónimos rotados o ambiguo que debe seguir siendo preciso

**No** la uses para escritura creativa, marketing o copy persuasivo donde el
tono importe más que la claridad literal.

## Modos

Elige un modo antes de reescribir. Si el usuario no lo indica, infiérelo del
tipo de texto y mantén la elección interna salvo que pida la tabla de reglas.

| Modo              | Úsalo para                                                          | Aplicación                                                                |
| ----------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Strict**        | Procedimientos, errores, acciones de UI, tools, textos de seguridad | Todas las reglas estructurales y de español; consistencia léxica estricta |
| **ESTE-flavored** | README, descripciones de PR, prosa explicativa                      | Reglas estructurales estrictas; léxicas orientativas                      |

## Proceso

1. Entiende el significado original. No reescribas antes de saber qué debe seguir siendo verdad.
2. Elige el modo.
3. Revisa oración a oración con `spec/rules.md` y la lista de comprobación.
4. Reescribe las oraciones marcadas. Conserva hechos, condiciones, matices de certeza, números y alcance.
5. Comprueba la terminología con `spec/vocabulary.yml` y el glosario del documento.
6. Devuelve el resultado según **Formato de salida**.

Si una versión más corta pierde precisión necesaria, mantén la frase más larga y
añade una línea `Kept as-is:` / `Se mantiene:`.

Si el texto ya cumple, dilo: no fuerces cambios.

## Lista de comprobación

1. **Rotación de sinónimos** — mismo concepto, varios nombres (`usuario` / `cliente` / `cuenta`).
2. **Apilado de rodeos** — afirmaciones vacías (`es importante señalar que podría eventualmente...`).
3. **Nominalización** — acción convertida en nombre (`realizar la verificación` → `verificar`).
4. **_Se_ ambiguo** — actor poco claro (`se procede a...`).
5. **Gerundio abusivo** — gerundio de consecuencia (`generando un error` cuando significa `y genera`).
6. **Oraciones largas** — varias ideas unidas con comas, dos puntos o rayas.
7. **Anglicismos innecesarios** — préstamo inglés cuando ya hay término español claro y compartido.
8. **Falsos amigos / doble sentido** — `actual`, `realizar`, `soportar`, `eventualmente`, etc.

## Reglas nucleares (resumen)

Aplícalas siempre en modo Strict. Detalle y origen: `spec/rules.md`.

| ID       | Regla                                                                            |
| -------- | -------------------------------------------------------------------------------- |
| ESTE-001 | Un concepto → un término, siempre el mismo                                       |
| ESTE-002 | Voz activa; nombra el actor si se conoce                                         |
| ESTE-003 | Una instrucción o idea por oración                                               |
| ESTE-004 | Prefiere verbo a acción nominalizada                                             |
| ESTE-005 | Conserva los matices de duda; no conviertas incertidumbre en hecho               |
| ESTE-006 | Oraciones ≤25 palabras (procedimientos ≤20)                                      |
| ESTE-007 | No uses punto y coma para unir oraciones; mejor sepáralas                        |
| ESTE-008 | Deja explícitos sujeto, verbo y objeto si omitirlos crea ambigüedad              |
| ESTE-009 | Evita el _se_ impersonal ambiguo cuando el actor importa                         |
| ESTE-010 | No uses gerundio de consecuencia; nueva oración o `y` + verbo finito             |
| ESTE-011 | Prefiere presente / imperativo / pretérito; compuesto solo si aporta significado |
| ESTE-012 | Listas para 3 o más pasos o condiciones                                          |
| ESTE-013 | Define términos de dominio una vez; luego reutilízalos exactos                   |
| ESTE-014 | Prefiere español claro y compartido frente a anglicismo innecesario              |
| ESTE-015 | Un tema por párrafo; ≤6 oraciones                                                |

## Formato de salida

**Por defecto:** solo el texto reescrito. Sin preámbulo, sin anunciar el modo, sin resumen de cambios.

Línea opcional al final si hace falta:

```text
Se mantiene: "<frase>" — <precisión que se perdería>
```

**Si lo piden** (`show the diff`, `qué reglas`, `antes/después`):

```markdown
| Regla    | Original                              | ESTE                                |
| -------- | ------------------------------------- | ----------------------------------- |
| ESTE-009 | "Se procede a reiniciar el servicio." | "El operador reinicia el servicio." |

Modo: Strict. N infracciones.
```

## Límites

**Sí hará**

- Reescribir español en oraciones cortas, unívocas y consistentes
- Conservar hechos, matices de duda, condiciones y alcance
- Señalar pérdidas de precisión en lugar de cortar en silencio
- Remitir a `spec/` y `references/` cuando haga falta más detalle

**No hará**

- Afirmar cumplimiento certificado de ASD-STE100, UNE 153101 o UNE-ISO 24495-1
- Reproducir diccionarios propietarios de esas normas
- Aplicar ESTE a copy creativo o de marketing
- Inventar causas, frecuencias o mecanismos que no estén en el original
- Arreglar un texto vacío: un párrafo hueco sigue hueco, solo más claro

## Referencias

- `spec/principles.md` — principios rectores (v0.1)
- `spec/rules.md` — reglas nucleares con severidad y origen
- `spec/vocabulary.yml` — vocabulario controlado inicial
- `references/language.md` — patrones propios del español
- `references/terminology.md` — disciplina terminológica
- `references/punctuation.md` — puntuación para la claridad
- `examples/` — antes/después por género
- `tests/cases.md` — casos de regresión
