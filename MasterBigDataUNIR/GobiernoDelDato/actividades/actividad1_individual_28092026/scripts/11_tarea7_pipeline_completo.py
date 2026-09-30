"""
Actividad 1 - Gobierno del dato y toma de decisiones
Parte II-B, Tarea 7: script único de automatización.

Este script encadena las cuatro tareas de transformación de la Parte II-A
(filtrado, normalización, integración y concatenación) y termina cargando el
resultado en el modelo dimensional Kimball diseñado en la Tarea 5
(Dim_Fecha, Dim_Ubicacion, Dim_TipoLicencia, Hechos_Terrazas).

Estructura del script (una función por tarea, encadenadas en main()):
    tarea1_filtrado_y_normalizacion()  -> Terrazas_Normalizadas
    tarea2_duplicados_y_texto()        -> Licencias_SinDuplicados, Books_Limpio
    tarea3_integracion(...)            -> Licencias_Terrazas_Integradas, Superficies_Agregadas
    tarea4_concatenacion(...)          -> Licencias_Concatenadas
    cargar_en_kimball(...)             -> carga las 4 tablas en SQL Server

Requisitos:
    pip install pandas numpy sqlalchemy pyodbc
    - Driver "ODBC Driver 17 for SQL Server" instalado en el sistema.
    - Los 4 ficheros ya limpios (salida del script 01_eda_y_limpieza.py) en DATA_DIR:
      Terrazas_202104.csv, Licencias_Locales_202104.csv, Locales_202104.csv, books.json.
    - El esquema de destino ya creado en SQL Server con 07_tarea5_kimball_esquema.sql.
    - CONNECTION_STRING (más abajo) ajustada a tu servidor, usuario y contraseña.

Uso:
    python 11_tarea7_pipeline_completo.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# Carpeta de entrada: ficheros ya limpios por el script del EDA (codificación
# unificada a UTF-8, coma decimal a punto, textos sin espacios de relleno).
DATA_DIR = Path("datos_limpios")

# Carpeta de salida: aquí se guardan todos los datasets intermedios que pide
# el enunciado, para poder inspeccionarlos sin necesidad de conectarse a Dremio
# ni a SQL Server.
SALIDA_DIR = Path("datos_procesados")
SALIDA_DIR.mkdir(exist_ok=True)

# Cadena de conexión a SQL Server (SQLAlchemy + pyodbc). Editar antes de ejecutar.
CONNECTION_STRING = (
    "mssql+pyodbc://usuario:contrasena@localhost/GobiernoDatoAct1"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

# Nombres de mes en español, usados para poblar Dim_Fecha.nombre_mes.
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
           "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ============================================================== TAREA 1
def tarea1_filtrado_y_normalizacion() -> pd.DataFrame:
    """Filtrado de nulos + normalización logarítmica + variable derivada.

    Aplica las tres sub-tareas de la Tarea 1 del enunciado sobre
    "Terrazas_202104":
      1a. Elimina las filas con más del 50 % de columnas nulas.
      1b. Añade una versión en escala logarítmica de las columnas numéricas
          de superficie y aforo (equivalente al ejemplo del enunciado de
          normalizar variables de precio a escala log).
      1c. Crea la variable derivada "Superficie_TO" (suma de Superficie_ES y
          Superficie_RA) y el ratio Superficie_TO / id_terraza que pide el
          enunciado literalmente.

    Returns:
        DataFrame "Terrazas_Normalizadas", que también se guarda en CSV.
    """
    print("\n=== TAREA 1: filtrado de nulos, normalización y variable derivada ===")
    # id_local se lee como texto (no como número) porque es un identificador,
    # no una cantidad, y así se evita perder ceros a la izquierda y poder
    # cruzarlo más tarde con Licencias sin problemas de tipo.
    terrazas = pd.read_csv(DATA_DIR / "Terrazas_202104.csv", sep=";", encoding="utf-8",
                           dtype={"id_local": str})

    # --- 1a. Filtrado de registros con más del 50 % de nulos ---
    # isna().mean(axis=1) calcula, fila a fila, la proporción de columnas
    # vacías. Se documenta el número de filas eliminadas, tal como exige el
    # enunciado, aunque en este dataset concreto el resultado sea 0 (ya
    # verificado en el EDA: ninguna fila supera el umbral).
    proporcion_nulos = terrazas.isna().mean(axis=1)
    filas_eliminadas = (proporcion_nulos > 0.5).sum()
    print(f"Terrazas: {filas_eliminadas} filas eliminadas de {len(terrazas)} "
          f"(> 50 % de nulos)")
    terrazas = terrazas[proporcion_nulos <= 0.5].reset_index(drop=True)

    # --- 1b. Normalización logarítmica ---
    # Se usa log1p (log(1 + x)) en vez de log(x) porque varias columnas
    # (mesas, sillas) contienen ceros, y log(0) no está definido.
    cols_log = ["Superficie_ES", "Superficie_RA", "mesas_es", "mesas_ra", "sillas_es"]
    for col in cols_log:
        terrazas[f"{col}_log"] = np.log1p(terrazas[col])

    # --- 1c. Variable derivada ---
    # Superficie_TO no existe en el fichero original: se calcula igual que en
    # el dataset personalizado de Dremio (Terraza_001), tratando los nulos de
    # Superficie_RA como 0 (son terrazas estacionales que no operan fuera de
    # temporada, ver EDA).
    terrazas["Superficie_TO"] = (
        terrazas["Superficie_ES"].fillna(0) + terrazas["Superficie_RA"].fillna(0)
    )
    # Ratio pedido literalmente por el enunciado. Nota para el informe:
    # id_terraza es un identificador, no una magnitud física, por lo que este
    # ratio no tiene una interpretación estadística clara; se implementa tal
    # cual lo pide el enunciado.
    terrazas["ratio_superficie_id"] = terrazas["Superficie_TO"] / terrazas["id_terraza"]

    terrazas.to_csv(SALIDA_DIR / "Terrazas_Normalizadas.csv", sep=";", index=False,
                    encoding="utf-8")
    print("Terrazas_Normalizadas guardado:", terrazas.shape)
    return terrazas


# ============================================================== TAREA 2
def tarea2_duplicados_y_texto() -> pd.DataFrame:
    """Eliminación de duplicados en Licencias + limpieza de texto en books.

    2a. Elimina de "Licencias_Locales_202104" las filas duplicadas según la
        clave de negocio (id_local, ref_licencia): un mismo local no debería
        tener la misma licencia repetida.
    2b. Limpia el texto de "books" (minúsculas + espacios de más colapsados),
        tanto en los campos de texto simples como dentro de las listas
        "authors" y "categories".

    Returns:
        DataFrame "Licencias_SinDuplicados" (se usa más adelante en la
        Tarea 3 y la Tarea 4). "Books_Limpio" se guarda en disco pero no se
        usa después en este script, porque no participa en el modelo Kimball.
    """
    print("\n=== TAREA 2: eliminación de duplicados y limpieza de texto ===")

    # --- 2a. Duplicados en Licencias ---
    lic = pd.read_csv(DATA_DIR / "Licencias_Locales_202104.csv", sep=";", encoding="utf-8",
                      dtype=str)
    # keep="first" conserva la primera aparición de cada (id_local, ref_licencia)
    # y marca el resto como duplicado.
    duplicados = lic.duplicated(subset=["id_local", "ref_licencia"], keep="first")
    print(f"Licencias: {duplicados.sum()} filas duplicadas eliminadas de {len(lic)}")
    licencias = lic[~duplicados].reset_index(drop=True)
    licencias.to_csv(SALIDA_DIR / "Licencias_SinDuplicados.csv", sep=";", index=False,
                     encoding="utf-8")

    # --- 2b. Limpieza de texto en books ---
    with open(DATA_DIR / "books.json", encoding="utf-8") as f:
        filas = [json.loads(l) for l in f if l.strip()]
    books = pd.json_normalize(filas)

    def limpiar(v):
        """minúsculas + colapsar espacios múltiples/tabulaciones + recortar extremos."""
        return " ".join(str(v).lower().split()) if isinstance(v, str) else v

    cols_texto = ["title", "shortDescription", "longDescription", "publisher"]
    cols_lista = ["authors", "categories"]  # campos que son listas de strings

    for col in cols_texto:
        if col in books.columns:
            books[col] = books[col].map(limpiar)
    for col in cols_lista:
        if col in books.columns:
            # Se limpia cada elemento de la lista por separado, no la lista como un todo.
            books[col] = books[col].map(
                lambda lst: [limpiar(v) for v in lst] if isinstance(lst, list) else lst
            )

    with open(SALIDA_DIR / "Books_Limpio.json", "w", encoding="utf-8") as out:
        for r in books.to_dict(orient="records"):
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("Books_Limpio guardado:", books.shape)
    return licencias


# ============================================================== TAREA 3
def tarea3_integracion(terrazas: pd.DataFrame, licencias: pd.DataFrame) -> pd.DataFrame:
    """JOIN Terrazas-Licencias + agregación geográfica de superficie.

    3a. INNER JOIN entre "terrazas" (salida de la Tarea 1) y "licencias"
        (salida de la Tarea 2) por "id_local". Al ser INNER, solo se
        conservan las terrazas cuyo local tiene una licencia asociada.
    3b. Agrega la superficie total (Superficie_TO) por distrito y barrio,
        para identificar las zonas con mayor y menor superficie de terrazas.

    Args:
        terrazas: DataFrame devuelto por tarea1_filtrado_y_normalizacion().
        licencias: DataFrame devuelto por tarea2_duplicados_y_texto().

    Returns:
        DataFrame "Licencias_Terrazas_Integradas", que se reutiliza después
        en cargar_en_kimball() para construir la tabla de hechos.
    """
    print("\n=== TAREA 3: JOIN e integración geográfica ===")

    # --- 3a. INNER JOIN por id_local ---
    # Solo se incorporan las columnas de licencias que no están ya en
    # terrazas, para no duplicar id_local con dos columnas iguales.
    integradas = terrazas.merge(
        licencias[["id_local", "ref_licencia", "desc_tipo_licencia",
                  "desc_tipo_situacion_licencia", "Fecha_Dec_Lic"]],
        on="id_local", how="inner",
    )
    integradas.to_csv(SALIDA_DIR / "Licencias_Terrazas_Integradas.csv", sep=";", index=False,
                      encoding="utf-8")
    print("Licencias_Terrazas_Integradas guardado:", integradas.shape)

    # --- 3b. Agregación geográfica ---
    # Se agrupa por (distrito, barrio) porque varios barrios distintos pueden
    # compartir nombre entre distritos: agrupar solo por barrio mezclaría zonas.
    agregado = (
        terrazas.groupby(["desc_distrito_local", "desc_barrio_local"], as_index=False)
        .agg(superficie_total_m2=("Superficie_TO", "sum"), num_terrazas=("id_terraza", "count"))
        .sort_values("superficie_total_m2", ascending=False)
    )
    agregado.to_csv(SALIDA_DIR / "Superficies_Agregadas.csv", sep=";", index=False, encoding="utf-8")
    print("Superficies_Agregadas guardado:", agregado.shape)
    # Documentar en el informe: agregado.iloc[0] = barrio con mayor superficie,
    # agregado.iloc[-1] = barrio con menor superficie (pedido por el enunciado).
    return integradas


# ============================================================== TAREA 4
def tarea4_concatenacion(licencias: pd.DataFrame) -> None:
    """Concatenación de datasets de distintos periodos.

    El zip de la actividad solo trae un periodo (202104): no existe un
    fichero real "Licencias_Locales_202105" con el que concatenar, como
    sugiere el enunciado. Para poder resolver el ejercicio se simula un
    segundo periodo a partir del mismo fichero (mismo esquema de columnas,
    fechas desplazadas un mes), dejándolo documentado aquí y en el informe
    como una simulación, no como datos reales.

    Args:
        licencias: DataFrame devuelto por tarea2_duplicados_y_texto(),
            usado como base para ambos periodos simulados.
    """
    print("\n=== TAREA 4: concatenación (periodo 202105 simulado) ===")

    p1 = licencias.copy()
    p1["periodo"] = "202104"

    # Periodo simulado: mismas filas, con la fecha de decreto desplazada un
    # mes, para que se pueda distinguir de las del periodo real.
    p2 = licencias.copy()
    p2["periodo"] = "202105"
    fechas = pd.to_datetime(p2["Fecha_Dec_Lic"], format="%Y-%m-%d", errors="coerce")
    p2["Fecha_Dec_Lic"] = (fechas + pd.DateOffset(months=1)).dt.strftime("%Y-%m-%d")

    # Comprobación de coherencia de columnas antes de concatenar (aunque aquí
    # se garantiza por construcción, es la misma comprobación que se haría
    # con dos ficheros reales de distintos meses).
    assert list(p1.columns) == list(p2.columns), "Los dos periodos no tienen el mismo esquema"

    concatenado = pd.concat([p1, p2], ignore_index=True)

    # La clave de duplicado incluye "periodo": con datos reales de dos meses
    # distintos, (id_local, ref_licencia) sí podría repetirse legítimamente
    # (la misma licencia sigue vigente en ambos periodos); solo se considera
    # duplicado si además coincide el periodo.
    dup = concatenado.duplicated(subset=["id_local", "ref_licencia", "periodo"])
    print(f"Duplicados por (id_local, ref_licencia, periodo): {dup.sum()}")
    concatenado = concatenado[~dup].reset_index(drop=True)
    concatenado.to_csv(SALIDA_DIR / "Licencias_Concatenadas.csv", sep=";", index=False,
                       encoding="utf-8")
    print("Licencias_Concatenadas guardado:", concatenado.shape)


# ============================================================== CARGA (Tarea 5: Kimball)
def cargar_en_kimball(integradas: pd.DataFrame) -> None:
    """Construye las dimensiones y la tabla de hechos, y las carga en SQL Server.

    A partir de "Licencias_Terrazas_Integradas" (salida de la Tarea 3), genera:
      - Dim_Fecha: una fila por cada fecha de decreto distinta.
      - Dim_Ubicacion: una fila por cada combinación (distrito, barrio).
      - Dim_TipoLicencia: una fila por cada combinación (tipo, situación).
      - Hechos_Terrazas: una fila por cada combinación terraza-licencia, con
        Superficie_TO como medida principal y las claves foráneas a las tres
        dimensiones anteriores.

    Requiere que el esquema de tablas ya exista en SQL Server (ver
    07_tarea5_kimball_esquema.sql); este script solo inserta datos
    (if_exists="append"), no crea tablas.

    Args:
        integradas: DataFrame devuelto por tarea3_integracion().
    """
    print("\n=== CARGA: modelo dimensional Kimball ===")
    fechas = pd.to_datetime(integradas["Fecha_Dec_Lic"], format="%Y-%m-%d", errors="coerce")

    # --- Dim_Fecha ---
    # id_fecha en formato YYYYMMDD (entero), la clave surrogate habitual para
    # dimensiones de fecha en modelos Kimball, porque además de identificar
    # es legible y ordenable directamente.
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
    )
    # Nota para el informe: aquí se incluye también la fecha centinela
    # "1900-01-01" detectada en el EDA, ya que formalmente es una fecha
    # válida; las filas de Hechos_Terrazas con esa fecha no tienen un
    # decreto real asociado.

    # --- Dim_Ubicacion ---
    # Clave surrogate autoincremental simple (posición en la tabla de
    # valores únicos), ya que distrito+barrio no tiene un identificador
    # natural corto y estable en el fichero de origen.
    dim_ubicacion = (
        integradas[["desc_distrito_local", "desc_barrio_local"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_ubicacion.insert(0, "id_ubicacion", dim_ubicacion.index + 1)

    # --- Dim_TipoLicencia ---
    dim_tipo = (
        integradas[["desc_tipo_licencia", "desc_tipo_situacion_licencia"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_tipo.insert(0, "id_tipo_licencia", dim_tipo.index + 1)

    # --- Hechos_Terrazas ---
    # Se cruzan las claves surrogate generadas arriba con cada fila de
    # "integradas", para sustituir los textos descriptivos por sus
    # identificadores numéricos (proceso típico de "surrogate key lookup").
    hechos = integradas.copy()
    hechos["id_fecha"] = fechas.dt.strftime("%Y%m%d").astype("Int64")  # Int64 admite nulos
    hechos = hechos.merge(dim_ubicacion, on=["desc_distrito_local", "desc_barrio_local"], how="left")
    hechos = hechos.merge(dim_tipo, on=["desc_tipo_licencia", "desc_tipo_situacion_licencia"],
                          how="left")

    # id_fecha es una clave foránea obligatoria en Hechos_Terrazas (NOT NULL
    # en el esquema SQL): las filas sin fecha válida se descartarían aquí. En
    # los datos de esta actividad no se da el caso (0 filas), pero se deja el
    # control por si se reutiliza el script con otro fichero de licencias.
    filas_sin_fecha = hechos["id_fecha"].isna().sum()
    if filas_sin_fecha:
        print(f"Aviso: {filas_sin_fecha} filas sin fecha válida se excluyen de Hechos_Terrazas")
    hechos = hechos.dropna(subset=["id_fecha"])

    hechos_terrazas = hechos[[
        "id_fecha", "id_ubicacion", "id_tipo_licencia", "id_terraza",
        "id_local", "ref_licencia", "Superficie_TO", "mesas_es", "sillas_es",
    ]].copy()
    hechos_terrazas["id_fecha"] = hechos_terrazas["id_fecha"].astype(int)

    print("Dim_Fecha:", dim_fecha.shape, "| Dim_Ubicacion:", dim_ubicacion.shape,
          "| Dim_TipoLicencia:", dim_tipo.shape, "| Hechos_Terrazas:", hechos_terrazas.shape)

    # --- Carga a SQL Server ---
    # Orden de carga importante: primero las dimensiones, después los hechos,
    # porque Hechos_Terrazas tiene claves foráneas (FOREIGN KEY) hacia las
    # tres dimensiones; SQL Server rechazaría los hechos si sus dimensiones
    # todavía no existen.
    engine = create_engine(CONNECTION_STRING)
    dim_fecha[["id_fecha", "fecha", "dia", "mes", "nombre_mes", "trimestre", "anio"]].to_sql(
        "Dim_Fecha", engine, if_exists="append", index=False)
    dim_ubicacion.to_sql("Dim_Ubicacion", engine, if_exists="append", index=False)
    dim_tipo.to_sql("Dim_TipoLicencia", engine, if_exists="append", index=False)
    hechos_terrazas.to_sql("Hechos_Terrazas", engine, if_exists="append", index=False)
    print("Carga en SQL Server completada.")


def main():
    """Orquesta el pipeline completo, en el orden que exige la dependencia de datos:
    Tarea 1 y Tarea 2 son independientes entre sí; Tarea 3 necesita el resultado
    de ambas; Tarea 4 solo necesita el de la Tarea 2; la carga final necesita
    el resultado de la Tarea 3.
    """
    terrazas = tarea1_filtrado_y_normalizacion()
    licencias = tarea2_duplicados_y_texto()
    integradas = tarea3_integracion(terrazas, licencias)
    tarea4_concatenacion(licencias)
    cargar_en_kimball(integradas)


if __name__ == "__main__":
    main()
