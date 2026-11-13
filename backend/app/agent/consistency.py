"""Comprobaciones de consistencia sobre hechos documentados."""

import ipaddress
import re
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.agent.conditions import flag, missing
from app.agent.models import Draft, Status


def network_errors(draft: Draft) -> list[str]:
    errors = []
    for key in ("origen", "destino"):
        value = draft.value("red", key)
        if not value:
            continue
        if re.fullmatch(r"[\d./:a-fA-F]+", value) or "/" in value:
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                errors.append(f"{key}: IP/CIDR inválido")
    for key in ("puerto_destino", "puerto_origen"):
        value = draft.value("red", key)
        if not value or value.casefold() in {"efímero", "efimero"}:
            continue
        if not re.fullmatch(r"\d+(?:[-–]\d+)?", value):
            errors.append(f"{key}: indica un número o rango de 1 a 65535")
            continue
        ports = [int(p) for p in re.split("[-–]", value)]
        if not all(1 <= p <= 65535 for p in ports) or ports[0] > ports[-1]:
            errors.append(f"{key}: puerto o rango inválido")
    return errors


def window_errors(draft: Draft) -> list[str]:
    start, end = (draft.value("comun", key) for key in ("ventana_inicio", "ventana_fin"))
    errors = []
    if start and end:
        try:
            if datetime.fromisoformat(start) >= datetime.fromisoformat(end):
                errors.append("La ventana termina antes de iniciar o tiene duración cero.")
        except ValueError, TypeError:
            errors.append("Usa fechas ISO 8601 comparables para la ventana.")
    zone = draft.value("comun", "zona_horaria")
    if zone:
        try:
            ZoneInfo(zone)
        except (ZoneInfoNotFoundError, ValueError):
            if not re.fullmatch(r"(?:UTC)?[+-](?:0\d|1[0-4]):[0-5]\d", zone):
                errors.append("Indica una zona IANA o un desplazamiento UTC válido.")
    return errors


def consistency(draft: Draft, rule_id: str) -> tuple[Status, str, list[str]]:
    errors: list[str] = []
    need: list[str] = []
    get = draft.value
    if rule_id == "OCD-C03":
        target = get("comun", "ambiente_objetivo")
        need = missing(draft, "comun", ["ambiente_objetivo", "dependencias_ambientes"])
        for name in ("ambiente_origen", "ambiente_destino"):
            value = get("red", name)
            if value and target and value.casefold() != target.casefold():
                errors.append(
                    f"{name} contradice el ambiente objetivo. Aclara el flujo entre ambientes."
                )
        errors.extend(window_errors(draft))
    elif rule_id == "MIC-R02":
        need = missing(
            draft,
            "microservicio",
            ["version_actual", "version_objetivo", "publica_version_diferente"],
        )
        if (
            get("microservicio", "version_actual") == get("microservicio", "version_objetivo")
            and flag(get("microservicio", "publica_version_diferente")) is True
        ):
            errors.append("Las versiones coinciden aunque se declara una versión diferente.")
    elif rule_id == "MIC-R03":
        artifact, version = (
            get("microservicio", "artefacto"),
            get("microservicio", "version_objetivo"),
        )
        need = missing(draft, "microservicio", ["artefacto", "version_objetivo"])
        tag = artifact.rsplit(":", 1)[-1] if ":" in artifact.rsplit("/", 1)[-1] else ""
        if not need and ("@sha256:" in artifact or not tag):
            return (
                "NO_VERIFICABLE",
                "La referencia no permite contrastar la versión sin metadatos.",
                [],
            )
        if tag and version and tag != version:
            errors.append("El tag del artefacto contradice la versión objetivo.")
    elif rule_id == "AZ-R02":
        need = missing(draft, "azure", ["configuracion_actual", "configuracion_propuesta"])
        if not need and get("azure", "configuracion_actual") == get(
            "azure", "configuracion_propuesta"
        ):
            errors.append("La configuración propuesta coincide con la actual.")
        elif not need:
            return (
                "NO_VERIFICABLE",
                "Valores distintos; la coherencia funcional requiere revisión técnica.",
                [],
            )
    elif rule_id == "AZ-R03":
        for key in ("replicas_min", "replicas_max"):
            value = get("azure", key)
            if value and not value.isdecimal():
                errors.append(f"{key} debe ser un entero no negativo.")
        low, high = get("azure", "replicas_min"), get("azure", "replicas_max")
        if low.isdecimal() and high.isdecimal() and int(low) > int(high):
            errors.append("Las réplicas mínimas superan las máximas.")
        boolean = get("azure", "bandera")
        if boolean and boolean.casefold() not in {"true", "false"}:
            errors.append("La bandera debe ser un booleano true o false.")
        if not low and not high and not boolean:
            return (
                "NO_VERIFICABLE",
                "No hay valores tipados de réplicas o bandera para contrastar.",
                [],
            )
        if bool(low) != bool(high):
            need = missing(draft, "azure", ["replicas_min", "replicas_max"])
    elif rule_id == "RED-R02":
        need = missing(draft, "red", ["origen", "destino", "puerto_destino"])
        errors = network_errors(draft)
    elif rule_id == "RED-R03":
        protocol = get("red", "protocolo").upper()
        need = missing(draft, "red", ["protocolo"])
        if protocol and protocol not in {
            "TCP",
            "UDP",
            "UDP Y TCP",
            "TCP Y UDP",
            "TCP/UDP",
            "UDP/TCP",
        }:
            errors.append("El protocolo no está admitido en la demostración TCP/UDP.")
        if get("red", "puerto_destino") == "53" and not ("TCP" in protocol and "UDP" in protocol):
            need.append("red.protocolo: DNS requiere UDP y TCP/53")
    elif rule_id == "ID-R03":
        need = missing(draft, "identidad", ["tipo_autorizacion", "rol", "alcance"])
        if "app" in get("identidad", "tipo_autorizacion").casefold():
            need.extend(missing(draft, "identidad", ["api_destino"]))
    if errors:
        return "ERROR", " ".join(errors), need
    if need:
        return "FALTA_INFORMACION", "Completa los datos para contrastar la consistencia.", need
    return "CUMPLE", "Sin contradicciones en las comprobaciones documentales indicadas.", []
