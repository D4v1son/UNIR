"""
Actividad 1 - Gobierno del dato: Parte II-A, Tarea 1 (2ª y 3ª subtarea)
- Normalización de datos: escala logarítmica de las columnas numéricas de Terrazas.
- Creación de variable derivada: ratio Superficie_TO / id_terraza -> "Terrazas_Normalizadas".

Entrada : DATA_DIR con los ficheros limpios (salida del script 01)
Salida  : SALIDA_DIR con dos nuevos datasets:
          - Terrazas_Log.csv          (columnas numéricas en escala log)
          - Terrazas_Normalizadas.csv (con la columna Superficie_TO y el ratio)
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path("datos_limpios")
SALIDA_DIR = Path("datos_procesados")
SALIDA_DIR.mkdir(exist_ok=True)

terrazas = pd.read_csv(DATA_DIR / "Terrazas_202104.csv", sep=";", encoding="utf-8")

# ---------------------------------------------------------- Normalización (log)
# Columnas numéricas sobre las que tiene sentido aplicar escala logarítmica
# (superficies y aforo). Se usa log1p (log(1 + x)) en vez de log(x) porque hay
# valores 0 en mesas/sillas, y log(0) no está definido.
cols_log = ["Superficie_ES", "Superficie_RA", "mesas_es", "mesas_ra", "sillas_es"]

terrazas_log = terrazas.copy()
for col in cols_log:
    terrazas_log[f"{col}_log"] = np.log1p(terrazas_log[col])

terrazas_log.to_csv(SALIDA_DIR / "Terrazas_Log.csv", sep=";", index=False, encoding="utf-8")
print("Terrazas_Log guardado:", terrazas_log.shape)
print(terrazas_log[[f"{c}_log" for c in cols_log]].describe().round(2))

# ---------------------------------------------------- Variable derivada (ratio)
# Superficie_TO no existe en el fichero original: se recalcula igual que en Dremio
# (Terraza_001), tratando los nulos de Superficie_RA como 0 (terrazas estacionales).
terrazas_norm = terrazas.copy()
terrazas_norm["Superficie_TO"] = (
    terrazas_norm["Superficie_ES"].fillna(0) + terrazas_norm["Superficie_RA"].fillna(0)
)

# Ratio Superficie_TO / id_terraza, tal como pide el enunciado. Nota: id_terraza es
# un identificador, no una magnitud física, por lo que este ratio no tiene una
# interpretación estadística clara (ver reflexión en el informe); se implementa
# de forma literal.
terrazas_norm["ratio_superficie_id"] = (
    terrazas_norm["Superficie_TO"] / terrazas_norm["id_terraza"]
)

terrazas_norm.to_csv(SALIDA_DIR / "Terrazas_Normalizadas.csv", sep=";", index=False,
                     encoding="utf-8")
print("\nTerrazas_Normalizadas guardado:", terrazas_norm.shape)
print(terrazas_norm[["id_terraza", "Superficie_TO", "ratio_superficie_id"]].head())
