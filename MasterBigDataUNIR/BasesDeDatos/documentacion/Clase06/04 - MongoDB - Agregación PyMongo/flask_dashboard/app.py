# Autor: Marlon Cárdenas (@mCardenas) - 2025

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import config
from services import (
    summarize_counts,
    top_ciudades,
    top_metodos_pago,
    compras_por_estatus,
    ventas_por_mes,
    recientes_clientes,
    recientes_compras,
    dataframe_from_collection,
)
import pandas as pd
from ydata_profiling import ProfileReport

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["APP_NAME"] = config.APP_NAME


@app.route("/")
def index():
    counts = summarize_counts()
    ciudades = top_ciudades()
    metodos = top_metodos_pago()
    compras = recientes_compras(limit=8)
    estatus = compras_por_estatus()
    mensual = ventas_por_mes()
    return render_template(
        "index.html",
        counts=counts,
        ciudades=ciudades,
        metodos=metodos,
        estatus=estatus,
        mensual=mensual,
        compras=compras,
        title="Dashboard",
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/eda")
def eda():
    dataset = request.args.get("dataset", "clientes")
    limit = int(request.args.get("limit", 500))
    df = dataframe_from_collection(dataset, limit=limit)
    profile_html = None
    error = None
    if df.empty:
        error = "No hay datos para generar el informe."
    else:
        try:
            profile = ProfileReport(df, title=f"EDA {dataset}", minimal=True, explorative=True)
            profile_html = profile.to_html()
        except Exception as exc:
            error = f"Error generando el perfil: {exc}"

    return render_template(
        "eda.html",
        title="EDA",
        dataset=dataset,
        limit=limit,
        profile_html=profile_html,
        error=error,
    )


@app.route("/clientes")
def clientes():
    clientes_list = recientes_clientes(limit=100)
    return render_template("clientes.html", clientes=clientes_list, title="Clientes")


@app.route("/compras")
def compras():
    estatus = request.args.get("estatus")
    compras_list = recientes_compras(limit=100, estatus=estatus)
    return render_template("compras.html", compras=compras_list, estatus=estatus, title="Compras")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
