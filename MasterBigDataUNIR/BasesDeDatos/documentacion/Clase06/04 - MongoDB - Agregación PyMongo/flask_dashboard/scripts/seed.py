import json
import pathlib
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv
import os

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"
load_dotenv(BASE_DIR / ".env", override=False)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "LabTestDB")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json_util.loads(f.read())


def main():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    clientes = load_json(DATA_DIR / "LabTestDB.clientes.json")
    compras = load_json(DATA_DIR / "LabTestDB.compras.json")

    db.clientes.drop()
    db.compras.drop()
    if clientes:
        db.clientes.insert_many(clientes)
    if compras:
        db.compras.insert_many(compras)
    print(f"Cargados {len(clientes)} clientes y {len(compras)} compras en {MONGODB_DB}")


if __name__ == "__main__":
    main()
