-- name: monthly_revenue
SELECT order_month,
       ROUND(SUM(revenue), 2) AS revenue,
       COUNT(*)               AS orders
FROM sales
GROUP BY order_month
ORDER BY order_month;

-- name: revenue_by_city
SELECT city,
       ROUND(SUM(revenue), 2) AS revenue,
       COUNT(*)               AS orders
FROM sales
GROUP BY city
ORDER BY revenue DESC;

-- name: top_products
SELECT product,
       SUM(quantity)          AS units_sold,
       ROUND(SUM(revenue), 2) AS revenue
FROM sales
GROUP BY product
ORDER BY revenue DESC;

-- name: top_customers
SELECT customer_id,
       COUNT(*)               AS orders,
       ROUND(SUM(revenue), 2) AS revenue
FROM sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 5;
