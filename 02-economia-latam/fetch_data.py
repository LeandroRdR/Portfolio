"""
Descarga indicadores macroeconómicos del Banco Mundial (API pública, no necesita clave)
y los guarda en data/worldbank_latam.csv

Uso (desde esta carpeta):
    python fetch_data.py
"""
import json                      # leer la respuesta de la API (formato JSON)
import urllib.request            # hacer la petición web
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# QUÉ DESCARGAR
# ----------------------------------------------------------------------------
# Códigos ISO de los 10 países: Argentina, Brasil, Chile, Colombia, México,
# Perú, Uruguay, Ecuador, Bolivia y Paraguay
COUNTRIES = ["ARG", "BRA", "CHL", "COL", "MEX", "PER", "URY", "ECU", "BOL", "PRY"]

# Código del Banco Mundial -> nombre corto que usamos en el análisis
INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",       # crecimiento del PIB (% anual)
    "FP.CPI.TOTL.ZG": "inflation",           # inflación, precios al consumidor (% anual)
    "SL.UEM.TOTL.ZS": "unemployment",        # desempleo (% de la fuerza laboral, estimación OIT)
    "NY.GDP.PCAP.PP.KD": "gdp_pc_ppp",       # PIB per cápita PPA (USD constantes)
    "GC.DOD.TOTL.GD.ZS": "gov_debt",         # deuda del gobierno central (% del PIB)
}
OUT = Path(__file__).resolve().parent / "data" / "worldbank_latam.csv"
OUT.parent.mkdir(exist_ok=True)


def get(indicator):
    """Descarga un indicador para los 10 países (2000-2024) y lo devuelve como tabla."""
    url = (f"https://api.worldbank.org/v2/country/{';'.join(COUNTRIES)}/indicator/{indicator}"
           "?format=json&per_page=5000&date=2000:2024")
    with urllib.request.urlopen(url, timeout=60) as r:
        meta, filas = json.load(r)       # la API devuelve [metadatos, datos]
    return pd.DataFrame([
        {"country_code": x["countryiso3code"], "country": x["country"]["value"],
         "year": int(x["date"]), INDICATORS[indicator]: x["value"]}
        for x in filas
    ])


# Descargamos los 5 indicadores y los unimos en una sola tabla (país + año)
tablas = [get(i) for i in INDICATORS]
df = tablas[0]
for t in tablas[1:]:
    df = df.merge(t, on=["country_code", "country", "year"], how="outer")

df = df.sort_values(["country_code", "year"])
df.to_csv(OUT, index=False)

print(f"Listo: {len(df)} filas guardadas en {OUT}")
print("\nDatos disponibles por país e indicador:")
print(df.groupby("country")[list(INDICATORS.values())].count())
