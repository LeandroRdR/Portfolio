"""
PROYECTO 1 - Ventas y segmentación de clientes (Online Retail, UCI)
====================================================================

¿Qué hace este script? (en 7 pasos)
    1. Carga el archivo CSV con las ventas.
    2. Limpia los datos (duplicados, cancelaciones, errores...).
    3. Guarda los datos limpios en una base de datos SQLite (en memoria).
    4. Ejecuta las consultas SQL del archivo queries.sql.
    5. Segmenta a los clientes con el método RFM.
    6. Calcula la retención de clientes por cohortes.
    7. Genera gráficos (carpeta output/) y un JSON con los resultados.

Cómo ejecutarlo (desde esta carpeta):
    pip install pandas matplotlib
    python analysis.py
"""

# ----------------------------------------------------------------------------
# LIBRERÍAS
# ----------------------------------------------------------------------------
import json                      # para guardar los resultados en formato JSON
import re                        # expresiones regulares (buscar patrones en texto)
import sqlite3                   # base de datos SQL ligera, incluida en Python
from pathlib import Path         # manejo cómodo de rutas de archivos

import matplotlib                # librería de gráficos
matplotlib.use("Agg")            # modo "sin ventana": guarda las imágenes en archivos
import matplotlib.pyplot as plt
import pandas as pd              # librería principal para trabajar con tablas

# ----------------------------------------------------------------------------
# RUTAS DE ARCHIVOS
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent   # carpeta donde está este script
RAW = ROOT / "data" / "online_retail.csv"  # archivo de datos original
OUT = ROOT / "output"                      # carpeta donde se guardan los resultados
OUT.mkdir(exist_ok=True)                   # la crea si no existe

# ============================================================================
# PASO 1 Y 2: CARGA Y LIMPIEZA DE DATOS
# ============================================================================

# Leemos el CSV. "parse_dates" convierte InvoiceDate en fecha real y
# "dtype" fuerza que InvoiceNo y StockCode se lean como texto (no como número),
# porque algunos empiezan por letras (ej: "C536379" = cancelación).
raw = pd.read_csv(
    RAW,
    parse_dates=["InvoiceDate"],
    dtype={"InvoiceNo": str, "StockCode": str},
)

# Diccionario donde iremos anotando cuántas filas elimina cada paso de limpieza.
# Sirve para documentar la calidad de los datos.
log = {"filas_originales": len(raw)}

# --- 2.1 Eliminar filas duplicadas exactas -----------------------------------
df = raw.drop_duplicates()
log["duplicados_eliminados"] = len(raw) - len(df)

# --- 2.2 Detectar cancelaciones ----------------------------------------------
# Las facturas que empiezan por "C" son cancelaciones (devoluciones).
cancel = df["InvoiceNo"].str.startswith("C")
log["cancelaciones"] = int(cancel.sum())

# --- 2.3 Eliminar ventas que fueron canceladas por completo ------------------
# Si un cliente compró algo y luego lo canceló con la misma cantidad, la venta
# no cuenta. Sin este paso, un pedido de 80.995 unidades que se anuló al día
# siguiente aparecería como el "producto estrella", lo cual sería falso.
key = ["CustomerID", "StockCode", "Quantity"]           # criterio para emparejar

# Tabla de cancelaciones (con la cantidad en positivo para poder compararla)
canc = df[cancel & df["CustomerID"].notna()].copy()
canc["Quantity"] = -canc["Quantity"]
# "occ" numera las repeticiones de cada combinación: así una cancelación
# solo anula UNA venta y no todas las que tengan la misma cantidad.
canc["occ"] = canc.groupby(key).cumcount()

# Tabla de ventas normales, numeradas del mismo modo
pos = df[~cancel & df["CustomerID"].notna()].copy()
pos["occ"] = pos.groupby(key).cumcount()

# Emparejamos cada cancelación con su venta original
matched = pos.merge(canc[key + ["occ"]], on=key + ["occ"], how="inner")
# Localizamos (por índice) las ventas que tienen cancelación equivalente
reversed_idx = pos.loc[
    pos.set_index(key + ["occ"]).index.isin(matched.set_index(key + ["occ"]).index)
].index
log["ventas_anuladas_por_cancelacion"] = int(len(reversed_idx))

# Nos quedamos solo con ventas (sin cancelaciones) y sin las ventas anuladas
df = df[~cancel].drop(index=reversed_idx)

# --- 2.4 Eliminar cantidades o precios inválidos -----------------------------
# Cantidad <= 0 o precio <= 0 son errores o ajustes de inventario, no ventas.
bad = (df["Quantity"] <= 0) | (df["UnitPrice"] <= 0)
log["cantidad_o_precio_invalido"] = int(bad.sum())
df = df[~bad]

# --- 2.5 Eliminar códigos que no son productos -------------------------------
# Hay "productos" que en realidad son portes (POST), comisiones (BANK CHARGES),
# ajustes manuales (M), etc. Distorsionarían el análisis de productos.
non_product = df["StockCode"].str.match(
    r"^(POST|D|M|DOT|CRUK|BANK CHARGES|AMAZONFEE|S|B|PADS|C2)$", flags=re.I
)
log["codigos_no_producto"] = int(non_product.sum())
df = df[~non_product]

# --- 2.6 Eliminar líneas sin cliente identificado ----------------------------
# Sin CustomerID no se puede hacer RFM ni cohortes, que son análisis POR CLIENTE.
log["sin_customer_id"] = int(df["CustomerID"].isna().sum())
df = df.dropna(subset=["CustomerID"]).copy()
df["CustomerID"] = df["CustomerID"].astype(int)   # 17850.0 -> 17850

# --- 2.7 Normalizar texto y calcular los ingresos ----------------------------
df["Description"] = df["Description"].fillna("").str.strip().str.upper()
df["revenue"] = df["Quantity"] * df["UnitPrice"]   # ingreso de cada línea

# Resumen final de la limpieza
log["filas_limpias"] = len(df)
log["porcentaje_conservado"] = round(100 * len(df) / log["filas_originales"], 1)

# Renombramos las columnas a minúsculas con guion bajo (estilo SQL)
sales = df.rename(columns={
    "InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description",
    "Quantity": "quantity", "InvoiceDate": "invoice_date", "UnitPrice": "unit_price",
    "CustomerID": "customer_id", "Country": "country",
})
# SQLite guarda las fechas como texto, así que las convertimos a "AAAA-MM-DD HH:MM:SS"
sales["invoice_date"] = sales["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

# ============================================================================
# PASO 3 Y 4: BASE DE DATOS SQL Y CONSULTAS
# ============================================================================

# Creamos una base de datos SQLite en memoria y volcamos la tabla "sales"
con = sqlite3.connect(":memory:")
sales.to_sql("sales", con, index=False)

# El archivo queries.sql contiene varias consultas, cada una marcada con
# una línea "-- name: <nombre>". Aquí las separamos y ejecutamos una a una.
queries = {}
texto_sql = (ROOT / "queries.sql").read_text(encoding="utf-8")
for bloque in re.split(r"-- name: ", texto_sql)[1:]:
    nombre, sql = bloque.split("\n", 1)            # 1ª línea = nombre, resto = SQL
    # Quitamos el comentario de la siguiente consulta que quedó pegado al final
    sql = sql.strip().rstrip(";").split("\n\n-- Q")[0]
    queries[nombre.strip()] = pd.read_sql_query(sql, con)   # resultado como tabla

# Guardamos cada resultado en una variable con nombre claro
monthly = queries["monthly"]            # ingresos por mes
countries = queries["countries"]        # ingresos por país
top_products = queries["top_products"]  # 10 productos con más ingresos
cohorts = queries["cohorts"]            # clientes activos por cohorte y mes
rfm = queries["rfm"]                    # recencia, frecuencia y valor por cliente

# Diciembre de 2011 solo llega hasta el día 9: lo marcamos como "parcial"
# para no interpretarlo como una caída real de ventas.
monthly["partial"] = monthly["month"] == monthly["month"].max()

# ============================================================================
# PASO 5: SEGMENTACIÓN RFM
# ============================================================================
# RFM puntúa a cada cliente de 1 a 5 en tres dimensiones (ya calculadas en SQL):
#   R (Recencia):   ¿hace cuánto compró?        (5 = muy reciente)
#   F (Frecuencia): ¿cuántas veces compró?      (5 = muchas)
#   M (Monetario):  ¿cuánto dinero ha gastado?  (5 = mucho)

def segment(row):
    """Asigna un nombre de segmento a cada cliente según sus puntuaciones R y F."""
    r, f = row["r"], row["f"]
    if r >= 4 and f >= 4: return "Campeones"             # compran a menudo y hace poco
    if r >= 3 and f >= 3: return "Leales"                # clientes regulares
    if r >= 4 and f <= 2: return "Nuevos / prometedores"  # recientes, pocas compras
    if r <= 2 and f >= 3: return "En riesgo"             # compraban mucho, llevan tiempo sin venir
    if r <= 2 and f <= 2: return "Hibernando"            # casi perdidos
    return "Necesitan atención"                          # el resto

rfm["segment"] = rfm.apply(segment, axis=1)

# Resumen por segmento: nº de clientes, ingresos, recencia y frecuencia medias
seg = (
    rfm.groupby("segment")
       .agg(customers=("customer_id", "count"),
            revenue=("monetary", "sum"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"))
       .reset_index()
)
# Porcentaje de ingresos y de clientes que representa cada segmento
seg["revenue_share"] = 100 * seg["revenue"] / seg["revenue"].sum()
seg["customer_share"] = 100 * seg["customers"] / seg["customers"].sum()
seg = seg.sort_values("revenue", ascending=False).round(1)

# Guardamos la lista completa de clientes con su segmento
rfm.to_csv(OUT / "rfm_clientes.csv", index=False)

# ============================================================================
# PASO 6: RETENCIÓN POR COHORTES
# ============================================================================
# Cohorte = grupo de clientes que hicieron su primera compra el mismo mes.
# Miramos qué % de ellos sigue comprando 1, 2, 3... meses después.

# Pasamos de formato "largo" a una matriz: filas = cohorte, columnas = meses desde la 1ª compra
mat = cohorts.pivot(index="cohort", columns="month_index", values="active_customers")
# Dividimos cada fila por su mes 0 (100 % de la cohorte) para obtener porcentajes
retention = (mat.div(mat[0], axis=0) * 100).round(1)

# ============================================================================
# KPIs GENERALES
# ============================================================================
total_rev = float(sales["revenue"].sum())
kpis = {
    "revenue": round(total_rev, 0),                               # ingresos totales
    "orders": int(sales["invoice_no"].nunique()),                 # nº de pedidos
    "customers": int(sales["customer_id"].nunique()),             # nº de clientes
    "aov": round(total_rev / sales["invoice_no"].nunique(), 2),   # ticket medio
    # % de ingresos que vienen del Reino Unido
    "uk_share": round(
        100 * float(countries.loc[countries.country == "United Kingdom", "revenue"].sum()) / total_rev, 1),
    # % de ingresos que aporta el 20 % de clientes que más gasta (regla de Pareto)
    "top20_share": round(
        100 * rfm.sort_values("monetary", ascending=False).head(int(len(rfm) * 0.2))["monetary"].sum()
        / rfm["monetary"].sum(), 1),
    # % de clientes que compraron más de una vez
    "repeat_rate": round(100 * (rfm["frequency"] > 1).mean(), 1),
}

# ============================================================================
# PASO 7: GRÁFICOS
# ============================================================================
# Estilo general: letra pequeña y sin bordes superior/derecho (más limpio)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
BLUE, GREY = "#2a6fdb", "#b9c2cf"

# --- Gráfico 1: ingresos mensuales -------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4))
completos = monthly[~monthly["partial"]]       # meses completos (azul)
parcial = monthly[monthly["partial"]]          # mes incompleto (gris)
ax.bar(completos["month"], completos["revenue"] / 1e3, color=BLUE)
ax.bar(parcial["month"], parcial["revenue"] / 1e3, color=GREY, label="mes parcial (hasta el 9)")
ax.set_ylabel("Ingresos (miles £)")
ax.set_title("Ingresos mensuales: pico estacional en nov-2011")
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "ingresos_mensuales.png", dpi=150)
plt.close(fig)

# --- Gráfico 2: peso de cada segmento RFM ------------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
s = seg.sort_values("revenue_share")
ax.barh(s["segment"], s["revenue_share"], color=BLUE)
# Etiqueta al final de cada barra con % de ingresos y % de clientes
for y, (v, c) in enumerate(zip(s["revenue_share"], s["customer_share"])):
    ax.text(v + 0.5, y, f"{v:.0f}% ingresos · {c:.0f}% clientes", va="center", fontsize=9)
ax.set_xlim(0, s["revenue_share"].max() * 1.6)   # espacio extra para las etiquetas
ax.set_xlabel("% de ingresos")
ax.set_title("Segmentos RFM: quién genera el dinero")
fig.tight_layout()
fig.savefig(OUT / "segmentos_rfm.png", dpi=150)
plt.close(fig)

# --- Gráfico 3: mapa de calor de retención por cohortes ----------------------
fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(retention.iloc[:, :12], cmap="Blues", vmin=0, vmax=60, aspect="auto")
ax.set_yticks(range(len(retention)))
ax.set_yticklabels(retention.index)
ax.set_xlabel("Meses desde la primera compra")
ax.set_title("Retención por cohorte (%)")
fig.colorbar(im, ax=ax)
fig.tight_layout()
fig.savefig(OUT / "retencion_cohortes.png", dpi=150)
plt.close(fig)

# ============================================================================
# EXPORTAR RESULTADOS (los usa el dashboard web)
# ============================================================================
primeros_12 = retention.iloc[:, :12]
resultados = {
    "kpis": kpis,
    "calidad": log,
    "monthly": monthly.to_dict("records"),
    "countries": countries.head(10).round(0).to_dict("records"),
    "top_products": top_products.to_dict("records"),
    "segments": seg.to_dict("records"),
    "retention": {
        "cohorts": list(retention.index),
        "values": primeros_12.where(primeros_12.notna(), None).values.tolist(),
    },
}
# Los valores vacíos (NaN) no son JSON válido, los cambiamos por null
texto_json = json.dumps(resultados, ensure_ascii=False, indent=1, default=float).replace("NaN", "null")
(OUT / "resultados.json").write_text(texto_json, encoding="utf-8")

# ============================================================================
# MOSTRAR UN RESUMEN EN PANTALLA
# ============================================================================
print("=== CALIDAD DE DATOS ===")
print(json.dumps(log, indent=1))
print("\n=== KPIs ===")
print(kpis)
print("\n=== SEGMENTOS RFM ===")
print(seg.to_string(index=False))
print("\n=== INGRESOS MENSUALES ===")
print(monthly.to_string(index=False))
print("\n=== TOP 5 PRODUCTOS ===")
print(top_products.head(5).to_string(index=False))
print("\nListo: gráficos y resultados guardados en la carpeta 'output'.")
