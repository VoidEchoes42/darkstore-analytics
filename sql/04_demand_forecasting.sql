-- =============================================================================
-- SQL Module 04: Demand Forecasting Support
-- =============================================================================
-- Key Questions:
--   - Hourly demand by store + SKU (input for Python Prophet models)
--   - Day-of-week patterns, peak hours
--   - Stockout detection
--   - Overstock identification
--   - Market basket (products bought together)
-- =============================================================================

-- ============================================================
-- Q4.1: Hourly demand aggregation by store + SKU
-- This is the PRIMARY input for Python Prophet forecasting
-- ============================================================
SELECT
    o.store_id,
    oi.product_id,
    p.product_name,
    c.category_name,
    DATE(o.order_placed_at)                          AS order_date,
    EXTRACT(HOUR FROM o.order_placed_at)             AS hour_of_day,
    COUNT(DISTINCT o.order_id)                       AS orders,
    SUM(oi.quantity)                                 AS units_sold,
    ROUND(SUM(oi.total_price), 2)                    AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories c ON c.category_id = p.category_id
WHERE o.order_status = 'delivered'
GROUP BY o.store_id, oi.product_id, p.product_name, c.category_name,
         DATE(o.order_placed_at), EXTRACT(HOUR FROM o.order_placed_at)
ORDER BY o.store_id, oi.product_id, order_date, hour_of_day;

-- ============================================================
-- Q4.2: Day-of-week demand patterns (aggregate)
-- ============================================================
SELECT
    o.store_id,
    TO_CHAR(o.order_placed_at, 'Day')                AS day_name,
    EXTRACT(DOW FROM o.order_placed_at)               AS dow_num,
    EXTRACT(HOUR FROM o.order_placed_at)              AS hour_of_day,
    COUNT(*)                                          AS orders,
    ROUND(SUM(oi.total_price), 2)                     AS revenue,
    ROUND(AVG(oi.total_price), 2)                     AS aov
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.store_id, TO_CHAR(o.order_placed_at, 'Day'),
         EXTRACT(DOW FROM o.order_placed_at),
         EXTRACT(HOUR FROM o.order_placed_at)
ORDER BY o.store_id, dow_num, hour_of_day;

-- ============================================================
-- Q4.3: Peak hour identification per store
-- ============================================================
WITH hourly AS (
    SELECT
        store_id,
        EXTRACT(HOUR FROM order_placed_at) AS hour_of_day,
        COUNT(*) AS orders
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY store_id, EXTRACT(HOUR FROM order_placed_at)
)
SELECT
    store_id,
    hour_of_day,
    orders,
    ROUND(
        orders::NUMERIC / NULLIF(SUM(orders) OVER (PARTITION BY store_id), 0) * 100, 2
    ) AS pct_of_daily_orders
FROM hourly
ORDER BY store_id, orders DESC;

-- ============================================================
-- Q4.4: Stockout detection
-- Days when inventory was 0 but demand existed (orders > 0 with 0 stock)
-- ============================================================
SELECT
    psi.store_id,
    psi.product_id,
    p.product_name,
    s.store_name,
    COUNT(DISTINCT o.order_id) AS orders_with_stockout,
    SUM(oi.quantity)           AS lost_units,
    ROUND(SUM(oi.total_price), 2) AS lost_revenue
FROM product_store_inventory psi
JOIN products p ON p.product_id = psi.product_id
JOIN stores s ON s.store_id = psi.store_id
LEFT JOIN orders o
    ON o.store_id = psi.store_id
    AND o.order_placed_at::DATE = psi.last_restocked_at::DATE
    AND o.order_status = 'cancelled'
LEFT JOIN order_items oi ON oi.order_id = o.order_id
WHERE psi.stock_quantity = 0
  AND psi.last_restocked_at IS NOT NULL
GROUP BY psi.store_id, psi.product_id, p.product_name, s.store_name
HAVING COUNT(DISTINCT o.order_id) > 0
ORDER BY lost_revenue DESC;

-- Simpler stockout: products with 0 stock currently at each store
SELECT
    s.store_id,
    s.store_name,
    p.product_id,
    p.product_name,
    c.category_name,
    p.selling_price
FROM product_store_inventory psi
JOIN stores s ON s.store_id = psi.store_id
JOIN products p ON p.product_id = psi.product_id
JOIN categories c ON c.category_id = p.category_id
WHERE psi.stock_quantity = 0
  AND p.is_available = TRUE
ORDER BY s.store_id, c.category_name;

-- ============================================================
-- Q4.5: Overstock identification (products with >30 days of inventory)
-- ============================================================
SELECT
    psi.store_id,
    s.store_name,
    psi.product_id,
    p.product_name,
    c.category_name,
    psi.stock_quantity,
    ROUND(AVG(oi.quantity), 1)                          AS avg_daily_demand,
    ROUND(psi.stock_quantity / NULLIF(AVG(oi.quantity), 0), 0) AS days_of_stock,
    ROUND(psi.stock_quantity * p.cost_price, 2)         AS inventory_value_inr
FROM product_store_inventory psi
JOIN stores s ON s.store_id = psi.store_id
JOIN products p ON p.product_id = psi.product_id
JOIN categories c ON c.category_id = p.category_id
LEFT JOIN order_items oi ON oi.product_id = psi.product_id
LEFT JOIN orders o ON o.order_id = oi.order_id
    AND o.order_status = 'delivered'
    AND o.order_placed_at >= CURRENT_DATE - INTERVAL '14 days'
GROUP BY psi.store_id, s.store_name, psi.product_id,
         p.product_name, c.category_name, psi.stock_quantity,
         p.cost_price
HAVING psi.stock_quantity / NULLIF(AVG(oi.quantity), 0) > 30
   OR psi.stock_quantity > 200
ORDER BY inventory_value_inr DESC;

-- ============================================================
-- Q4.6: Market basket — products frequently bought together
-- ============================================================
WITH product_pairs AS (
    SELECT
        oi1.product_id AS product_a,
        oi2.product_id AS product_b,
        COUNT(DISTINCT oi1.order_id) AS times_bought_together
    FROM order_items oi1
    JOIN order_items oi2
        ON oi1.order_id = oi2.order_id
        AND oi1.product_id < oi2.product_id
    JOIN orders o ON o.order_id = oi1.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi1.product_id, oi2.product_id
)
SELECT
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    c1.category_name AS cat_a,
    c2.category_name AS cat_b,
    pp.times_bought_together
FROM product_pairs pp
JOIN products p1 ON p1.product_id = pp.product_a
JOIN products p2 ON p2.product_id = pp.product_b
JOIN categories c1 ON c1.category_id = p1.category_id
JOIN categories c2 ON c2.category_id = p2.category_id
ORDER BY times_bought_together DESC
LIMIT 30;
