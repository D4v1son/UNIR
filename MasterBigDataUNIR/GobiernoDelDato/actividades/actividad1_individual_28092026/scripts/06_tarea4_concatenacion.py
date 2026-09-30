"""
Actividad 1 - Gobierno del dato: Parte II-A, Tarea 4 (Concatenación de datasets)

El zip de la actividad solo trae un periodo (202104): no existe un
"Licencias_Locales_202105" real con el que concatenar. Para cumplir el
ejercicio se simula un segundo periodo a partir del mismo fichero (mismo
esquema de columnas, fechas desplazadas un mes), y se documenta como tal.

Entrada : SALIDA_DIR / "Licencias_SinDuplicados.csv"
Salida  : SALIDA_DIR / "Licencias_Concatenadas.csv"
"""
from pathlib import Path

import pandas as pd

SALIDA_DIR = Path("datos_procesados")

periodo_202104 = pd.read_csv(SALIDA_DIR / "Licencias_SinDuplicados.csv", sep=";",
                             encoding="utf-8", dtype=str)
periodo_202104["periodo"] = "202104"

# --- Periodo simulado 202105 (NO son datos reales, ver docstring) ---
periodo_202105 = periodo_202104.copy()
periodo_202105["periodo"] = "202105"
fechas = pd.to_datetime(periodo_202105["Fecha_Dec_Lic"], format="%Y-%m-%d", errors="coerce")
periodo_202105["Fecha_Dec_Lic"] = (fechas + pd.DateOffset(months=1)).dt.strftime("%Y-%m-%d")

# Coherencia de columnas: incluso simulado, se comprueba que ambos periodos
# tengan exactamente el mismo esquema antes de concatenar.
assert list(periodo_202104.columns) == list(periodo_202105.columns), "Esquemas distintos"

concatenado = pd.concat([periodo_202104, periodo_202105], ignore_index=True)
print(f"Filas antes de deduplicar: {len(concatenado)}")

# Con dos periodos reales, una misma licencia no debería repetirse salvo que
# de verdad siga vigente; aquí, al ser el mismo fichero duplicado, la clave
# (id_local, ref_licencia) coincide en ambos periodos, así que sin considerar
# el periodo en la clave se perdería toda la simulación. Se deduplica por
# (id_local, ref_licencia, periodo), que sí sería la clave correcta con datos
# reales de dos meses distintos.
duplicados = concatenado.duplicated(subset=["id_local", "ref_licencia", "periodo"])
print(f"Duplicados por (id_local, ref_licencia, periodo): {duplicados.sum()}")

licencias_concatenadas = concatenado[~duplicados].reset_index(drop=True)
licencias_concatenadas.to_csv(SALIDA_DIR / "Licencias_Concatenadas.csv", sep=";", index=False,
                              encoding="utf-8")
print("Licencias_Concatenadas guardado:", licencias_concatenadas.shape)
print(licencias_concatenadas["periodo"].value_counts())
