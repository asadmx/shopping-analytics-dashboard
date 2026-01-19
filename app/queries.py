TOTALS = """
SELECT
  COUNT(*) AS total_orders,
  SUM(quantity * price * (1 - discount_pct/100.0)) AS revenue,
  AVG(quantity * price * (1 - discount_pct/100.0)) AS avg_order_value,
  AVG(discount_pct) AS avg_discount
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date;
"""

REVENUE_BY_CATEGORY = """
SELECT category,
       SUM(quantity * price * (1 - discount_pct/100.0)) AS revenue
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date
GROUP BY category
ORDER BY revenue DESC;
"""

REVENUE_BY_GENDER = """
SELECT gender,
       SUM(quantity * price * (1 - discount_pct/100.0)) AS revenue
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date
GROUP BY gender
ORDER BY revenue DESC;
"""

TOP_ITEMS = """
SELECT item,
       SUM(quantity) AS units_sold,
       SUM(quantity * price * (1 - discount_pct/100.0)) AS revenue
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date
GROUP BY item
ORDER BY revenue DESC
LIMIT :limit;
"""

SUBSCRIPTION_SPLIT = """
SELECT subscription,
       SUM(quantity * price * (1 - discount_pct/100.0)) AS revenue
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date
GROUP BY subscription
ORDER BY revenue DESC;
"""
