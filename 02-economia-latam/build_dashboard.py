"""
Genera dashboard.html del PROYECTO 2 (economía de América Latina).

Lee output/resultados.json (lo crea analysis.py) y lo inserta en una plantilla HTML.
Cómo ejecutarlo:
    python fetch_data.py       # descarga los datos del Banco Mundial
    python analysis.py         # calcula resultados
    python build_dashboard.py  # crea dashboard.html
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
datos = json.loads((ROOT / "output" / "resultados.json").read_text(encoding="utf-8"))

HTML = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economía de América Latina 2000-2023</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mute:#667085;--line:#e4e7ec;--a:#2a6fdb;--b:#c3cad5;--warn:#c0392b}
@media (prefers-color-scheme:dark){:root{--bg:#10151c;--card:#171e28;--ink:#e8ecf2;--mute:#97a3b4;--line:#263041;--a:#5b94f0;--b:#3a4558;--warn:#e5675a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:26px;margin:0 0 4px}h3{font-size:14px;margin:0 0 8px;color:var(--mute);font-weight:600}
.sub{color:var(--mute);margin:0 0 20px}
.story{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px;margin-bottom:16px}
.story .card{font-size:14px}.story b{display:block;font-size:12px;color:var(--a);letter-spacing:.04em;text-transform:uppercase;margin-bottom:4px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px}
.kpi,.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.kpi b{display:block;font-size:24px}.kpi span{color:var(--mute);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:16px;margin-bottom:16px}
.chart{position:relative;height:300px}
.insights{margin:0;padding-left:18px}.insights li{margin:6px 0}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}th{color:var(--mute);font-weight:600}
.note{font-size:13px;color:var(--mute)}
</style></head><body><div class="wrap">
<h1>Crecimiento, inflación y empleo en América Latina</h1>
<p class="sub">10 países, 2000–2023 · Indicadores del Banco Mundial (API pública). Convergencia, volatilidad, ley de Okun y choques de 2009 y 2020.</p>
<div class="story">
 <div class="card"><b>Los datos</b>Indicadores públicos del Banco Mundial para 10 países de América Latina (Argentina, Bolivia, Brasil, Chile, Colombia, Ecuador, México, Paraguay, Perú y Uruguay) entre 2000 y 2023.</div>
 <div class="card"><b>La pregunta</b>¿Qué países crecieron más, con qué estabilidad, y cómo resistieron las dos grandes crisis del período: la financiera de 2009 y la pandemia de 2020?</div>
 <div class="card"><b>Cómo se respondió</b>Se comparó el crecimiento del PIB por persona, cuánto oscila de un año a otro, la relación con el desempleo y la inflación, y el golpe y la recuperación tras cada crisis.</div>
</div>
<div class="kpis" id="k"></div>
<div class="card" style="margin-bottom:16px"><h3>Hallazgos</h3><ul class="insights" id="ins"></ul></div>
<div class="grid">
 <div class="card"><h3>PIB per cápita PPA (2000 = 100) · toca la leyenda para ocultar países</h3><div class="chart"><canvas id="c_idx"></canvas></div></div>
 <div class="card"><h3>Crecimiento medio vs. volatilidad</h3><div class="chart"><canvas id="c_sc"></canvas></div></div>
</div>
<div class="grid">
 <div class="card"><h3>Caída del PIB: 2009 vs. 2020 (% anual)</h3><div class="chart"><canvas id="c_shock"></canvas></div></div>
 <div class="card"><h3>Resumen por país</h3><div id="tab" style="overflow:auto"></div></div>
</div>
<div class="card"><h3>Calidad de datos y límites</h3><div id="q" class="note"></div></div>
</div>
<script>
const P2 = __DATOS__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fmt = (n, d = 0) => n.toLocaleString('es-ES', {maximumFractionDigits: d, minimumFractionDigits: d});
const $ = id => document.getElementById(id);

// ---- Textos y tablas ----
const S = P2.summary, by = Object.fromEntries(S.map(x => [x.country, x])), st = P2.stats;
$('k').innerHTML = [['10','países'],['24','años (2000–2023)'],[st.okun_slope.toFixed(2)+' pp','desempleo por cada +1 pp de PIB'],[st.convergence_r.toFixed(2),'correlación de convergencia'],[P2.quality.cobertura_pct+'%','cobertura de datos']]
 .map(([v,l]) => `<div class="kpi"><b>${v}</b><span>${l}</span></div>`).join('');
$('ins').innerHTML = [
 `<b>Perú lidera el crecimiento per cápita</b> (${by['Perú'].cagr_pib_pc}% anual), seguido de Colombia y Chile. <b>México</b> apenas avanzó (${by['México'].cagr_pib_pc}% anual): su PIB per cápita en 2023 es solo ~7 % mayor que en 2000.`,
 `<b>Argentina es el caso atípico:</b> volatilidad del crecimiento de ${by.Argentina.volatilidad} pp (casi el doble que la mayoría, ~3,3) e inflación mediana de ${by.Argentina.inflacion_mediana_2018_23}% en 2018–23, frente a 0,2–8 % en el resto.`,
 `<b>Convergencia:</b> los países más pobres en 2000 crecieron más rápido (r = ${st.convergence_r}, n = 10 países; muestra pequeña, interpretar con cautela).`,
 `<b>Ley de Okun:</b> +1 pp de crecimiento se asocia con ${st.okun_slope} pp de desempleo (r = ${st.okun_r}, n = ${st.okun_n} país-años, sin 2020). Relación moderada.`,
 `<b>Choques:</b> en 2009 varios países ni se contrajeron (Uruguay +4,2 %, Bolivia +3,4 %), pero México (−6,3 %) y Argentina (−5,9 %) cayeron fuerte. En 2020 Bolivia (−12,7 %) y Perú (−10,9 %) sufrieron más; Paraguay casi nada (−0,8 %).`,
 `<b>Inflación y crecimiento:</b> sin relación lineal visible (r = ${st.infl_growth_r}, excluyendo inflación ≥ 50 %): la correlación no capta el efecto de los episodios extremos.`
].map(t => `<li>${t}</li>`).join('');
const tb = (rows, h) => '<table><tr>' + h.map(x => `<th>${x}</th>`).join('') + '</tr>' + rows.map(r => '<tr>' + r.map(x => `<td>${x}</td>`).join('') + '</tr>').join('') + '</table>';
$('tab').innerHTML = tb(S.map(x => [x.country, fmt(x.pib_pc_2023), x.cagr_pib_pc+'%', x.crec_medio+'%', x.volatilidad, x.desempleo_medio+'%', x.inflacion_mediana_2018_23+'%']),
 ['País','PIB pc 2023 (PPA)','CAGR pc','Crec. medio','Vol.','Desempleo','Infl. med. 18–23']);
$('q').innerHTML = `Fuente: Banco Mundial (indicadores NY.GDP.MKTP.KD.ZG, FP.CPI.TOTL.ZG, SL.UEM.TOTL.ZS, NY.GDP.PCAP.PP.KD). Argentina no tiene inflación publicada para 2000–2017 (${P2.quality.argentina_inflacion_faltante} años), así que la comparación de inflación usa 2018–2023. La deuda pública se descartó por cobertura insuficiente. El desempleo es una estimación modelada de la OIT; los resultados son asociaciones, no causalidad.`;

// ---- Gráficos ----
let charts = [];
function dibujar() {
 charts.forEach(c => c.destroy()); charts = [];
 const ink = css('--ink'), A = css('--a'), B = css('--b'), W = css('--warn');
 Chart.defaults.color = css('--mute'); Chart.defaults.borderColor = css('--line'); Chart.defaults.font.size = 11;
 const base = {maintainAspectRatio: false, animation: false};
 const pal = {Chile:'#2a6fdb', Perú:'#e0792a', Uruguay:'#1f9d6b', Argentina:'#c0392b', México:'#8e44ad'};
 const names = Object.keys(P2.series);
 charts.push(new Chart($('c_idx'), {type: 'line',
  data: {labels: P2.series.Chile.years, datasets: names.map(n => ({label: n, data: P2.series[n].idx, borderColor: pal[n] || B, backgroundColor: pal[n] || B, borderWidth: pal[n] ? 2.4 : 1.2, pointRadius: 0, tension: .2}))},
  options: {...base, plugins: {legend: {position: 'bottom', labels: {boxWidth: 10}}}, scales: {y: {title: {display: true, text: '2000 = 100'}}}}}));
 charts.push(new Chart($('c_sc'), {type: 'scatter',
  data: {datasets: [{data: S.map(x => ({x: x.volatilidad, y: x.crec_medio, n: x.country})), backgroundColor: A, pointRadius: 6}]},
  options: {...base, layout: {padding: {right: 56}}, plugins: {legend: {display: false}, tooltip: {callbacks: {label: c => `${c.raw.n}: crec. ${c.raw.y}% · vol. ${c.raw.x}`}}},
   scales: {x: {title: {display: true, text: 'Volatilidad (desv. est., pp)'}}, y: {title: {display: true, text: 'Crecimiento medio (%)'}}}},
  plugins: [{id: 'etiquetas', afterDatasetsDraw(ch) { const c = ch.ctx; c.save(); c.fillStyle = ink; c.font = '11px system-ui';
   ch.getDatasetMeta(0).data.forEach((p, i) => c.fillText(S[i].country, p.x + 8, p.y + 4)); c.restore(); }}]}));
 charts.push(new Chart($('c_shock'), {type: 'bar',
  data: {labels: names, datasets: [{label: '2009', data: names.map(c => P2.shock09[c].caida), backgroundColor: B}, {label: '2020', data: names.map(c => P2.shock20[c].caida), backgroundColor: W}]},
  options: {...base, plugins: {legend: {position: 'bottom', labels: {boxWidth: 10}}}}}));
}
dibujar();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', dibujar);
</script></body></html>"""

salida = HTML.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
(ROOT / "dashboard.html").write_text(salida, encoding="utf-8")
print("dashboard.html generado:", len(salida) // 1024, "KB")
