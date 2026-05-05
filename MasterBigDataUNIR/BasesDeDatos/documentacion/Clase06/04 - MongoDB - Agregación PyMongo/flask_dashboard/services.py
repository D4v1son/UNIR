# Autor: Marlon Cárdenas (@mCardenas) - 2025

from pymongo import DESCENDING
from db import get_db
import pandas as pd
from pandas import json_normalize


def summarize_counts():
    db = get_db()
    compras_total = db.compras.estimated_document_count()
    ventas_total = sum(doc.get("total", 0) for doc in db.compras.find({}, {"total": 1}))
    avg_ticket = (ventas_total / compras_total) if compras_total else 0
    return {
        "clientes": db.clientes.estimated_document_count(),
        "compras": compras_total,
        "ventas_total": round(ventas_total, 2),
        "avg_ticket": round(avg_ticket, 2),
    }


def top_ciudades(limit=5):
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$direccion.ciudad", "clientes": {"$sum": 1}}},
        {"$sort": {"clientes": -1}},
        {"$limit": limit},
    ]
    return list(db.clientes.aggregate(pipeline))


def top_metodos_pago(limit=5):
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$metodo_pago", "compras": {"$sum": 1}, "monto": {"$sum": "$total"}}},
        {"$sort": {"compras": -1}},
        {"$limit": limit},
    ]
    return list(db.compras.aggregate(pipeline))


def compras_por_estatus():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$estatus", "compras": {"$sum": 1}, "monto": {"$sum": "$total"}}},
        {"$sort": {"compras": -1}},
    ]
    return list(db.compras.aggregate(pipeline))


def ventas_por_mes(limit=6):
    db = get_db()
    pipeline = [
        {"$match": {"fecha": {"$exists": True}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$fecha"}},
            "monto": {"$sum": "$total"},
            "compras": {"$sum": 1},
        }},
        {"$sort": {"_id": -1}},
        {"$limit": limit},
        {"$sort": {"_id": 1}},  # ordenar ascendente tras limitar
    ]
    return list(db.compras.aggregate(pipeline))


def recientes_clientes(limit=10):
    db = get_db()
    cursor = db.clientes.find(
        {}, {"_id": 1, "nombre": 1, "email": 1, "estatus": 1, "fecha_registro": 1}
    ).sort("fecha_registro", DESCENDING).limit(limit)
    return list(cursor)


def recientes_compras(limit=10, estatus=None):
    db = get_db()
    filtro = {"estatus": estatus} if estatus else {}
    cursor = (
        db.compras.find(
            filtro,
            {"cliente_id": 1, "total": 1, "metodo_pago": 1, "estatus": 1, "fecha": 1},
        )
        .sort("fecha", DESCENDING)
        .limit(limit)
    )
    return list(cursor)


def dataframe_from_collection(name: str, limit: int = 500):
    db = get_db()
    if name not in {"clientes", "compras"}:
        raise ValueError("Coleccion no soportada")
    docs = list(db[name].find({}, {"_id": 0}).limit(limit))
    if not docs:
        return pd.DataFrame()
    return json_normalize(docs)
