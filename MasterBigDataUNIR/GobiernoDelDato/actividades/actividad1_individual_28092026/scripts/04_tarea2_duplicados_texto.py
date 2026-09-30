"""
Actividad 1 - Gobierno del dato: Parte II-A, Tarea 2
- Detección y eliminación de duplicados en Licencias_Locales_202104 -> "Licencias_SinDuplicados".
- Limpieza y normalización de texto en books -> "Books_Limpio".

Entrada : DATA_DIR con los ficheros limpios (salida del script 01)
Salida  : SALIDA_DIR con "Licencias_SinDuplicados.csv" y "Books_Limpio.json"
"""
import json
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path("datos_limpios")
SALIDA_DIR = Path("datos_procesados")
SALIDA_DIR.mkdir(exist_ok=True)

# --------------------------------------------------- Licencias_SinDuplicados
lic = pd.read_csv(DATA_DIR / "Licencias_Locales_202104.csv", sep=";", encoding="utf-8",
                  dtype=str)

# Clave de negocio: un local no debería tener la misma licencia repetida.
# keep="first" conserva la primera aparición y descarta el resto.
duplicados = lic.duplicated(subset=["id_local", "ref_licencia"], keep="first")
print(f"Licencias: {duplicados.sum()} filas duplicadas de {len(lic)} "
      f"(por id_local + ref_licencia)")

licencias_sin_dup = lic[~duplicados].reset_index(drop=True)
licencias_sin_dup.to_csv(SALIDA_DIR / "Licencias_SinDuplicados.csv", sep=";", index=False,
                         encoding="utf-8")
print("Licencias_SinDuplicados guardado:", licencias_sin_dup.shape)

# ------------------------------------------------------------- Books_Limpio
with open(DATA_DIR / "books.json", encoding="utf-8") as f:
    filas_books = [json.loads(l) for l in f if l.strip()]
books = pd.json_normalize(filas_books)


def limpiar_texto(valor):
    """minúsculas + espacios de más (dobles, tabulaciones, o al principio/final)."""
    if not isinstance(valor, str):
        return valor
    valor = valor.lower()
    valor = re.sub(r"\s+", " ", valor)  # varios espacios/tabs -> uno solo
    return valor.strip()


def limpiar_lista_texto(valor):
    """Igual que limpiar_texto pero para listas (authors, categories)."""
    if not isinstance(valor, list):
        return valor
    return [limpiar_texto(v) for v in valor]


books_limpio = books.copy()
cols_texto = ["title", "shortDescription", "longDescription", "publisher"]
cols_lista = ["authors", "categories"]

for col in cols_texto:
    if col in books_limpio.columns:
        books_limpio[col] = books_limpio[col].map(limpiar_texto)
for col in cols_lista:
    if col in books_limpio.columns:
        books_limpio[col] = books_limpio[col].map(limpiar_lista_texto)

print("\nEjemplo antes / después (title):")
print(" antes :", books["title"].iloc[0])
print(" después:", books_limpio["title"].iloc[0])

with open(SALIDA_DIR / "Books_Limpio.json", "w", encoding="utf-8") as out:
    for registro in books_limpio.to_dict(orient="records"):
        out.write(json.dumps(registro, ensure_ascii=False) + "\n")
print("\nBooks_Limpio guardado:", books_limpio.shape)
