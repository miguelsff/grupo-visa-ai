"""Vista previa preliminar de una Tarea Jira a partir de hechos del solicitante."""

from app.agent.models import Draft, JiraPreview, ValidationResult


def _service_name(draft: Draft) -> str:
    name = draft.value("microservicio", "microservicio")
    if name.casefold().strip() in {"mi microservicio", "el microservicio", "un microservicio"}:
        return ""
    return name


def minimum_question(draft: Draft) -> str | None:
    """Solicita solo los dos identificadores necesarios para una solicitud preliminar."""
    name = _service_name(draft)
    version = draft.value("microservicio", "version_objetivo")
    if not name and not version:
        return "¿Qué microservicio vas a pasar y qué versión quieres publicar?"
    if not name:
        return "¿Qué microservicio vas a pasar?"
    if not version:
        return "¿Qué versión quieres publicar?"
    return None


def production_destination(draft: Draft) -> bool:
    return draft.value("comun", "ambiente_objetivo").casefold() in {
        "producción",
        "produccion",
        "prod",
    }


def prepare_preview(draft: Draft, validations: list[ValidationResult]) -> JiraPreview | None:
    if (
        not production_destination(draft)
        or minimum_question(draft)
        or any(item.status == "ERROR" for item in validations)
    ):
        return None
    name = _service_name(draft)
    version = draft.value("microservicio", "version_objetivo")
    objective = draft.value("comun", "objetivo")
    pending = [
        label
        for label, known in (
            ("objetivo", objective),
            (
                "ventana",
                draft.value("comun", "ventana_inicio")
                and draft.value("comun", "ventana_fin")
                and draft.value("comun", "zona_horaria"),
            ),
            ("responsable", draft.value("comun", "responsable")),
            ("repositorio", draft.value("microservicio", "repositorio")),
            ("pruebas", draft.value("comun", "plan_pruebas")),
            ("reversión", draft.value("comun", "plan_reversion")),
        )
        if not known
    ]
    description = "\n".join(
        (
            f"Pase a producción del microservicio {name}, versión {version}.",
            f"Objetivo declarado: {objective or 'Pendiente de confirmar.'}",
            "Datos desconocidos por confirmar: "
            + (", ".join(pending) if pending else "ninguno"),
            "Revisión documental: V-01, V-02 y V-03; los datos faltantes "
            "requieren confirmación antes de ejecutar el cambio.",
        )
    )
    return JiraPreview(
        project_key="SCRUM",
        issue_type="Tarea",
        title=f"Pase a producción de {name} {version}",
        description=description,
        pending=pending,
    )
