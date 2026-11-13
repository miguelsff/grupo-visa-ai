"""Condiciones y completitud de campos del contrato OCD."""

from app.agent.models import Draft, Status
from app.knowledge.models import Record


def flag(value: str) -> bool | None:
    value = value.casefold().strip()
    if value in {"sí", "si", "true", "nueva", "nuevo"}:
        return True
    if value in {"no", "false", "existente"}:
        return False
    return None


def executing(draft: Draft) -> bool | None:
    stage = draft.value("comun", "etapa").casefold()
    if stage in {"ejecución", "ejecucion", "despliegue"}:
        return True
    if stage in {"borrador", "preparación", "preparacion", "certificación", "certificacion"}:
        return False
    return None


def applicability(draft: Draft, scope: str, condition: str) -> bool | None:
    match condition:
        case "Siempre":
            return True
        case "Antes de ejecutar" | "Antes de ejecutar el despliegue":
            return executing(draft)
        case "Al definir la regla ejecutable":
            return flag(draft.value("red", "regla_ejecutable"))
        case "Si existe la identidad":
            state = draft.value("identidad", "estado_identidad").casefold()
            return {"nueva": False, "nuevo": False, "existente": True}.get(state)
        case "Si se utiliza resolución de nombres":
            return True if draft.value("red", "nombre_dns") else flag(draft.value("red", "usa_dns"))
        case "Si cambia un contrato o datos":
            values = [flag(draft.value(scope, k)) for k in ("cambia_datos", "cambia_contrato")]
            return True if True in values else False if values == [False, False] else None
        case "Si intervienen secretos o certificados":
            return flag(draft.value(scope, "intervienen_credenciales"))
        case "Según el mecanismo":
            return True if draft.value(scope, "mecanismo_autenticacion") else None
        case _:
            return None


def required_names(scope: str, name: str) -> list[str]:
    if name == "identidad_nueva / existente":
        return ["estado_identidad"]
    return [part.strip() for part in name.split("/")]


def missing(draft: Draft, scope: str, names: list[str]) -> list[str]:
    return [f"{scope}.{name}" for name in names if not draft.value(scope, name)]


def complete(draft: Draft, scope: str, names: list[str]) -> tuple[Status, str, list[str]]:
    absent = missing(draft, scope, names)
    return (
        "FALTA_INFORMACION" if absent else "CUMPLE",
        "Completa los datos indicados." if absent else "Datos documentales presentes.",
        absent,
    )


def field_result(draft: Draft, record: Record) -> tuple[Status, str, list[str]]:
    p = record.payload
    assert p.field is not None
    applies = applicability(draft, p.scope, p.field.when)
    if applies is None:
        return (
            "FALTA_INFORMACION",
            f"Aclara la condición: {p.field.when}.",
            [f"{p.scope}.{p.field.name}: {p.field.when}"],
        )
    if not applies:
        return "CUMPLE", f"No exigido en esta revisión: {p.field.when}.", []
    if p.field.name == "confianza_o_certificado":
        mechanism = draft.value("identidad", "mecanismo_autenticacion").casefold()
        if "oidc" in mechanism or "federa" in mechanism:
            return complete(draft, "identidad", ["emisor", "sujeto", "audiencia"])
        if "certificado" in mechanism:
            return complete(draft, "identidad", ["referencia_certificado", "vigencia_certificado"])
        return "NO_VERIFICABLE", "El mecanismo de autenticación requiere revisión técnica.", []
    return complete(draft, p.scope, required_names(p.scope, p.field.name))
