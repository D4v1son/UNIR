"""
Actividad 1 - Gobierno del dato: Parte II-B, Tarea 5
Carga de "Licencias_Terrazas_Integradas" en el modelo dimensional Kimball
creado por "07_tarea5_kimball_esquema.sql" (Dim_Fecha, Dim_Ubicacion,
Dim_TipoLicencia, Hechos_Terrazas).

Requiere: pip install pandas sqlalchemy pyodbc
          Driver ODBC "ODBC Driver 17 for SQL Server" instalado en el sistema.

Antes de ejecutar, ajusta CONNECTION_STRING con tu servidor/usuario.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

SALIDA_DIR = Path("datos_procesados")

CONNECTION_STRING = (
    "mssql+pyodbc://usuario:contrasena@localhost/GobiernoDatoAct1"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
           "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

datos = pd.read_csv(SALIDA_DIR / "Licencias_Terrazas_Integradas.csv", sep=";",
                    encoding="utf-8", dtype={"id_local": str})

# -------------------------------------------------------------- Dim_Fecha
fechas = pd.to_datetime(datos["Fecha_Dec_Lic"], format="%Y-%m-%d", errors="coerce")
dim_fecha = (
    pd.DataFrame({"fecha": fechas.dropna().unique()})
    .assign(
        id_fecha=lambda d: d["fecha"].dt.strftime("%Y%m%d").astype(int),
        dia=lambda d: d["fecha"].dt.day,
        mes=lambda d: d["fecha"].dt.month,
        nombre_mes=lambda d: d["mes"].map(lambda m: MESES_ES[m - 1]),
        trimestre=lambda d: d["fecha"].dt.quarter,
        anio=lambda d: d["fecha"].dt.year,
    )
    .sort_values("id_fecha")
)
print("Dim_Fecha:", dim_fecha.shape)

# ---------------------------------------------------------- Dim_Ubicacion
dim_ubicacion = (
    datos[["desc_distrito_local", "desc_barrio_local"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_ubicacion.insert(0, "id_ubicacion", dim_ubicacion.index + 1)
print("Dim_Ubicacion:", dim_ubicacion.shape)

# ------------------------------------------------------- Dim_TipoLicencia
dim_tipo_licencia = (
    datos[["desc_tipo_licencia", "desc_tipo_situacion_licencia"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_tipo_licencia.insert(0, "id_tipo_licencia", dim_tipo_licencia.index + 1)
print("Dim_TipoLicencia:", dim_tipo_licencia.shape)

# ----------------------------------------------------------- Hechos_Terrazas
hechos = datos.copy()
hechos["_fecha_dt"] = fechas
hechos["id_fecha"] = hechos["_fecha_dt"].dt.strftime("%Y%m%d")
hechos["id_fecha"] = hechos["id_fecha"].astype("Int64")  # admite nulos (fechas no válidas)

hechos = hechos.merge(dim_ubicacion, on=["desc_distrito_local", "desc_barrio_local"], how="left")
hechos = hechos.merge(dim_tipo_licencia, on=["desc_tipo_licencia", "desc_tipo_situacion_licencia"],
                      how="left")

# Filas con fecha no válida (ver EDA: fechas centinela 1900-01-01) no tienen id_fecha:
# se documentan y se descartan de la tabla de hechos, ya que la dimensión Fecha es obligatoria.
sin_fecha = hechos["id_fecha"].isna().sum()
print(f"Filas sin fecha válida (excluidas de Hechos_Terrazas): {sin_fecha}")
hechos = hechos.dropna(subset=["id_fecha"])

hechos_terrazas = hechos[[
    "id_fecha", "id_ubicacion", "id_tipo_licencia", "id_terraza", "id_local",
    "ref_licencia", "Superficie_TO", "mesas_es", "sillas_es",
]].copy()
hechos_terrazas["id_fecha"] = hechos_terrazas["id_fecha"].astype(int)
print("Hechos_Terrazas:", hechos_terrazas.shape)

# --------------------------------------------------------------- Carga a SQL Server
engine = create_engine(CONNECTION_STRING)

dim_fecha[["id_fecha", "fecha", "dia", "mes", "nombre_mes", "trimestre", "anio"]].to_sql(
    "Dim_Fecha", engine, if_exists="append", index=False)
dim_ubicacion.to_sql("Dim_Ubicacion", engine, if_exists="append", index=False)
dim_tipo_licencia.to_sql("Dim_TipoLicencia", engine, if_exists="append", index=False)
hechos_terrazas.to_sql("Hechos_Terrazas", engine, if_exists="append", index=False)

print("\nCarga completada en SQL Server.")
