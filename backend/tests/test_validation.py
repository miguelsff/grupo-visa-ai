"""Casos válidos, condicionales, contradicciones y límites de evidencia."""

import pytest

from app.agent.consistency import window_errors
from app.agent.facts import grounded, redact
from app.agent.models import Draft, ExtractedFact, Extraction, ServiceUnavailable, UserMessage
from app.agent.validation import validar_ocd
from app.knowledge.models import Knowledge, parse_record


@pytest.mark.parametrize("zone", ["../Lima", "/etc/passwd", "America/../Lima", "Unknown/Zone"])
def test_invalid_iana_zone_returns_validation_error(zone):
    assert window_errors(make_draft("red", {"comun.zona_horaria": zone}))


def make_draft(category: str, values: dict[str, str]) -> Draft:
    return Draft(
        categories=[category],
        facts={
            key: ExtractedFact(
                scope=key.split(".")[0],
                name=key.split(".")[1],
                value=value,
                quote=value,
                message_id=1,
            )
            for key, value in values.items()
        },
    )


def results(points, draft):
    knowledge = Knowledge(
        "ocd_fixture",
        [parse_record(p) for p in points if p["payload"]["scope"] in ["comun", *draft.categories]],
    )
    return {r.rule_id: r for r in validar_ocd(draft, knowledge)}


@pytest.fixture
def valid_microservice() -> Draft:
    common = {
        "titulo": "Certificar microservicio",
        "objetivo": "Publicar versión 2.0",
        "solicitante": "Equipo",
        "rol_solicitante": "Desarrollo",
        "responsable": "Equipo Ops",
        "rol_responsable": "Operaciones",
        "etapa": "borrador",
        "ambientes": "produccion",
        "ventana_inicio": "2026-11-14T10:00:00-05:00",
        "ventana_fin": "2026-11-14T11:00:00-05:00",
        "zona_horaria": "UTC-05:00",
        "impacto": "Reinicio breve",
        "ambiente_objetivo": "produccion",
        "dependencias_ambientes": "NO_APLICA: servicio autónomo",
        "plan_ejecucion": "Publicar el artefacto identificado",
        "resultado_ejecucion": "Versión 2.0",
        "plan_pruebas": "Enviar consulta",
        "resultado_pruebas": "HTTP 200",
        "plan_reversion": "Restaurar versión 1.0",
        "resultado_reversion": "Versión 1.0 saludable",
    }
    micro = {
        "microservicio": "ms-nuevo",
        "repositorio": "git/servicio",
        "version_actual": "1.0",
        "version_objetivo": "2.0",
        "artefacto": "registry/servicio:2.0",
        "dependencias": "NO_APLICA: servicio autónomo",
        "cambia_datos": "no",
        "cambia_contrato": "no",
        "pruebas_y_reversion": "Consulta HTTP 200 y recuperar 1.0",
        "publica_version_diferente": "sí",
        "criterio_funcional": "Consulta devuelve HTTP 200",
        "version_reversion": "1.0",
    }
    return make_draft(
        "microservicio",
        {f"comun.{k}": v for k, v in common.items()}
        | {f"microservicio.{k}": v for k, v in micro.items()},
    )


def test_valid_documentary_baseline_does_not_assert_execution(points, valid_microservice):
    output = results(points, valid_microservice)
    assert {r.status for r in output.values()} == {"CUMPLE", "NO_VERIFICABLE"}
    assert output["MIC-R05"].status == "NO_VERIFICABLE"
    assert output["OCD-C04"].status == "NO_VERIFICABLE"
    assert output["field:identificador_inmutable"].status == "CUMPLE"
    assert output["field:cambio_datos / compatibilidad"].status == "CUMPLE"
    assert all(
        r.reference.point_id and r.reference.version and r.reference.excerpt
        for r in output.values()
    )


@pytest.mark.parametrize(
    ("values", "rule", "status"),
    [
        (
            {
                "microservicio.version_actual": "2.0",
                "microservicio.version_objetivo": "2.0",
                "microservicio.publica_version_diferente": "sí",
            },
            "MIC-R02",
            "ERROR",
        ),
        (
            {"microservicio.artefacto": "image:1.0", "microservicio.version_objetivo": "2.0"},
            "MIC-R03",
            "ERROR",
        ),
        (
            {"azure.configuracion_actual": "1", "azure.configuracion_propuesta": "1"},
            "AZ-R02",
            "ERROR",
        ),
        ({"azure.replicas_min": "4", "azure.replicas_max": "2"}, "AZ-R03", "ERROR"),
        ({"azure.bandera": "habilitada"}, "AZ-R03", "ERROR"),
        ({"azure.bandera": "false"}, "AZ-R03", "CUMPLE"),
        (
            {"red.origen": "999.2.1.1", "red.destino": "10.1.1.1", "red.puerto_destino": "443"},
            "RED-R02",
            "ERROR",
        ),
        (
            {"red.origen": "10.0.0.0/24", "red.destino": "10.1.1.1", "red.puerto_destino": "65536"},
            "RED-R02",
            "ERROR",
        ),
        ({"red.puerto_destino": "443-80"}, "RED-R02", "ERROR"),
        ({"red.protocolo": "TCP", "red.puerto_destino": "53"}, "RED-R03", "FALTA_INFORMACION"),
        ({"red.protocolo": "TCP/UDP", "red.puerto_destino": "53"}, "RED-R03", "CUMPLE"),
        (
            {"identidad.tipo_autorizacion": "Azure RBAC", "identidad.rol": "Reader"},
            "ID-R03",
            "FALTA_INFORMACION",
        ),
        (
            {"identidad.prueba_permitida": "enviar", "identidad.revocacion": "retirar"},
            "ID-R04",
            "FALTA_INFORMACION",
        ),
    ],
)
def test_specific_consistency_rules(points, values, rule, status):
    category = next(iter(values)).split(".")[0]
    assert results(points, make_draft(category, values))[rule].status == status


def test_conditional_identity_dns_and_execution_fields(points):
    new = make_draft("identidad", {"identidad.estado_identidad": "nueva"})
    existing = make_draft("identidad", {"identidad.estado_identidad": "existente"})
    assert results(points, new)["field:client_id / object_id"].status == "CUMPLE"
    assert results(points, existing)["field:client_id / object_id"].status == "FALTA_INFORMACION"
    no_dns = make_draft("red", {"red.usa_dns": "no", "comun.etapa": "borrador"})
    assert results(points, no_dns)["field:nombre_dns"].status == "CUMPLE"
    assert results(points, no_dns)["RED-R04"].status == "CUMPLE"
    before_execution = make_draft("microservicio", {"comun.etapa": "ejecución"})
    assert (
        results(points, before_execution)["field:identificador_inmutable"].status
        == "FALTA_INFORMACION"
    )


def test_missing_conditions_remain_questions(points):
    draft = make_draft("microservicio", {})
    output = results(points, draft)
    assert output["field:cambio_datos / compatibilidad"].status == "FALTA_INFORMACION"
    assert output["OCD-C01"].missing


def test_authentication_requires_metadata_for_selected_mechanism(points):
    draft = make_draft("identidad", {"identidad.mecanismo_autenticacion": "OIDC"})
    output = results(points, draft)["field:confianza_o_certificado"]
    assert output.status == "FALTA_INFORMACION"
    assert output.missing == ["identidad.emisor", "identidad.sujeto", "identidad.audiencia"]
    draft = make_draft(
        "identidad",
        {
            "identidad.mecanismo_autenticacion": "certificado",
            "identidad.referencia_certificado": "cert-uno",
            "identidad.vigencia_certificado": "2027-01-01",
        },
    )
    assert results(points, draft)["field:confianza_o_certificado"].status == "CUMPLE"


def test_azure_credentials_condition_is_preserved(points):
    draft = make_draft("azure", {"azure.intervienen_credenciales": "no"})
    assert results(points, draft)["field:referencias_credenciales"].status == "CUMPLE"
    draft = make_draft("azure", {"azure.intervienen_credenciales": "sí"})
    assert results(points, draft)["field:referencias_credenciales"].status == "FALTA_INFORMACION"


def test_pending_values_and_unjustified_not_applicable_are_not_completed(points):
    draft = make_draft(
        "identidad",
        {
            "identidad.estado_identidad": "existente",
            "identidad.client_id": "PENDIENTE hasta crear la identidad",
            "identidad.object_id": "desconocido por ahora",
        },
    )
    assert results(points, draft)["field:client_id / object_id"].status == "FALTA_INFORMACION"
    draft = make_draft("microservicio", {"microservicio.dependencias": "NO_APLICA"})
    assert results(points, draft)["field:dependencias"].status == "FALTA_INFORMACION"


def test_all_26_rules_are_evaluated_once_with_their_references(points):
    draft = Draft(categories=["microservicio", "azure", "red", "identidad"])
    output = results(points, draft)
    rules = [r for key, r in output.items() if not key.startswith("field:")]
    assert len(rules) == 26
    assert {r.check for r in rules} == {"V-01", "V-02", "V-03"}


def test_grounding_rejects_invented_values_example_ids_and_missing_quote():
    fact = ExtractedFact(
        scope="comun", name="titulo", value="inventado", quote="Necesito un cambio", message_id=1
    )
    with pytest.raises(ServiceUnavailable):
        grounded(
            Extraction(categories=[], facts=[fact]),
            [UserMessage(id=1, content="Necesito un cambio")],
            Draft(),
        )
    fact.value = "Necesito"
    fact.message_id = 99
    with pytest.raises(ServiceUnavailable):
        grounded(
            Extraction(categories=[], facts=[fact]),
            [UserMessage(id=1, content="Necesito un cambio")],
            Draft(),
        )


def test_secrets_are_redacted_but_public_ids_are_not():
    text = "client_id=abc object_id=def password=valor-secreto access_token=otro-secreto"
    cleaned = redact(text)
    assert "valor-secreto" not in cleaned and "otro-secreto" not in cleaned
    assert "client_id=abc object_id=def" in cleaned


def test_dates_and_environment_contradictions(points):
    draft = make_draft(
        "red",
        {
            "comun.ambiente_objetivo": "produccion",
            "red.ambiente_destino": "certificacion",
            "comun.ventana_inicio": "2026-11-14T12:00:00",
            "comun.ventana_fin": "2026-11-14T11:00:00",
        },
    )
    output = results(points, draft)["OCD-C03"]
    assert output.status == "ERROR" and "ventana" in output.detail
