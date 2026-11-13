"""Caso de uso local de la etapa 1; no utiliza un modelo de IA."""

from app.database import Database
from app.schemas import Greeting


def say_hello(name: str, database: Database) -> Greeting:
    message = f"Hola, {name}. Next.js, FastAPI y SQLite están conectados."
    return database.create_greeting(name, message)
