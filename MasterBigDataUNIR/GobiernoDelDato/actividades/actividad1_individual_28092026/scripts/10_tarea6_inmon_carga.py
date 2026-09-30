"""
Actividad 1 - Gobierno del dato: Parte II-B, Tarea 6
Carga de "Licencias_Terrazas_Integradas" en el modelo normalizado 3FN
(Distrito, Barrio, Local, Terraza, TipoLicencia, SituacionLicencia, Licencia),
creado por "09_tarea6_inmon_esquema.sql".

Requiere: pip install pandas sqlalchemy pyodbc
Antes de ejecutar, ajusta CONNECTION_STRING con tu servidor/usuario.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

SALIDA_DIR = Path("datos_procesados")

CONNECTION_STRING = (
    "mssql+pyodbc://usuario:contrasena@localhost/GobiernoDatoAct1_3FN"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

datos = pd.read_csv(SALIDA_DIR / "Licencias_Terrazas_Integradas.csv", sep=";",
                    encoding="utf-8", dtype={"id_local": str})

# ------------------------------------------------------------------ Distrito
distrito = (
    datos[["desc_distrito_local"]].drop_duplicates()
    .rename(columns={"desc_distrito_local": "desc_distrito"})
    .reset_index(drop=True)
)
distrito.insert(0, "id_distrito", distrito.index + 1)
print("Distrito:", distrito.shape)

# --------------------------------------------------------------------- Barrio
barrio = (
    datos[["desc_distrito_local", "desc_barrio_local"]].drop_duplicates()
    .merge(distrito.rename(columns={"desc_distrito": "desc_distrito_local"}),
          on="desc_distrito_local")
    [["id_distrito", "desc_barrio_local"]]
    .rename(columns={"desc_barrio_local": "desc_barrio"})
    .reset_index(drop=True)
)
barrio.insert(0, "id_barrio", barrio.index + 1)
print("Barrio:", barrio.shape)

# Tabla puente para resolver id_barrio a partir de (distrito, barrio) en los pasos siguientes
_barrio_lookup = (
    datos[["desc_distrito_local", "desc_barrio_local"]].drop_duplicates()
    .merge(distrito.rename(columns={"desc_distrito": "desc_distrito_local"}), on="desc_distrito_local")
    .merge(barrio, on="id_distrito")
    .loc[lambda d: d["desc_barrio_local"] == d["desc_barrio"], ["desc_distrito_local", "desc_barrio_local", "id_barrio"]]
)

# ---------------------------------------------------------------------- Local
local = (
    datos[["id_local", "desc_distrito_local", "desc_barrio_local"]].drop_duplicates("id_local")
    .merge(_barrio_lookup, on=["desc_distrito_local", "desc_barrio_local"])
    [["id_local", "id_barrio"]]
)
print("Local:", local.shape)

# -------------------------------------------------------------------- Terraza
terraza = (
    datos[["id_terraza", "id_local", "desc_periodo_terraza", "desc_situacion_terraza",
          "Superficie_ES", "Superficie_RA", "Superficie_TO", "mesas_es", "sillas_es"]]
    .drop_duplicates("id_terraza")
)
print("Terraza:", terraza.shape)

# --------------------------------------------------------------- TipoLicencia
tipo_licencia = (
    datos[["desc_tipo_licencia"]].drop_duplicates().reset_index(drop=True)
)
tipo_licencia.insert(0, "id_tipo_licencia", tipo_licencia.index + 1)
print("TipoLicencia:", tipo_licencia.shape)

# ---------------------------------------------------------- SituacionLicencia
situacion_licencia = (
    datos[["desc_tipo_situacion_licencia"]].drop_duplicates().reset_index(drop=True)
)
situacion_licencia.insert(0, "id_situacion_licencia", situacion_licencia.index + 1)
print("SituacionLicencia:", situacion_licencia.shape)

# ------------------------------------------------------------------- Licencia
licencia = (
    datos[["id_local", "ref_licencia", "desc_tipo_licencia",
          "desc_tipo_situacion_licencia", "Fecha_Dec_Lic"]]
    .drop_duplicates(["id_local", "ref_licencia"])
    .merge(tipo_licencia, on="desc_tipo_licencia")
    .merge(situacion_licencia, on="desc_tipo_situacion_licencia")
    [["id_local", "ref_licencia", "id_tipo_licencia", "id_situacion_licencia", "Fecha_Dec_Lic"]]
)
print("Licencia:", licencia.shape)

# --------------------------------------------------------------- Carga a SQL Server
engine = create_engine(CONNECTION_STRING)

distrito.to_sql("Distrito", engine, if_exists="append", index=False)
barrio.to_sql("Barrio", engine, if_exists="append", index=False)
local.to_sql("Local", engine, if_exists="append", index=False)
terraza.to_sql("Terraza", engine, if_exists="append", index=False)
tipo_licencia.to_sql("TipoLicencia", engine, if_exists="append", index=False)
situacion_licencia.to_sql("SituacionLicencia", engine, if_exists="append", index=False)
licencia.to_sql("Licencia", engine, if_exists="append", index=False)

print("\nCarga completada en SQL Server.")
