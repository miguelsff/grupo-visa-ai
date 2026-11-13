"""Registro de mensajes recibidos por el chat en MongoDB."""

from datetime import UTC, datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.write_concern import WriteConcern

from app.agent.facts import redact


class QuestionLogUnavailable(Exception):
    """La escritura no quedó confirmada."""


class QuestionLog:
    def __init__(self, uri: str) -> None:
        try:
            self.client = MongoClient(uri, connect=False, timeoutMS=3000)
        except (PyMongoError, ValueError):
            raise ValueError("Revisa el formato de MONGODB_URI.") from None
        self.questions = self.client.ocd.get_collection(
            "preguntas", write_concern=WriteConcern(w=1, j=True)
        )

    def record(self, message: str) -> None:
        try:
            self.questions.insert_one({"texto": redact(message), "fecha": datetime.now(UTC)})
        except PyMongoError:
            raise QuestionLogUnavailable from None

    def close(self) -> None:
        self.client.close()
