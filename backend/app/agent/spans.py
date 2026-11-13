"""Recupera citas de los mensajes originales mediante sus palabras inicial y final."""

import re

from app.agent.facts import InvalidExtraction
from app.agent.models import (
    Category,
    ExtractedFact,
    Extraction,
    Scope,
    SelectedCategory,
    StrictModel,
    UserMessage,
)


class MessageSpan(StrictModel):
    message_id: int
    first: str
    last: str


class FactSpan(MessageSpan):
    scope: Scope
    name: str


class CategorySpan(MessageSpan):
    category: Category
    selected: bool


class SpanExtraction(StrictModel):
    categories: list[CategorySpan]
    facts: list[FactSpan]


type TokenIndex = dict[int, dict[str, re.Match[str]]]


def index_tokens(messages: list[UserMessage]) -> TokenIndex:
    return {
        message.id: {
            f"{i}:{token[0]}": token
            for i, token in enumerate(re.finditer(r"\w+|[^\w\s]", message.content))
        }
        for message in messages
    }


def materialize(spans: SpanExtraction, index: TokenIndex) -> Extraction:
    def literal(span: MessageSpan) -> str:
        tokens = index.get(span.message_id, {})
        first = tokens.get(span.first)
        last = tokens.get(span.last)
        if first is None or last is None or first.start() > last.start():
            raise InvalidExtraction(
                "No se pudo ubicar el fragmento indicado. Los mensajes siguen pendientes."
            )
        return first.string[first.start() : last.end()]

    facts = []
    for span in spans.facts:
        value = literal(span)
        facts.append(
            ExtractedFact(
                scope=span.scope,
                name=span.name,
                value=value,
                quote=value,
                message_id=span.message_id,
            )
        )
    categories = [
        SelectedCategory(
            category=span.category,
            selected=span.selected,
            quote=literal(span),
            message_id=span.message_id,
        )
        for span in spans.categories
    ]
    return Extraction(categories=categories, facts=facts)
