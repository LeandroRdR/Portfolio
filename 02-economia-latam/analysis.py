"""
PROYECTO 2 - Crecimiento, inflación y empleo en América Latina (Banco Mundial, 2000-2023)
===========================================================================================

¿Qué hace este script? (en 6 pasos)
    1. Carga los datos descargados por fetch_data.py y revisa su calidad.
    2. Resume cada país: crecimiento, estabilidad, desempleo e inflación.
    3. Mide cómo golpearon las crisis de 2009 y 2020 y cuánto tardó cada país en recuperarse.
    4. Prueba tres relaciones: crecimiento-desempleo (ley de Okun), convergencia
       (¿crecen más los países pobres?) e inflación-crecimiento.
    5. Genera gráficos (carpeta output/).
    6. Guarda un JSON con los resultados, que usa el dashboard.

Cómo ejecutarlo (desde esta carpeta):
    pip install pandas matplotlib numpy
    python analysis.py
"""

# ----------------------------------------------------------------------------
# LIBRERÍAS
# ----------------------------------------------------------------------------
import json                      # guardar resultados en formato JSON
from pathlib import Path         # manejo cómodo de rutas de archivos

import matplotlib                # librería de gráficos
matplotlib.use("Agg")            # modo "sin ventana": guarda las imágenes en archivos
import matplotlib.pyplot as plt
import numpy as np               # cálculo numérico (regresión y correlaciones)
import pandas as pd              # trabajo con tablas

# ----------------------------------------------------------------------------
# RUTAS DE ARCHIVOS
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent   # carpeta donde está este script
OUT = ROOT / "output"                      # carpeta de resultados
OUT.mkdir(exist_ok=True)                   # la crea si no existe

# ============================================================================
# PASO 1: CARGA Y CALIDAD DE DATOS
# ============================================================================
raw = pd.read_csv(ROOT / "data" / "worldbank_latam.csv")

# Nos quedamos con 2000-2023 (2024 está incompleto para muchos indicadores)
# y descartamos la deuda pública: menos del 40 % de los datos existe.
df = raw[raw["year"].between(2000, 2023)].drop(columns=["gov_debt"])

# Traducimos los nombres de los países al español
es = {"Argentina": "Argentina", "Bolivia": "Bolivia", "Brazil": "Brasil", "Chile": "Chile",
      "Colombia": "Colombia", "Ecuador": "Ecuador", "Mexico": "México", "Paraguay": "Paraguay",
      "Peru": "Perú", "Uruguay": "Uruguay"}
df["country"] = df["country"].map(es)

# Cuántos datos hay por país e indicador (para detectar huecos)
indicadores = ["gdp_growth", "inflation", "unemployment", "gdp_pc_ppp"]
cov = df.groupby("country")[indicadores].count()
quality = {
    "paises": df["country"].nunique(),
    "anios": 24,                                                   # 2000..2023
    # Argentina no tiene inflación publicada para 2000-2017: contamos los años que faltan
    "argentina_inflacion_faltante": int(24 - cov.loc["Argentina", "inflation"]),
    # % de datos presentes sobre el total posible
    "cobertura_pct": round(100 * df[indicadores].notna().mean().mean(), 1),
}

# ============================================================================
# PASO 2: RESUMEN POR PAÍS
# ============================================================================
def cagr(serie):
    """Tasa de crecimiento anual compuesta entre el primer y el último dato."""
    serie = serie.dropna()
    anios = serie.index[-1] - serie.index[0]
    return (serie.iloc[-1] / serie.iloc[0]) ** (1 / anios) - 1

g = df.set_index("year").groupby("country")   # agrupamos por país (año como índice)
summary = pd.DataFrame({
    "pib_pc_2000": g["gdp_pc_ppp"].apply(lambda s: s.dropna().iloc[0]),   # nivel inicial
    "pib_pc_2023": g["gdp_pc_ppp"].apply(lambda s: s.dropna().iloc[-1]),  # nivel final
    "cagr_pib_pc": g["gdp_pc_ppp"].apply(cagr) * 100,   # crecimiento anual del PIB por persona (%)
    "crec_medio": g["gdp_growth"].mean(),                # crecimiento medio del PIB (%)
    "volatilidad": g["gdp_growth"].std(),                # qué tanto oscila el crecimiento (pp)
    "desempleo_medio": g["unemployment"].mean(),         # desempleo medio (%)
}).round(2)

# Inflación: solo 2018-2023 para que Argentina sea comparable (no tiene datos antes)
summary["inflacion_mediana_2018_23"] = (
    df[df["year"].between(2018, 2023)].groupby("country")["inflation"].median().round(1)
)
# Crecimiento obtenido por cada punto de volatilidad (a más alto, más "eficiente")
summary["crec_por_unidad_riesgo"] = (summary["crec_medio"] / summary["volatilidad"]).round(2)
summary = summary.sort_values("cagr_pib_pc", ascending=False)

# ============================================================================
# PASO 3: CHOQUES DE 2009 Y 2020
# ============================================================================
def shock(year):
    """Crecimiento del PIB en el año de crisis y su promedio de los dos años previos."""
    out = {}
    for pais, d in df.groupby("country"):
        d = d.set_index("year")["gdp_growth"]
        out[pais] = {"caida": round(float(d[year]), 1),
                     "previo": round(float(d[year - 3:year - 1].mean()), 1)}
    return out

shock09, shock20 = shock(2009), shock(2020)

# ¿En qué año el PIB per cápita volvió a superar el nivel de 2019 (antes de la pandemia)?
# None significa que, según los datos, aún no lo había hecho en 2023.
recov = {}
for pais, d in df.groupby("country"):
    s = d.set_index("year")["gdp_pc_ppp"]
    ok = s[(s.index > 2020) & (s >= s[2019])]
    recov[pais] = int(ok.index[0]) if len(ok) else None

# ============================================================================
# PASO 4: RELACIONES ENTRE VARIABLES
# ============================================================================
# --- 4.1 Ley de Okun: cuando el PIB crece más, ¿baja el desempleo? ----------
panel = df.dropna(subset=["gdp_growth", "unemployment"]).copy()
panel["d_unemp"] = panel.groupby("country")["unemployment"].diff()   # cambio anual del desempleo
okun = panel.dropna(subset=["d_unemp"])
okun = okun[okun["year"] != 2020]            # 2020 (confinamientos) distorsiona la relación
slope, intercept = np.polyfit(okun["gdp_growth"], okun["d_unemp"], 1)   # recta de regresión
r_okun = float(np.corrcoef(okun["gdp_growth"], okun["d_unemp"])[0, 1])  # correlación

# --- 4.2 Convergencia: ¿crecen más rápido los países que partían más pobres? -
r_conv = float(np.corrcoef(np.log(summary["pib_pc_2000"]), summary["cagr_pib_pc"])[0, 1])

# --- 4.3 Inflación vs crecimiento (sin inflaciones extremas, >= 50 %) --------
pi = df.dropna(subset=["inflation", "gdp_growth"]).query("inflation < 50")
r_pi = float(np.corrcoef(pi["inflation"], pi["gdp_growth"])[0, 1])

# ============================================================================
# PASO 5: GRÁFICOS
# ============================================================================
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
BLUE, GREY = "#2a6fdb", "#c3cad5"
destacados = {"Chile": "#2a6fdb", "Perú": "#e0792a", "Uruguay": "#1f9d6b", "Argentina": "#c0392b"}

# --- Gráfico 1: PIB per cápita con base 100 en el año 2000 -------------------
fig, ax = plt.subplots(figsize=(9, 4.5))
for pais, d in df.groupby("country"):
    s = d.set_index("year")["gdp_pc_ppp"]
    s = s / s[2000] * 100                                   # 2000 = 100
    resaltar = pais in destacados                           # los demás en gris
    ax.plot(s.index, s, color=destacados.get(pais, GREY), lw=2.2 if resaltar else 1.2,
            zorder=3 if resaltar else 2)
    if resaltar:
        ax.text(2023.2, s.iloc[-1], pais, color=destacados[pais], va="center", fontsize=9)
ax.axhline(100, color="#888", lw=.6)
for anio in (2009, 2020):                                   # líneas de las dos crisis
    ax.axvline(anio, color="#888", lw=.6, ls=":")
ax.set_xlim(2000, 2025.5)
ax.set_ylabel("PIB per cápita PPA (2000 = 100)")
ax.set_title("Quién creció más: Chile, Perú y Uruguay se alejaron; Argentina quedó estancada")
fig.tight_layout(); fig.savefig(OUT / "pib_per_capita_indice.png", dpi=150); plt.close(fig)

# --- Gráfico 2: crecimiento medio vs volatilidad -----------------------------
fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.scatter(summary["volatilidad"], summary["crec_medio"], s=60, color=BLUE)
for pais, fila in summary.iterrows():                       # nombre junto a cada punto
    ax.annotate(pais, (fila["volatilidad"], fila["crec_medio"]), xytext=(5, 4),
                textcoords="offset points", fontsize=9)
ax.set_xlabel("Volatilidad del crecimiento (desv. est., pp)")
ax.set_ylabel("Crecimiento medio del PIB (%)")
ax.set_title("Crecimiento medio vs. volatilidad (2000-2023)")
fig.tight_layout(); fig.savefig(OUT / "crecimiento_vs_volatilidad.png", dpi=150); plt.close(fig)

# --- Gráfico 3: ley de Okun (nube de puntos + recta) -------------------------
fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.scatter(okun["gdp_growth"], okun["d_unemp"], s=14, alpha=.45, color=BLUE)
xs = np.linspace(okun["gdp_growth"].min(), okun["gdp_growth"].max(), 50)
ax.plot(xs, slope * xs + intercept, color="#c0392b", lw=2)   # recta de regresión
ax.set_xlabel("Crecimiento del PIB (%)")
ax.set_ylabel("Cambio en desempleo (pp)")
ax.set_title(f"Ley de Okun regional: cada +1 pp de PIB → {slope:+.2f} pp de desempleo")
fig.tight_layout(); fig.savefig(OUT / "okun.png", dpi=150); plt.close(fig)

# ============================================================================
# PASO 6: EXPORTAR RESULTADOS (los usa el dashboard)
# ============================================================================
# Series anuales por país: índice (2000 = 100), crecimiento, inflación y desempleo
series = {}
for pais, d in df.groupby("country"):
    base = d.loc[d["year"] == 2000, "gdp_pc_ppp"].iloc[0]
    series[pais] = {
        "years": d["year"].tolist(),
        "idx": (d["gdp_pc_ppp"] / base * 100).round(1).tolist(),
        "growth": d["gdp_growth"].round(2).tolist(),
        "inflation": d["inflation"].round(1).tolist(),
        "unemployment": d["unemployment"].round(2).tolist(),
    }

resultados = {
    "quality": quality,
    "summary": summary.reset_index().to_dict("records"),
    "shock09": shock09, "shock20": shock20, "recovery_year": recov, "series": series,
    "stats": {"okun_slope": round(slope, 3), "okun_r": round(r_okun, 2), "okun_n": len(okun),
              "convergence_r": round(r_conv, 2),
              "infl_growth_r": round(r_pi, 2), "infl_growth_n": len(pi)},
}
# Los valores vacíos (NaN) no son JSON válido: los cambiamos por null
texto = json.dumps(resultados, ensure_ascii=False, indent=1, default=float).replace("NaN", "null")
(OUT / "resultados.json").write_text(texto, encoding="utf-8")
summary.to_csv(OUT / "resumen_paises.csv")

# ----------------------------------------------------------------------------
# RESUMEN EN PANTALLA
# ----------------------------------------------------------------------------
print("=== CALIDAD DE DATOS ===");  print(quality)
print("\n=== RESUMEN POR PAÍS ===");  print(summary.to_string())
print(f"\nOkun: pendiente {slope:.3f} (r={r_okun:.2f}, n={len(okun)}) | "
      f"convergencia r={r_conv:.2f} | inflación-crecimiento r={r_pi:.2f} (n={len(pi)})")
print("\nCaída del PIB en 2009:", {p: v["caida"] for p, v in shock09.items()})
print("Caída del PIB en 2020:", {p: v["caida"] for p, v in shock20.items()})
print("Año en que el PIB per cápita superó el de 2019:", recov)
print("\nListo: gráficos y resultados guardados en la carpeta 'output'.")
