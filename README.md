# Portfolio de Análisis de Datos

Hola, soy **Leandro Rodriguez del Rio**. Este repositorio reúne mis proyectos de análisis de datos con datos públicos reales: cada uno parte de una pregunta, pasa por limpieza, análisis y visualización, y termina en conclusiones claras.

## Proyectos

| # | Proyecto | Pregunta que responde | Herramientas | Enlaces |
|---|---|---|---|---|
| 1 | **[Ventas y segmentación de clientes](01-ventas-retail/)** | ¿De quién depende una tienda online, cuándo vende más y a qué clientes conviene recuperar? | Python · pandas · SQL (SQLite) · matplotlib · Chart.js | [**Dashboard**](https://leandrordr.github.io/Portfolio/01-ventas-retail/dashboard.html) · [Historia](01-ventas-retail/LA_HISTORIA_DEL_PROYECTO.md) · [Código](01-ventas-retail/analysis.py) |
| 2 | **[Crecimiento, inflación y empleo en América Latina](02-economia-latam/)** | ¿Qué países crecieron más y con más estabilidad, y cómo resistieron las crisis de 2009 y 2020? | Python · pandas · NumPy · API del Banco Mundial · matplotlib · Chart.js | [**Dashboard**](https://leandrordr.github.io/Portfolio/02-economia-latam/dashboard.html) · [Historia](02-economia-latam/LA_HISTORIA_DEL_PROYECTO.md) · [Código](02-economia-latam/analysis.py) |

*Más proyectos próximamente.*

### Proyecto 1 de un vistazo
- El **26 %** de los clientes genera el **69 %** de las ventas.
- Las ventas de noviembre duplican las de febrero.
- Solo **1 de cada 5** clientes nuevos vuelve a comprar al mes siguiente.

![Ingresos mensuales](01-ventas-retail/output/ingresos_mensuales.png)

### Proyecto 2 de un vistazo
- **Perú** duplicó su PIB per cápita desde 2000 (+3,1 % anual); **México** casi no avanzó (+0,3 %).
- **Argentina** es el caso atípico: crecimiento muy inestable e inflación mediana del 51 % en 2018–23.
- +1 punto de crecimiento se asocia con −0,18 puntos de desempleo.

![PIB per cápita](02-economia-latam/output/pib_per_capita_indice.png)

## Habilidades que muestran estos proyectos
- **Limpieza y calidad de datos:** duplicados, devoluciones, huecos y valores atípicos, documentando qué se descarta y por qué.
- **SQL analítico:** CTEs, funciones de ventana, `NTILE`, cohortes.
- **Análisis en Python:** pandas, NumPy, segmentación RFM, regresión y correlaciones.
- **Obtención de datos:** descarga desde archivos públicos y desde una API REST.
- **Visualización y comunicación:** gráficos y dashboards pensados para públicos técnicos y no técnicos.

## Cómo está organizado
Cada proyecto vive en su propia carpeta numerada y es independiente:
```
Portfolio/
├── README.md                     ← esta página
├── 01-ventas-retail/
│   ├── README.md                 ← resumen, método y cómo reproducirlo
│   ├── LA_HISTORIA_DEL_PROYECTO.md   ← el proyecto contado sin tecnicismos
│   ├── analysis.py · queries.sql · build_dashboard.py
│   ├── dashboard.html
│   ├── data/                     ← script para descargar los datos
│   └── output/                   ← gráficos y resultados
└── 02-economia-latam/
    ├── README.md · LA_HISTORIA_DEL_PROYECTO.md
    ├── fetch_data.py · analysis.py · build_dashboard.py
    ├── dashboard.html
    ├── data/                     ← datos del Banco Mundial (pesan poco)
    └── output/
```
Los datos grandes no se incluyen; cada proyecto indica cómo obtenerlos.
