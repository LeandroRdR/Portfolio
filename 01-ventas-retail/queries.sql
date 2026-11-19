-- Proyecto 1: Análisis de ventas y segmentación de clientes (Online Retail, UCI)
-- Tabla base: sales (ventas limpias, sin cancelaciones, con revenue = quantity * unit_price)

-- Q1. Ingresos mensuales, pedidos y clientes activos
-- name: monthly
SELECT strftime('%Y-%m', invoice_date) AS month,
       ROUND(SUM(revenue), 2)          AS revenue,
       COUNT(DISTINCT invoice_no)      AS orders,
       COUNT(DISTINCT customer_id)     AS customers
FROM sales
GROUP BY month
ORDER BY month;

-- Q2. Ingresos por país y ticket medio
-- name: countries
SELECT country,
       ROUND(SUM(revenue), 2)                                   AS revenue,
       COUNT(DISTINCT customer_id)                              AS customers,
       ROUND(SUM(revenue) * 1.0 / COUNT(DISTINCT invoice_no), 2) AS avg_order_value
FROM sales
GROUP BY country
ORDER BY revenue DESC;

-- Q3. Top 10 productos por ingresos
-- name: top_products
SELECT description,
       SUM(quantity)           AS units,
       ROUND(SUM(revenue), 2)  AS revenue
FROM sales
GROUP BY description
ORDER BY revenue DESC
LIMIT 10;

-- Q4. Retención por cohorte mensual (mes de primera compra vs. meses posteriores)
-- name: cohorts
WITH first_purchase AS (
    SELECT customer_id, MIN(strftime('%Y-%m', invoice_date)) AS cohort
    FROM sales GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, strftime('%Y-%m', invoice_date) AS month FROM sales
)
SELECT f.cohort,
       (CAST(substr(a.month,1,4) AS INT) - CAST(substr(f.cohort,1,4) AS INT)) * 12
       + CAST(substr(a.month,6,2) AS INT) - CAST(substr(f.cohort,6,2) AS INT) AS month_index,
       COUNT(DISTINCT a.customer_id) AS active_customers
FROM first_purchase f
JOIN activity a USING (customer_id)
GROUP BY f.cohort, month_index
ORDER BY f.cohort, month_index;

-- Q5. Segmentación RFM (quintiles con NTILE)
-- name: rfm
WITH ref AS (SELECT DATE(MAX(invoice_date), '+1 day') AS today FROM sales),
base AS (
    SELECT customer_id,
           CAST(julianday((SELECT today FROM ref)) - julianday(MAX(invoice_date)) AS INT) AS recency,
           COUNT(DISTINCT invoice_no) AS frequency,
           ROUND(SUM(revenue), 2)     AS monetary
    FROM sales GROUP BY customer_id
)
SELECT customer_id, recency, frequency, monetary,
       NTILE(5) OVER (ORDER BY recency DESC)   AS r,
       NTILE(5) OVER (ORDER BY frequency ASC)  AS f,
       NTILE(5) OVER (ORDER BY monetary ASC)   AS m
FROM base;
