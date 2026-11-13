"""Dobles sin red y bases temporales para el flujo OCD."""

import json
from pathlib import Path

import pytest

from app.agent.conversation import Claim, Evidence, Intent, Support, Synthesis
from app.agent.models import Draft, ExtractedFact, Extraction, SelectedCategory, UserMessage
from app.config import Settings
from app.integrations.openai import ToolExecutor
from app.knowledge.models import Knowledge, parse_record
from app.schemas import KnowledgeMatch


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    frontend = tmp_path / "static"
    frontend.mkdir()
    (frontend / "index.html").write_text("<h1>Hola mundo</h1>", encoding="utf-8")
    return Settings(
        database_path=tmp_path / "ocd.sqlite3",
        knowledge_dir=tmp_path / "missing",
        frontend_dir=frontend,
    )


@pytest.fixture
def points() -> list[dict]:
    return json.loads((Path(__file__).parent / "fixtures/points.json").read_text(encoding="utf-8"))


class FakeModel:
    def classify(self, message: str, draft: Draft) -> Intent:
        return "borrador"

    def compose(self, message: str, evidence: dict[str, Evidence], *, reviewing: bool) -> Synthesis:
        key, entry = next(iter(evidence.items()))
        return Synthesis(
            claims=[Claim(text=entry.text, support=[Support(key=key, quote=entry.text)])]
        )

    def supported(self, message, proposal, selected, *, reviewing) -> bool:
        return True

    def extract(self, messages: list[UserMessage], draft: Draft) -> Extraction:
        facts = {}
        categories = []
        for message in messages:
            for line in message.content.splitlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key == "categoria":
                    categories.append(
                        SelectedCategory(
                            category=value, selected=True, quote=line, message_id=message.id
                        )
                    )
                else:
                    scope, name = key.split(".", 1)
                    facts[key] = ExtractedFact(
                        scope=scope, name=name, value=value, quote=line, message_id=message.id
                    )
        return Extraction(categories=categories, facts=list(facts.values()))

    def tools(self, execute: ToolExecutor) -> None:
        execute("buscar_conocimiento")
        execute("validar_ocd")


class FakeKnowledge:
    def __init__(self, points: list[dict]) -> None:
        self.points = points
        self.resolutions = 0
        self.collection = "ocd_test"

    def resolve(self) -> str:
        self.resolutions += 1
        return self.collection

    def retrieve(self, collection: str, categories: list[str], query: str) -> Knowledge:
        return Knowledge(
            collection,
            [
                parse_record(p)
                for p in self.points
                if p["payload"]["scope"] in ["comun", *categories]
            ],
        )

    def search(self, query: str) -> list[KnowledgeMatch]:
        record = parse_record(self.points[6])
        source = record.payload.source
        return [
            KnowledgeMatch(
                code=source.code,
                title=source.title,
                version=source.version,
                url=source.url,
                excerpt=record.payload.text,
            )
        ]

    def documentary(self, collection: str, query: str):
        return [parse_record(p) for p in self.points[:5]]


@pytest.fixture
def model() -> FakeModel:
    return FakeModel()


@pytest.fixture
def knowledge(points: list[dict]) -> FakeKnowledge:
    return FakeKnowledge(points)
