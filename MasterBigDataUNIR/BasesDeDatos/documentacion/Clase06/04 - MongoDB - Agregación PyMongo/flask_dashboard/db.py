# Autor: Marlon Cárdenas (@mCardenas) - 2025

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import config

_client = None


def get_client():
    global _client
    if _client:
        return _client
    _client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=4000)
    try:
        _client.admin.command("ping")
    except ConnectionFailure as exc:
        raise RuntimeError(f"No se pudo conectar a MongoDB en {config.MONGODB_URI}") from exc
    return _client


def get_db():
    return get_client()[config.MONGODB_DB]
