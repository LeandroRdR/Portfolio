"""
Descarga el dataset Online Retail (UCI) y lo deja listo como data/online_retail.csv

Uso (desde la carpeta del proyecto):
    python data/descargar_datos.py
"""
import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

# Dirección oficial del dataset en el repositorio de la UCI
URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
DESTINO = Path(__file__).resolve().parent / "online_retail.csv"

print("Descargando el dataset (unos 23 MB)...")
with urllib.request.urlopen(URL, timeout=120) as r:
    contenido = r.read()

# El zip trae un único archivo Excel: lo leemos directamente desde memoria
with zipfile.ZipFile(io.BytesIO(contenido)) as z:
    nombre_excel = z.namelist()[0]
    with z.open(nombre_excel) as f:
        df = pd.read_excel(f)

# Lo guardamos como CSV, que se lee mucho más rápido que el Excel
df.to_csv(DESTINO, index=False)
print(f"Listo: {len(df):,} filas guardadas en {DESTINO}")
