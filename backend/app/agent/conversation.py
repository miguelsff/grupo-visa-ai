"""Intención del turno y redacción respaldada por el borrador y los puntos recuperados."""

import re
from dataclasses import dataclass
from typing import Literal

from app.agent.models import Citation, Draft, StrictModel, ValidationResult

Intent = Literal["saludo", "fuera_de_contexto", "consulta", "borrador"]


class TurnIntent(StrictModel):
    intent: Intent


class Support(StrictModel):
    key: str
    quote: str


class Claim(StrictModel):
    text: str
    support: list[Support]


class Synthesis(StrictModel):
    claims: list[Claim]


class Assessment(StrictModel):
    supported: bool


@dataclass(frozen=True)
class Evidence:
    text: str
    citation: Citation | None


CAPABILITIES = (
    "Puedo ayudarte a preparar o revisar un borrador OCD, explicar sus reglas con fuentes "
    "e identificar qué datos faltan sobre microservicios, Azure, redes e identidades."
)
INTRO = "Hola, soy el asistente de solicitudes de cambio OCD. " + CAPABILITIES
OFF_TOPIC = "Solo puedo responder preguntas sobre solicitudes de cambio OCD. " + CAPABILITIES
NO_INFORMATION = "No tengo información suficiente para responder esa pregunta."


def obvious_intent(message: str) -> Intent | None:
    normalized = message.casefold().strip(" \t\r\n¡!¿?.,")
    if normalized in {"hola", "buenas", "buenos días", "buenas tardes", "buenas noches"}:
        return "saludo"
    if (
        normalized in {"continuar", "reanudar"}
        or re.fullmatch(
            r"(?:quiero|necesito) (?:preparar|crear|armar) (?:un cambio|una (?:solicitud|ocd))",
            normalized,
        )
        or re.match(r"^(?:categoria|(?:comun|microservicio|azure|red|identidad)\.\w+)=", normalized)
    ):
        return "borrador"
    return None


def evidence_for(
    draft: Draft, sources: list[Citation], validations: list[ValidationResult]
) -> dict[str, Evidence]:
    evidence = {
        f"dato:{key}": Evidence(f"{key}: {fact.value}", None)
        for key, fact in draft.facts.items()
        if draft.value(fact.scope, fact.name)
    }
    for source in sources:
        evidence[source.point_id] = Evidence(source.excerpt, source)
    for rule in validations:
        text = f"{rule.check} {rule.rule_id}: {rule.status}. {rule.detail}"
        if rule.missing:
            text += " Datos pendientes: " + ", ".join(rule.missing)
        evidence[f"validacion:{rule.reference.point_id}"] = Evidence(text, rule.reference)
    return evidence


def admitted_support(
    proposal: Synthesis, evidence: dict[str, Evidence]
) -> dict[str, Evidence] | None:
    selected: dict[str, Evidence] = {}
    for claim in proposal.claims:
        if not claim.text.strip() or not claim.support:
            return None
        for item in claim.support:
            entry = evidence.get(item.key)
            if entry is None or not item.quote.strip() or item.quote not in entry.text:
                return None
            selected[item.key] = entry
    return selected or None


def evidence_data(evidence: dict[str, Evidence]) -> dict[str, dict[str, str]]:
    return {
        key: {
            "tipo": (
                "dato del solicitante"
                if entry.citation is None
                else "ejemplo histórico"
                if entry.citation.origin == "jira"
                else "validación del borrador"
                if key.startswith("validacion:")
                else "documentación"
            ),
            "referencia": entry.citation.record_key if entry.citation else key,
            "codigo": entry.citation.code if entry.citation else "",
            "texto": entry.text,
        }
        for key, entry in evidence.items()
    }


def render(proposal: Synthesis, selected: dict[str, Evidence]) -> tuple[str, list[Citation]]:
    paragraphs = []
    citations = {}
    for claim in proposal.claims:
        labels = []
        for item in claim.support:
            citation = selected[item.key].citation
            if citation:
                citations[citation.point_id] = citation
                if citation.code not in labels:
                    labels.append(citation.code)
        suffix = " [" + ", ".join(labels) + "]" if labels else ""
        paragraphs.append(claim.text.strip() + suffix)
    return "\n\n".join(paragraphs), list(citations.values())


def review_summary(draft: Draft, validations: list[ValidationResult]) -> str:
    """Describe un borrador desde hechos admitidos y controles ya ejecutados."""
    priority = (
        "comun.titulo",
        "microservicio.microservicio",
        "microservicio.version_actual",
        "microservicio.version_objetivo",
        "comun.ambiente_objetivo",
        "comun.objetivo",
        "azure.recurso",
        "red.destino",
        "identidad.nombre_identidad",
    )
    details = []
    for key in dict.fromkeys((*priority, *draft.facts)):
        fact = draft.facts.get(key)
        if fact and (value := draft.value(fact.scope, fact.name)):
            label = {
                "titulo": "título",
                "version_actual": "versión actual",
                "version_objetivo": "versión objetivo",
            }.get(fact.name, fact.name.replace("_", " "))
            details.append(f"• {label.capitalize()}: {value}")
        if len(details) == 5:
            break
    paragraphs = [
        "Preparé el borrador con los datos que indicaste:\n" + "\n".join(details)
        if details
        else "Aún no tengo datos suficientes para describir el cambio que solicitas."
    ]
    errors = [v for v in validations if v.status == "ERROR"]
    pending = [v for v in validations if v.status == "FALTA_INFORMACION" and v.missing]
    pending.sort(key=lambda v: v.rule_id != "OCD-C01")
    if errors:
        problem = errors[0]
        paragraphs.append(
            f"Hay una inconsistencia que revisar: {problem.detail} "
            f"[{problem.reference.code}, {problem.rule_id}]."
        )
    if pending:
        item = pending[0]
        labels = [name.split(".", 1)[-1].replace("_", " ") for name in item.missing[:3]]
        needed = ", ".join(labels)
        paragraphs.append(
            f"Para continuar, indícame estos datos: {needed}. "
            f"[{item.reference.code}, {item.rule_id}]"
        )
    elif not errors and validations:
        paragraphs.append("La revisión documental no encontró campos pendientes de completar.")
    return "\n\n".join(paragraphs)
