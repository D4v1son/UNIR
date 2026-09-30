"""
Actividad 1 - Gobierno del dato: Parte II-A, Tarea 3 (Integración de datos)
- INNER JOIN entre Terrazas_Normalizadas y Licencias_SinDuplicados por "id_local"
  -> "Licencias_Terrazas_Integradas".
- Agregación geográfica de superficie por barrio -> "Superficies_Agregadas".

Entrada : SALIDA_DIR con los datasets generados por los scripts 03 y 04.
Salida  : "Licencias_Terrazas_Integradas.csv" y "Superficies_Agregadas.csv"
"""
from pathlib import Path

import pandas as pd

SALIDA_DIR = Path("datos_procesados")

# ---------------------------------------------- Licencias_Terrazas_Integradas
terrazas = pd.read_csv(SALIDA_DIR / "Terrazas_Normalizadas.csv", sep=";", encoding="utf-8",
                       dtype={"id_local": str})
licencias = pd.read_csv(SALIDA_DIR / "Licencias_SinDuplicados.csv", sep=";", encoding="utf-8",
                        dtype={"id_local": str})

# INNER JOIN: solo se conservan las terrazas cuyo local tiene una licencia asociada.
integradas = terrazas.merge(
    licencias[["id_local", "ref_licencia", "desc_tipo_licencia",
               "desc_tipo_situacion_licencia", "Fecha_Dec_Lic"]],
    on="id_local", how="inner",
)
print(f"Licencias_Terrazas_Integradas: {len(integradas)} filas "
      f"(de {len(terrazas)} terrazas, {terrazas['id_local'].isin(licencias['id_local']).sum()} "
      f"tenían licencia)")

integradas.to_csv(SALIDA_DIR / "Licencias_Terrazas_Integradas.csv", sep=";", index=False,
                  encoding="utf-8")

# ---------------------------------------------------------- Superficies_Agregadas
# Se agrega Superficie_TO por barrio (Terrazas_202104 sí trae ubicación: distrito y barrio).
agregado = (
    terrazas.groupby(["desc_distrito_local", "desc_barrio_local"], as_index=False)
    .agg(
        superficie_total_m2=("Superficie_TO", "sum"),
        num_terrazas=("id_terraza", "count"),
    )
    .sort_values("superficie_total_m2", ascending=False)
)
agregado.to_csv(SALIDA_DIR / "Superficies_Agregadas.csv", sep=";", index=False, encoding="utf-8")

print("\nSuperficies_Agregadas guardado:", agregado.shape)
print("\nBarrio con mayor superficie agregada:")
print(agregado.iloc[0])
print("\nBarrio con menor superficie agregada:")
print(agregado.iloc[-1])
