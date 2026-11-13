"""V-01/02/03: reglas del corpus y resultados trazables, sin ejecutar fuentes."""

from app.agent.conditions import complete, executing, field_result
from app.agent.consistency import consistency
from app.agent.models import Draft, Status, ValidationResult
from app.knowledge.models import Knowledge, Record

RULE_FIELDS = {
    "OCD-C01": (
        "comun",
        "titulo objetivo solicitante rol_solicitante responsable rol_responsable "
        "etapa ambientes ventana_inicio ventana_fin zona_horaria impacto",
    ),
    "OCD-C02": (
        "comun",
        "plan_ejecucion resultado_ejecucion plan_pruebas resultado_pruebas "
        "plan_reversion resultado_reversion",
    ),
    "MIC-R01": (
        "microservicio",
        "microservicio repositorio version_actual version_objetivo artefacto",
    ),
    "MIC-R04": ("microservicio", "criterio_funcional version_reversion pruebas_y_reversion"),
    "AZ-R01": ("azure", "tipo_servicio recurso suscripcion grupo_recursos region"),
    "AZ-R04": ("comun", "plan_pruebas resultado_pruebas plan_reversion resultado_reversion"),
    "RED-R01": (
        "red",
        "origen ambiente_origen destino ambiente_destino protocolo "
        "puerto_destino finalidad sentido",
    ),
    "RED-R04": ("red", "punto_control regla reversion"),
    "ID-R01": ("identidad", "tenant nombre_identidad consumidor destino finalidad"),
    "ID-R04": ("identidad", "prueba_permitida prueba_denegada revocacion"),
}


def rule_result(draft: Draft, record: Record) -> tuple[Status, str, list[str]]:
    assert record.payload.rule is not None
    rule_id = record.payload.rule.id
    if rule_id.endswith("R05") or rule_id == "OCD-C04":
        return (
            "NO_VERIFICABLE",
            "La revisión conserva la fuente documental. "
            "La ejecución, la evidencia y los permisos efectivos requieren verificación externa.",
            [],
        )
    if rule_id in {"OCD-C05", "ID-R02"}:
        if draft.sensitive_detected:
            return (
                "ERROR",
                "Se detectó contenido sensible y se omitió. Usa referencias de credenciales.",
                [],
            )
        return "CUMPLE", "La detección limitada no encontró secretos; no garantiza su ausencia.", []
    if rule_id == "OCD-C06":
        if not draft.categories:
            return "FALTA_INFORMACION", "Indica qué secciones requiere el cambio.", ["categorias"]
        return (
            "CUMPLE",
            "Los hechos conservan citas literales del solicitante, separadas de ejemplos.",
            [],
        )
    if rule_id == "RED-R04" and executing(draft) is False:
        return "CUMPLE", "El control y la regla exacta quedan pendientes antes de ejecutar.", []
    if rule_id == "AZ-R04" and not draft.value("azure", "configuracion_actual"):
        return (
            "FALTA_INFORMACION",
            "Indica la configuración anterior que permitirá recuperar el cambio.",
            ["azure.configuracion_actual"],
        )
    if rule_id in RULE_FIELDS:
        scope, fields = RULE_FIELDS[rule_id]
        return complete(draft, scope, fields.split())
    return consistency(draft, rule_id)


def validar_ocd(draft: Draft, knowledge: Knowledge) -> list[ValidationResult]:
    results = []
    for record in knowledge.records:
        p = record.payload
        if not p.normative:
            continue
        if p.field:
            status, detail, absent = field_result(draft, record)
            check, rule_id = "V-01", f"field:{p.field.name}"
        elif p.rule:
            status, detail, absent = rule_result(draft, record)
            check = {
                "Completitud": "V-01",
                "Consistencia": "V-02",
                "Protección de datos": "V-02",
                "Procedencia": "V-03",
                "Trazabilidad": "V-03",
                "Ejecución": "V-03",
            }[p.rule.rule_class]
            rule_id = p.rule.id
        else:
            continue
        results.append(
            ValidationResult(
                check=check,
                rule_id=rule_id,
                status=status,
                detail=detail,
                missing=absent,
                reference=record.citation(),
            )
        )
    return results
