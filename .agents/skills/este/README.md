# ESTE Skill — Español Técnico Simplificado

Skill para agentes (Cursor / Claude / similares) que escribe, revisa y reescribe **español técnico** con una sola lectura posible.

Se inspira en la disciplina estructural de [ASD-STE100](https://www.asd-ste100.org/) y en los principios de lenguaje claro de [UNE-ISO 24495-1:2024](https://www.une.org/), adaptados a patrones de ambigüedad del español.

> ESTE no es Lectura Fácil (UNE 153101). La Lectura Fácil ayuda a lectores con dificultades de comprensión. ESTE apunta a documentación técnica, UI, errores e instrucciones para lectores técnicos o agentes.

## Antes / después

| Antes                                                                                                                                                | Después                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Se procederá a la realización de una verificación del estado del servicio, pudiendo eventualmente reiniciarse en caso de detectarse alguna anomalía. | El operador verifica el estado del servicio. Si detecta una anomalía, puede reiniciar el servicio.        |
| El sistema soporta la actualización del perfil del usuario actual generando un error si los datos no son válidos.                                    | El sistema actualiza el perfil de este usuario. Si los datos no son válidos, el sistema muestra un error. |

Más ejemplos en [`examples/`](examples/).

## Qué hace

1. Elige el modo: **Strict** (procedimientos, errores, UI, tools) o **ESTE-flavored** (prosa explicativa).
2. Lee el texto para conservar el significado.
3. Marca infracciones de las reglas nucleares (`spec/rules.md`).
4. Reescribe sin perder hechos, condiciones ni matices de certeza.
5. Devuelve solo el texto reescrito (o la tabla de reglas si la pides).

## Instalación

```bash
npx skills add esadrian/este-skill
```

## Uso

```
Aplica ESTE a este mensaje de error
Reescribe esta documentación en español técnico simplificado
Desambigua este texto (modo Strict)
ANTES/DESPUÉS de este párrafo con ESTE
```

## Estructura

```
este-skill/
├── SKILL.md              # Instrucciones de la skill
├── README.md
├── LICENSE
├── spec/                 # Definición normativa v0.1
│   ├── principles.md
│   ├── rules.md
│   └── vocabulary.yml
├── references/           # Guías explicativas
├── examples/             # Antes/después por género
└── tests/                # Casos de regresión
```

## Fuentes (inspiración, no copia)

- ASD-STE100 — Simplified Technical English (estructura y disciplina; **no** se redistribuye su diccionario)
- UNE-ISO 24495-1:2024 — Lenguaje claro (principios: pertinente / encontrable / comprensible / utilizable)
- Particularidades del español técnico (_se_ impersonal, gerundio de consecuencia, falsos amigos, anglicismos)

## Licencia

MIT — ver [LICENSE](LICENSE).
