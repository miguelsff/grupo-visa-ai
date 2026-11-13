import hashlib
import json
import logging
import re
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

from .models import DocumentField, Payload, Rule, Source, normalize
from .remote import Atlassian

logger = logging.getLogger("ocd.ingesta")


def compact(value: str) -> str:
    return " ".join(normalize(value).split())


def load_manifest(path: Path, base_url: str) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    pages = [manifest["index"], *manifest["models"]]
    tickets = [e for m in manifest["models"] for e in m["examples"]]
    rules = [
        *manifest["index"]["commonRules"],
        *(r for m in manifest["models"] for r in m["rules"]),
    ]
    if (len(pages), len(manifest["models"]), len(rules), len(tickets)) != (5, 4, 26, 20):
        raise ValueError("Manifiesto incompleto")
    for items, key in ((pages, "pageId"), (rules, "id"), (tickets, "key")):
        if len({i[key] for i in items}) != len(items):
            raise ValueError("Identificadores duplicados en manifiesto")
    for item in [*pages, *tickets]:
        if urlsplit(item["url"]).netloc != urlsplit(base_url).netloc:
            raise ValueError("Origen del manifiesto incompatible")
    if manifest["status"] != "PUBLISHED" or not manifest["protectedExampleExcluded"]:
        raise ValueError("Manifiesto sin autorización")
    return manifest


def parse_html(html: str) -> BeautifulSoup:
    if not html.strip():
        raise ValueError("HTML remoto vacío")
    soup = BeautifulSoup(html, "html.parser")
    if soup.find(["script", "iframe", "ac:structured-macro"]):
        raise ValueError("HTML ejecutable o macro sin resolver")
    for time_tag in soup.find_all("time"):
        if time_tag.get("datetime"):
            time_tag.insert(0, str(time_tag["datetime"]) + " ")
    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        if href not in link.get_text():
            link.append(" (" + href + ")")
    return soup


def cells(row: Tag) -> list[str]:
    return [compact(cell.get_text(" ")) for cell in row.find_all(["td", "th"], recursive=False)]


def normative_table(soup: BeautifulSoup, header: str, expected: list[list[str]]) -> list[list[str]]:
    tables = [
        t for t in soup.find_all("table") if t.find("tr") and cells(t.find("tr"))[0] == header
    ]
    if len(tables) != 1:
        raise ValueError("Tabla normativa ausente o duplicada")
    table = tables[0]
    rows = [cells(row) for row in table.find_all("tr")][1:]
    if rows != [[compact(v) for v in row] for row in expected]:
        raise ValueError("Reglas o condiciones remotas requieren revisión")
    table.decompose()
    return rows


def blocks(soup: BeautifulSoup) -> list[str]:
    result = []
    for node in soup.find_all(["h1", "h2", "h3", "p", "li", "tr", "pre"]):
        if node.find_parent(["p", "li", "tr", "pre"]):
            continue
        text = compact(node.get_text(" "))
        if text:
            result.append(text)
    if not result:
        raise ValueError("Fuente sin contenido utilizable")
    return result


def chunks(units: list[str], limit: int = 6000) -> list[str]:
    result: list[str] = []
    current = ""
    for unit in units:
        if len(unit) > 12000:
            raise ValueError("Unidad remota demasiado grande; requiere revisión")
        if current and len(current) + len(unit) + 1 > limit:
            result.append(current)
            current = ""
        current = current + "\n" + unit if current else unit
    if current:
        result.append(current)
    return result


def make_record(
    cloud: str,
    source: Source,
    scope: str,
    kind: str,
    key: str,
    text: str,
    run_id: str,
    loaded_at: str,
    applies: str | None = None,
    rule: Rule | None = None,
    field: DocumentField | None = None,
) -> Payload:
    text = normalize(text)
    return Payload(
        source_id=f"{source.system}:{cloud}:{source.id}",
        record_key=f"{kind}:{key}",
        kind=kind,
        scope=scope,
        normative=kind in ("rule", "field"),
        text=text,
        content_sha256=hashlib.sha256(text.encode()).hexdigest(),
        ingestion_run_id=run_id,
        loaded_at=loaded_at,
        source=source.model_copy(update={"locator": f"{kind}:{key}"}),
        applies_when=applies,
        rule=rule,
        field=field,
    )


def page_records(
    remote: dict, entry: dict, manifest: dict, run_id: str, loaded_at: str
) -> list[Payload]:
    if (
        remote["id"] != entry["pageId"]
        or remote["title"] != entry["title"]
        or remote["status"] != "current"
        or remote["spaceId"] != manifest["space"]["id"]
        or remote["version"]["number"] != entry["confluenceVersion"]
    ):
        raise ValueError(f"Fuente {entry['code']}: identidad o versión remota distinta")
    soup = parse_html(remote["body"]["view"]["value"])
    logger.info(
        "HTML recibido code=%s tablas=%d paneles=%d fechas=%d",
        entry["code"],
        len(soup.find_all("table")),
        len(soup.select('[data-type^="panel"], .confluence-information-macro')),
        len(soup.find_all("time")),
    )
    text = compact(soup.get_text(" "))
    if not re.search(r"Versión\s+" + re.escape(entry["documentVersion"]) + r"(?!\d|\.\d)", text):
        raise ValueError(f"Fuente {entry['code']}: versión documental distinta")
    if manifest["documentDate"] not in text:
        raise ValueError(f"Fuente {entry['code']}: fecha documental ausente")
    source = Source(
        system="confluence",
        id=remote["id"],
        code=entry["code"],
        title=remote["title"],
        url=entry["url"],
        version=str(remote["version"]["number"]),
        document_version=entry["documentVersion"],
        updated_at=remote["version"].get("createdAt"),
        locator="page",
    )
    scope = entry.get("category", "comun")
    common = scope == "comun"
    expected = []
    for rule in entry["commonRules" if common else "rules"]:
        row = [
            rule["id"],
            rule["ruleClass"],
            rule["condition" if common else "fields"],
            rule["result"],
        ]
        if not common:
            row.append(rule["mode"])
        expected.append(row)
    try:
        rule_rows = normative_table(soup, "Regla", expected)
        field_rows = (
            normative_table(
                soup,
                "Campo",
                [[f["name"], f["type"], f["when"], f["example"]] for f in entry["requiredFields"]],
            )
            if not common
            else []
        )
    except ValueError as error:
        raise ValueError(f"Fuente {entry['code']}: contenido normativo distinto") from error
    records = []
    for row in rule_rows:
        rule = Rule(
            id=row[0],
            rule_class=row[1],
            fields=None if common else row[2],
            requirement=row[2],
            result=row[3],
            mode=None if common else row[4],
        )
        applies = "Siempre" if common else f"Sección {scope} activada"
        # La condición literal de estas reglas forma parte del resultado completo.
        if not common:
            applies += "; " + row[3]
        records.append(
            make_record(
                manifest["cloudId"],
                source,
                scope,
                "rule",
                row[0],
                " | ".join(row),
                run_id,
                loaded_at,
                applies,
                rule=rule,
            )
        )
    for row in field_rows:
        field = DocumentField(name=row[0], type=row[1], when=row[2], example=row[3])
        records.append(
            make_record(
                manifest["cloudId"],
                source,
                scope,
                "field",
                row[0],
                " | ".join(row),
                run_id,
                loaded_at,
                f"Sección {scope} activada; {row[2]}",
                field=field,
            )
        )
    for ordinal, text in enumerate(chunks(blocks(soup))):
        records.append(
            make_record(
                manifest["cloudId"], source, scope, "context", str(ordinal), text, run_id, loaded_at
            )
        )
    return records


def collect(atlassian: Atlassian, manifest: dict, run_id: str, loaded_at: str) -> list[Payload]:
    records = []
    for entry in [manifest["index"], *manifest["models"]]:
        logger.info("Leyendo fuente code=%s", entry["code"])
        records.extend(
            page_records(atlassian.page(entry["pageId"]), entry, manifest, run_id, loaded_at)
        )
    for model in manifest["models"]:
        for example in model["examples"]:
            logger.info("Leyendo ejemplo code=%s", example["key"])
            remote = atlassian.ticket(example["key"])
            fields = remote["fields"]
            if remote["key"] != example["key"] or not fields["updated"]:
                raise ValueError("Ticket remoto incompatible")
            source = Source(
                system="jira",
                id=remote["id"],
                code=remote["key"],
                title=fields["summary"],
                url=example["url"],
                version=fields["updated"],
                updated_at=fields["updated"],
                document_version=None,
                locator="ticket",
            )
            units = [source.title, *blocks(parse_html(remote["renderedFields"]["description"]))]
            for ordinal, text in enumerate(chunks(units)):
                records.append(
                    make_record(
                        manifest["cloudId"],
                        source,
                        model["category"],
                        "example",
                        str(ordinal),
                        text,
                        run_id,
                        loaded_at,
                    )
                )
    validate_load(records, manifest)
    return records


def validate_load(records: list[Payload], manifest: dict) -> None:
    if len({r.point_id for r in records}) != len(records):
        raise ValueError("IDs de puntos duplicados")
    pages = {r.source.id for r in records if r.source.system == "confluence"}
    tickets = {r.source.id for r in records if r.kind == "example"}
    rules = {r.rule.id for r in records if r.rule}
    field_count = sum(len(m["requiredFields"]) for m in manifest["models"])
    if (len(pages), len(tickets), len(rules), sum(r.kind == "field" for r in records)) != (
        5,
        20,
        26,
        field_count,
    ):
        raise ValueError("Carga incompleta")
