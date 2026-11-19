# ¿De quién depende realmente nuestra tienda online?
### La historia del Proyecto 1, contada sin tecnicismos

## 1. La empresa

Los datos vienen de una **tienda online del Reino Unido, sin local físico**, que vende **regalos originales para toda ocasión**. Muchos de sus clientes son **mayoristas** (otras tiendas que compran en cantidad).

Usamos sus ventas reales entre el **1 de diciembre de 2010 y el 9 de diciembre de 2011**: 541.909 líneas de venta. Son datos públicos de la Universidad de California, Irvine (UCI). La empresa no revela su nombre.

## 2. El desafío

> *Este desafío lo planteamos nosotros como ejercicio de análisis: la empresa no nos encargó nada. Es el tipo de pregunta que haría cualquier negocio con estos datos.*

La tienda vende bien, pero no sabe **de quién depende**. Nos propusimos responder cuatro preguntas:

1. ¿Todos los clientes aportan lo mismo, o unos pocos sostienen el negocio?
2. ¿Hay épocas del año en que hay que estar más preparados?
3. ¿Los clientes nuevos vuelven a comprar?
4. ¿A qué clientes conviene cuidar o intentar recuperar?

El objetivo final: decidir **dónde poner el tiempo y el dinero de marketing**.

## 3. Cómo lo completamos

**Paso 1: limpiar.** Los datos en bruto traen errores. Quitamos duplicados, devoluciones, ventas que luego se anularon, cargos que no son productos (envíos, comisiones bancarias) y líneas sin cliente identificado. De 541.909 líneas, usamos 388.067 (el 71,6 %). La mayor parte de lo descartado son compras sin cliente registrado: sin saber quién compró, no se puede estudiar a los clientes.

**Paso 2: ordenar.** Pusimos los datos limpios en una base de datos y las consultamos con SQL (el lenguaje estándar para preguntarle cosas a una base de datos).

**Paso 3: agrupar a los clientes.** A cada cliente le miramos tres cosas: *cuándo compró por última vez*, *cuántas veces compró* y *cuánto gastó en total*. Con eso los dividimos en seis grupos: estrella, fieles, que se alejan, dormidos, ocasionales y nuevos. (En el código esto se llama análisis RFM.)

**Paso 4: medir cuántos vuelven.** Agrupamos a los clientes según el mes de su primera compra y vimos qué porcentaje seguía comprando meses después.

**Paso 5: contarlo.** Armamos un tablero visual (`dashboard.html`) pensado para leerse sin conocimientos técnicos.

## 4. Lo que encontramos

| Hallazgo | Dato |
|---|---|
| **Pocos clientes sostienen el negocio** | 1.123 clientes "estrella" (26 % del total) generan el **69 %** de las ventas |
| **Las ventas se disparan en otoño** | En noviembre de 2011 se vendió más del doble que en febrero; el aumento empieza en septiembre |
| **La mayoría de clientes nuevos no vuelve** | Solo **1 de cada 5** compra de nuevo al mes siguiente (promedio 19,7 %) |
| **Hay clientes que se están yendo** | 644 clientes con varias compras llevan unos 148 días sin volver; suman el 10 % de las ventas |
| **Todo depende del Reino Unido** | El 82 % de las ventas; fuera de allí hay pocos clientes, pero algunos mayoristas compran mucho |

## 5. Qué recomendamos

1. **Cuidar a los clientes estrella** con trato preferente: es lo más valioso del negocio.
2. **Recuperar a los clientes que se alejan** con mensajes personalizados: es más barato que conseguir clientes nuevos.
3. **Prepararse para el otoño** planificando stock y campañas desde agosto.
4. **Lograr la segunda compra** con una oferta o recordatorio tras la primera compra.
5. **Probar con mayoristas en el extranjero** con una acción pequeña antes de invertir más (es una hipótesis, no una certeza).

## 6. Límites (lo que no podemos asegurar)

- Es **un solo año** de datos y diciembre de 2011 está incompleto. La estacionalidad se basa en una única temporada.
- Los datos muestran **asociaciones, no causas**: las recomendaciones son hipótesis que conviene probar.
- Las cifras corresponden a **clientes identificados**; las ventas sin cliente registrado quedaron fuera.

---
**Archivos de este proyecto:** `dashboard.html` (el tablero), `analysis.py` (el análisis, comentado), `queries.sql` (las consultas), `build_dashboard.py` (genera el tablero) y `output/` (gráficos y resultados).
