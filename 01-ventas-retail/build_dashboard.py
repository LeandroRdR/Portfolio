"""
Genera dashboard.html del PROYECTO 1 (pensado para un público NO técnico).

Qué hace:
    1. Lee los resultados que dejó analysis.py (output/resultados.json).
    2. Calcula un dato extra: cuántos clientes nuevos vuelven a comprar con los meses.
    3. Inserta todo en una plantilla HTML y guarda dashboard.html.

Cómo ejecutarlo (primero analysis.py, luego este):
    python analysis.py
    python build_dashboard.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
datos = json.loads((ROOT / "output" / "resultados.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# Dato extra: retención media por meses transcurridos desde la primera compra
# ---------------------------------------------------------------------------
# Para cada "cohorte" (clientes que compraron por primera vez en un mes) tenemos
# el % que sigue activo 1, 2, 3... meses después. Aquí promediamos entre cohortes.
# Reglas para que el dato sea justo:
#   - Se excluye la cohorte de dic-2010: incluye clientes que ya existían antes.
#   - Se excluyen los valores que caen en dic-2011, porque ese mes está incompleto
#     (los datos llegan solo hasta el día 9) y daría una falsa caída.
ret = datos["retention"]
suma, cuenta = {}, {}
for cohorte, fila in zip(ret["cohorts"], ret["values"]):
    if cohorte == "2010-12":
        continue
    anio, mes = int(cohorte[:4]), int(cohorte[5:])
    for k, valor in enumerate(fila):
        if k == 0 or valor is None:
            continue
        mes_calendario = (anio * 12 + mes - 1) + k          # mes absoluto
        if mes_calendario == 2011 * 12 + 11:                # = dic-2011 (parcial)
            continue
        suma[k] = suma.get(k, 0) + valor
        cuenta[k] = cuenta.get(k, 0) + 1
# Solo mostramos los meses con al menos 3 cohortes, para que el promedio sea fiable
datos["retencion_media"] = [
    {"mes": k, "pct": round(suma[k] / cuenta[k], 1)} for k in sorted(suma) if cuenta[k] >= 3
]

# ---------------------------------------------------------------------------
# Plantilla HTML (el código JavaScript dibuja los gráficos con Chart.js)
# ---------------------------------------------------------------------------
HTML = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quién sostiene las ventas de la tienda</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mute:#5b6676;--line:#e4e7ec;--a:#2a6fdb;--soft:#c3cad5;--warn:#c0392b;--hl:#eaf1fd}
@media (prefers-color-scheme:dark){:root{--bg:#10151c;--card:#171e28;--ink:#e8ecf2;--mute:#a1adbd;--line:#263041;--a:#5b94f0;--soft:#3a4558;--warn:#e5675a;--hl:#1a2740}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:28px 16px 72px}
h1{font-size:32px;line-height:1.2;margin:0 0 8px}
h2{font-size:23px;line-height:1.3;margin:36px 0 6px}
h3{font-size:15px;margin:0 0 10px;color:var(--mute);font-weight:600}
p{margin:0 0 12px}.lead{font-size:19px;color:var(--mute)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.story{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:14px}
.story .card{margin:0}.story b{display:block;font-size:13px;color:var(--a);letter-spacing:.04em;text-transform:uppercase;margin-bottom:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.kpi strong{display:block;font-size:30px;line-height:1.1}.kpi span{color:var(--mute);font-size:15px}
.chart{position:relative;height:300px}
.big{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.big .num{font-size:56px;font-weight:700;color:var(--a);line-height:1}
.seg{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:12px;margin-top:14px}
.seg div{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--card)}
.seg b{display:block}.seg small{color:var(--mute);display:block;margin-top:2px;font-size:14px}
.rec{display:grid;gap:12px}.rec .card{margin:0;border-left:5px solid var(--a)}
.rec b{font-size:18px}.rec .why{color:var(--mute);font-size:15px;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:15px}td,th{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}th{color:var(--mute);font-weight:600}
.note{font-size:14px;color:var(--mute)}
</style></head><body><div class="wrap">

<h1>¿De quién depende realmente nuestra tienda online?</h1>
<p class="lead">Análisis de un año de ventas de una tienda online británica de regalos: quién compra, cuándo, y a qué clientes conviene cuidar o recuperar.</p>

<div class="story">
 <div class="card"><b>La empresa</b>Tienda online del Reino Unido, sin local físico, que vende <u>regalos originales para toda ocasión</u>. Muchos de sus clientes son mayoristas. Usamos sus ventas reales entre el 1 de diciembre de 2010 y el 9 de diciembre de 2011 (datos públicos de la Universidad de California, Irvine; la empresa no revela su nombre).</div>
 <div class="card"><b>El desafío</b>La tienda vende bien, pero no sabe <u>de quién depende</u>. ¿Todos los clientes aportan lo mismo? ¿Cuándo hay que prepararse? ¿A quién estamos perdiendo? Hay que decidir dónde poner el tiempo y el dinero de marketing.</div>
 <div class="card"><b>Cómo lo resolvimos</b>1. Limpiamos los datos (quitamos errores, devoluciones y duplicados).<br>2. Los ordenamos en una base de datos.<br>3. Agrupamos a los clientes según <u>cuándo compraron por última vez, cuántas veces y cuánto gastaron</u>.<br>4. Medimos cuántos clientes vuelven.</div>
</div>

<div class="kpis" id="kpis"></div>

<h2 id="t1"></h2>
<p id="p1"></p>
<div class="card"><h3>Porcentaje de clientes y porcentaje de ventas de cada grupo</h3><div class="chart"><canvas id="c_seg"></canvas></div></div>
<div class="seg" id="seg"></div>

<h2 id="t2"></h2>
<p id="p2"></p>
<div class="card"><h3>Ventas de cada mes (miles de libras)</h3><div class="chart"><canvas id="c_month"></canvas></div>
<p class="note">En gris, diciembre de 2011: los datos llegan solo hasta el día 9, por eso parece bajo.</p></div>

<h2 id="t3"></h2>
<p id="p3"></p>
<div class="card"><div class="big"><div class="num" id="ret1"></div><div id="ret1t"></div></div>
<div class="chart" style="height:240px;margin-top:14px"><canvas id="c_ret"></canvas></div>
<h3 style="margin-top:8px">De cada 100 clientes nuevos, cuántos compran de nuevo en cada mes posterior a su primera compra</h3></div>

<h2>¿Dónde y qué se vende?</h2>
<div class="card" id="geo"></div>
<div class="card"><h3>Los 10 productos que más dinero dejaron</h3><div id="prod"></div></div>

<h2>Qué recomendamos hacer</h2>
<div class="rec" id="rec"></div>

<h2>Lo que hay que tener en cuenta</h2>
<div class="card note" id="lim"></div>
<p class="note">Fuente de los datos: Online Retail (UCI Machine Learning Repository). Análisis hecho con Python y SQL. Todas las cifras son ventas netas (sin devoluciones) de clientes identificados.</p>
</div>

<script>
const D = __DATOS__;                         // resultados del análisis
const num = (n, d = 0) => n.toLocaleString('es-ES', {maximumFractionDigits: d, minimumFractionDigits: d});
const libras = n => '£' + num(n);
const nombreMes = m => ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'][+m.slice(5) - 1] + ' ' + m.slice(2, 4);
const $ = id => document.getElementById(id);

// Nombres sencillos para los grupos de clientes (en el análisis se llaman Campeones, Leales, etc.)
const GRUPOS = {
 'Campeones':            ['Clientes estrella',          'Compran seguido y compraron hace muy poco.'],
 'Leales':               ['Clientes fieles',            'Compran con regularidad y siguen activos.'],
 'En riesgo':            ['Clientes que se alejan',     'Compraban bastante, pero llevan meses sin volver.'],
 'Hibernando':           ['Clientes dormidos',          'Compraron una o dos veces y hace mucho que no vuelven.'],
 'Necesitan atención':   ['Clientes ocasionales',       'Compran poco y no muy recientemente.'],
 'Nuevos / prometedores':['Clientes nuevos',            'Llegaron hace poco y han comprado pocas veces.']
};
const seg = D.segments.map(s => ({...s, nombre: GRUPOS[s.segment][0], desc: GRUPOS[s.segment][1]}));
const grupo = k => seg.find(s => s.segment === k);
const k = D.kpis, estrella = grupo('Campeones'), alejan = grupo('En riesgo'), dormidos = grupo('Hibernando');
const mes = Object.fromEntries(D.monthly.map(m => [m.month, m.revenue]));
const r1 = D.retencion_media.find(r => r.mes === 1).pct;
const uk = D.countries.find(c => c.country === 'United Kingdom');

// Cifras destacadas
$('kpis').innerHTML = [
 [num(k.revenue / 1e6, 1) + ' M£', 'vendidos en el período'],
 [num(k.customers), 'clientes distintos'],
 [num(k.orders), 'pedidos realizados'],
 [libras(k.aov), 'gasto medio por pedido']
].map(([v, l]) => `<div class="kpi"><strong>${v}</strong><span>${l}</span></div>`).join('');

// Sección 1: concentración de clientes
$('t1').textContent = `Pocos clientes sostienen casi todo el negocio`;
$('p1').innerHTML = `Los <b>${num(estrella.customers)} “clientes estrella”</b> son solo el <b>${num(estrella.customer_share)}%</b> de los clientes, pero generan el <b>${num(estrella.revenue_share)}%</b> de las ventas. Dicho de otra forma: si perdiéramos a este grupo, las ventas se reducirían a menos de la mitad. En cambio, los <b>${num(dormidos.customers)} clientes dormidos</b> son el ${num(dormidos.customer_share)}% de la base y aportan apenas el ${num(dormidos.revenue_share)}%.`;
$('seg').innerHTML = seg.map(s => `<div><b>${s.nombre}</b><span>${num(s.customers)} clientes · ${libras(s.revenue)}</span><small>${s.desc}${s.segment==='En riesgo' ? ' Llevan en promedio ' + num(s.avg_recency) + ' días sin comprar.' : ''}</small></div>`).join('');

// Sección 2: estacionalidad
$('t2').textContent = `Las ventas se disparan en otoño`;
$('p2').innerHTML = `Entre septiembre y noviembre la tienda vende mucho más que el resto del año. En <b>noviembre de 2011</b> se vendieron <b>${libras(mes['2011-11'])}</b>, más del doble que en febrero (${libras(mes['2011-02'])}). Es la temporada de compras para las fiestas, y conviene llegar preparados.`;

// Sección 3: retención
$('t3').textContent = `La mayoría de los clientes nuevos no vuelve`;
$('p3').innerHTML = `Cuando alguien compra por primera vez, <b>solo uno de cada cinco vuelve a comprar al mes siguiente</b>. Conseguir esa segunda compra es una de las formas más baratas de hacer crecer las ventas.`;
$('ret1').textContent = num(r1) + '%';
$('ret1t').innerHTML = `de los clientes nuevos <b>vuelve a comprar al mes siguiente</b>.<br><span class="note">Aun así, ${num(k.repeat_rate)}% de todos los clientes compró más de una vez a lo largo del año.</span>`;

// Dónde y qué se vende
$('geo').innerHTML = `<h3>Dónde se vende</h3><p>El <b>${num(k.uk_share)}%</b> de las ventas viene del Reino Unido. Fuera de allí hay pocos clientes, pero algunos son mayoristas que compran mucho: por ejemplo, los 9 clientes de Países Bajos gastan unas <b>${libras(D.countries.find(c => c.country==='Netherlands').avg_order_value)}</b> por pedido, contra ${libras(uk.avg_order_value)} en el Reino Unido.</p>`;
$('prod').innerHTML = '<table><tr><th>Producto</th><th>Unidades</th><th>Ventas</th></tr>' + D.top_products.map(p => `<tr><td>${p.description.charAt(0) + p.description.slice(1).toLowerCase()}</td><td>${num(p.units)}</td><td>${libras(p.revenue)}</td></tr>`).join('') + '</table>';

// Recomendaciones
const recs = [
 ['Cuidar a los clientes estrella', `Son ${num(estrella.customers)} clientes que aportan el ${num(estrella.revenue_share)}% de las ventas. Un trato preferente (atención directa, avisos de novedades, condiciones especiales) protege lo más valioso del negocio.`],
 ['Recuperar a los clientes que se alejan', `Hay ${num(alejan.customers)} clientes que ya compraron varias veces (${libras(alejan.revenue)} en total) y llevan unos ${num(alejan.avg_recency)} días sin volver. Un mensaje personalizado ahora es mucho más barato que conseguir clientes nuevos.`],
 ['Prepararse para el otoño', `Las ventas empiezan a subir en septiembre. Planificar stock y campañas desde agosto evita quedarse sin producto en los meses más fuertes.`],
 ['Lograr la segunda compra', `Cuatro de cada cinco clientes nuevos no vuelven al mes siguiente. Una oferta o un recordatorio tras la primera compra puede cambiar eso.`],
 ['Explorar mayoristas en el extranjero', `Pocos clientes fuera del Reino Unido hacen pedidos muy grandes. Es una hipótesis que conviene probar con una acción comercial pequeña antes de invertir más.`]
];
$('rec').innerHTML = recs.map(([t, w], i) => `<div class="card"><b>${i + 1}. ${t}</b><div class="why">${w}</div></div>`).join('');

// Límites
const q = D.calidad;
$('lim').innerHTML = `<ul style="margin:0;padding-left:20px"><li>Se analizaron ${num(q.filas_limpias)} de ${num(q.filas_originales)} líneas de venta (${num(q.porcentaje_conservado, 1)}%). La mayor parte de lo descartado (${num(q.sin_customer_id)} líneas) no tenía cliente identificado, y sin eso no se puede estudiar el comportamiento de cada cliente.</li><li>También se quitaron duplicados, devoluciones, ventas anuladas y cargos que no son productos (envíos, comisiones).</li><li>Es un solo año de datos y diciembre de 2011 está incompleto; las conclusiones sobre estacionalidad se basan en una única temporada.</li><li>Los grupos de clientes muestran asociaciones, no causas: las recomendaciones son hipótesis a probar.</li></ul>`;

// ----- Gráficos -----
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
let charts = [];
function dibujar() {
 charts.forEach(c => c.destroy()); charts = [];
 const A = css('--a'), S = css('--soft');
 Chart.defaults.color = css('--mute'); Chart.defaults.borderColor = css('--line'); Chart.defaults.font.size = 13;
 const base = {maintainAspectRatio: false, animation: false};
 const orden = [...seg].sort((a, b) => b.revenue_share - a.revenue_share);
 charts.push(new Chart($('c_seg'), {type: 'bar',
  data: {labels: orden.map(s => s.nombre), datasets: [
   {label: '% de los clientes', data: orden.map(s => s.customer_share), backgroundColor: S},
   {label: '% de las ventas', data: orden.map(s => s.revenue_share), backgroundColor: A}]},
  options: {...base, indexAxis: 'y', plugins: {legend: {position: 'bottom'}, tooltip: {callbacks: {label: c => `${c.dataset.label}: ${num(c.raw)}%`}}}, scales: {x: {ticks: {callback: v => v + '%'}}}}}));
 charts.push(new Chart($('c_month'), {type: 'bar',
  data: {labels: D.monthly.map(m => nombreMes(m.month)), datasets: [{data: D.monthly.map(m => m.revenue / 1e3),
   backgroundColor: D.monthly.map(m => m.partial ? S : A)}]},
  options: {...base, plugins: {legend: {display: false}, tooltip: {callbacks: {label: c => '£' + num(c.raw) + ' mil'}}}}}));
 charts.push(new Chart($('c_ret'), {type: 'bar',
  data: {labels: D.retencion_media.map(r => 'Mes ' + r.mes), datasets: [{data: D.retencion_media.map(r => r.pct), backgroundColor: A}]},
  options: {...base, plugins: {legend: {display: false}, tooltip: {callbacks: {label: c => num(c.raw) + ' de cada 100'}}}, scales: {y: {beginAtZero: true, title: {display: true, text: 'de cada 100 clientes'}}}}}));
}
dibujar();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', dibujar);
</script></body></html>"""

# Insertamos los datos en la plantilla y guardamos el archivo final
salida = HTML.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
(ROOT / "dashboard.html").write_text(salida, encoding="utf-8")
print("dashboard.html generado:", len(salida) // 1024, "KB")
print("Retención media por mes:", datos["retencion_media"])
