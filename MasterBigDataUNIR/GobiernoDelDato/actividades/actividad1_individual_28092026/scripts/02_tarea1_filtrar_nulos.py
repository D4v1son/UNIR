"""
Actividad 1 - Gobierno del dato: Parte II-A, Tarea 1
Elimina las filas con más del 50 % de valores nulos de cada dataset.

Entrada : DATA_DIR con los ficheros ya limpios (salida del EDA, script 01)
Salida  : impresión del nº de filas eliminadas por dataset (aquí no se elimina
          ninguna, ver comentario al final)
"""
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path("datos_limpios")


def filtrar_nulos(df: pd.DataFrame, umbral: float = 0.5) -> pd.DataFrame:
    """Elimina las filas cuya proporción de valores nulos supera `umbral`."""
    proporcion_nulos = df.isna().mean(axis=1)
    filas_a_eliminar = proporcion_nulos > umbral
    print(f"  Filas eliminadas: {filas_a_eliminar.sum()} de {len(df)}")
    return df[~filas_a_eliminar].reset_index(drop=True)


def leer_csv(nombre):
    return pd.read_csv(DATA_DIR / nombre, sep=";", encoding="utf-8", dtype=str,
                       keep_default_na=False, na_values=[""])


print("Terrazas_202104:")
terrazas = filtrar_nulos(leer_csv("Terrazas_202104.csv"))

print("Licencias_Locales_202104:")
licencias = filtrar_nulos(leer_csv("Licencias_Locales_202104.csv"))

print("Locales_202104:")
locales = filtrar_nulos(leer_csv("Locales_202104.csv"))

print("books:")
with open(DATA_DIR / "books.json", encoding="utf-8") as f:
    filas_books = [json.loads(l) for l in f if l.strip()]
books = filtrar_nulos(pd.json_normalize(filas_books))