# ¿Qué países de América Latina crecieron más y mejor?
### La historia del Proyecto 2, contada sin tecnicismos

## 1. De dónde vienen los datos

Del **Banco Mundial**, que publica de forma gratuita indicadores económicos de todos los países. Usamos **10 países de América Latina** (Argentina, Bolivia, Brasil, Chile, Colombia, Ecuador, México, Paraguay, Perú y Uruguay) entre **2000 y 2023**, y cuatro indicadores:

| Indicador | Qué significa |
|---|---|
| **PIB por persona** | Cuánta riqueza produce el país por habitante (ajustada por el costo de vida). Es la mejor señal de cómo cambia el nivel de vida. |
| **Crecimiento del PIB** | Cuánto crece o se achica la economía cada año. |
| **Inflación** | Cuánto suben los precios en un año. |
| **Desempleo** | Qué porcentaje de las personas que quieren trabajar no encuentra empleo. |

## 2. El desafío

> *Esta pregunta la planteamos nosotros como ejercicio de análisis. Nadie nos la encargó.*

Dos décadas dan para mucho: auge de las materias primas, la crisis financiera mundial de 2009 y la pandemia de 2020. Quisimos responder:

1. ¿Qué países mejoraron más su nivel de vida desde el año 2000?
2. ¿Quiénes crecieron de forma estable y quiénes con sobresaltos?
3. ¿Cómo golpearon las crisis de 2009 y 2020, y cuánto tardó cada país en recuperarse?
4. ¿Se cumplen en la región algunas ideas clásicas de la economía? Por ejemplo, que cuando la economía crece baja el desempleo, o que los países más pobres crecen más rápido.

## 3. Cómo lo completamos

**Paso 1: descargar.** Un programa pide los datos directamente a la API del Banco Mundial.

**Paso 2: revisar la calidad.** Antes de analizar, vimos qué faltaba. Dos hallazgos: Argentina **no tiene inflación publicada entre 2000 y 2017**, y los datos de deuda pública eran tan escasos que los descartamos.

**Paso 3: resumir cada país.** Calculamos cuánto creció el PIB por persona cada año (en promedio) y cuánto *oscila* el crecimiento: un país que crece 3 % todos los años es más estable que otro que alterna +8 % y −2 %, aunque promedien parecido.

**Paso 4: medir las crisis.** Miramos cuánto cayó cada economía en 2009 y 2020, y en qué año su PIB por persona volvió al nivel de antes de la pandemia.

**Paso 5: probar las ideas clásicas** con estadística sencilla (correlaciones y una recta de tendencia).

**Paso 6: contarlo** en un tablero visual (`dashboard.html`).

## 4. Lo que encontramos

| Hallazgo | Dato |
|---|---|
| **Perú fue el que más mejoró** | Su PIB por persona se **duplicó** (+3,1 % al año). Le siguen Colombia (+2,3 %) y Chile (+2,3 %) |
| **México casi no avanzó** | +0,3 % al año; en 2023 apenas estaba un 7 % por encima de 2000 |
| **Argentina es un caso aparte** | Su crecimiento fue el más inestable (oscila el doble que en la mayoría) y su inflación mediana en 2018-2023 fue del **51 %**, contra 0,2 %–8 % en los demás |
| **Los países más pobres crecieron más rápido** | Hay una relación clara en la región (aunque son solo 10 países) |
| **Más crecimiento, menos desempleo** | Por cada punto extra de crecimiento, el desempleo baja unos 0,18 puntos. Es una relación moderada |
| **Las crisis golpearon distinto** | En 2009, México (−6,3 %) y Argentina (−5,9 %) cayeron fuerte; Uruguay (+4,2 %) y Bolivia (+3,4 %) siguieron creciendo. En 2020, Bolivia (−12,7 %) y Perú (−10,9 %) sufrieron más y Paraguay casi nada (−0,8 %) |
| **La recuperación tras la pandemia** | La mayoría recuperó su nivel de 2019 entre 2021 y 2022, México en 2023. Según los datos, Bolivia aún no lo había hecho en 2023 |
| **Inflación y crecimiento** | No se ve una relación directa, salvo que los episodios de inflación extrema son raros y no caben en una recta |

## 5. Límites (lo que no podemos asegurar)

- **Son asociaciones, no causas.** Que dos cosas vayan juntas no prueba que una cause la otra.
- **Pocos países.** Con 10 casos, las conclusiones sobre "los países pobres crecen más" son orientativas.
- **Datos incompletos para Argentina:** la comparación de inflación solo usa 2018-2023.
- **El desempleo es una estimación modelada** (de la OIT), no una medición directa en cada país.
- **El PIB por persona no lo dice todo:** no refleja cómo se reparte la riqueza ni la calidad de vida.

---
**Archivos de este proyecto:** `dashboard.html` (el tablero), `fetch_data.py` (descarga), `analysis.py` (el análisis, comentado), `build_dashboard.py` (genera el tablero), `data/` y `output/`.
