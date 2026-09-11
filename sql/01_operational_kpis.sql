-- =============================================================================
-- SQL Module 01: Operational KPIs
-- =============================================================================
-- Key Questions:
--   - Daily/hourly order volume, GMV, AOV, fulfillment rate
--   - Category revenue mix
--   - Top products
--   - Customer acquisition by channel
-- =============================================================================

-- ============================================================
-- Q1.1: Daily GMV, Orders, AOV per store
-- ============================================================
SELECT
    store_id,
    DATE(order_placed_at) AS order_date,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(oi.total_price), 2)   AS gmv,
    ROUND(AVG(oi.total_price), 2)   AS aov
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND DATE(o.order_placed_at) >= '2023-01-01'
GROUP BY store_id, DATE(order_placed_at)
ORDER BY store_id, order_date;

-- ============================================================
-- Q1.2: Hourly order volume (heatmap data: store × hour of day)
-- ============================================================
SELECT
    store_id,
    EXTRACT(HOUR FROM order_placed_at) AS hour_of_day,
    COUNT(*)                           AS orders,
    ROUND(SUM(oi.total_price), 2)      AS gmv
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY store_id, EXTRACT(HOUR FROM order_placed_at)
ORDER BY store_id, hour_of_day;

-- ============================================================
-- Q1.3: Daily fulfillment rate (delivered / placed)
-- ============================================================
SELECT
    DATE(order_placed_at)                                               AS order_date,
    COUNT(*)                                                            AS total_orders,
    COUNT(*) FILTER (WHERE order_status = 'delivered')                  AS delivered_orders,
    COUNT(*) FILTER (WHERE order_status = 'cancelled')                  AS cancelled_orders,
    ROUND(
        COUNT(*) FILTER (WHERE order_status = 'delivered')::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                                   AS fulfillment_rate_pct
FROM orders
WHERE DATE(order_placed_at) >= '2023-01-01'
GROUP BY DATE(order_placed_at)
ORDER BY order_date;

-- ============================================================
-- Q1.4: Category-wise revenue mix per store
-- ============================================================
SELECT
    o.store_id,
    c.category_name,
    COUNT(DISTINCT o.order_id)                          AS orders,
    ROUND(SUM(oi.total_price), 2)                       AS revenue,
    ROUND(
        SUM(oi.total_price)::NUMERIC
        / NULLIF(SUM(SUM(oi.total_price)) OVER (PARTITION BY o.store_id), 0) * 100, 2
    )                                                    AS pct_of_store_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories c ON c.category_id = p.category_id
WHERE o.order_status = 'delivered'
  AND DATE(o.order_placed_at) >= '2023-01-01'
GROUP BY o.store_id, c.category_name
ORDER BY o.store_id, revenue DESC;

-- ============================================================
-- Q1.5: Top 20 products by volume (units sold)
-- ============================================================
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    SUM(oi.quantity)                         AS total_units_sold,
    ROUND(SUM(oi.total_price), 2)            AS total_revenue,
    COUNT(DISTINCT o.order_id)               AS order_count
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN categories c ON c.category_id = p.category_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_id, p.product_name, c.category_name
ORDER BY total_units_sold DESC
LIMIT 20;

-- ============================================================
-- Q1.6: Top 20 products by revenue
-- ============================================================
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    ROUND(SUM(oi.total_price), 2)            AS total_revenue,
    SUM(oi.quantity)                         AS total_units_sold,
    COUNT(DISTINCT o.order_id)               AS order_count
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN categories c ON c.category_id = p.category_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_id, p.product_name, c.category_name
ORDER BY total_revenue DESC
LIMIT 20;

-- ============================================================
-- Q1.7: Customer acquisition rate by channel
-- ============================================================
SELECT
    acquisition_channel,
    COUNT(*)                                             AS total_customers,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM customers) * 100, 2) AS pct_of_total,
    ROUND(AVG(total_orders), 2)                          AS avg_orders_per_customer,
    ROUND(AVG(total_gmv), 2)                             AS avg_gmv_per_customer
FROM customers
GROUP BY acquisition_channel
ORDER BY total_customers DESC;

-- ============================================================
-- Q1.8: Daily GMV trend (last 30 days overview)
-- ============================================================
SELECT
    DATE(order_placed_at)              AS order_date,
    COUNT(*)                           AS orders,
    ROUND(SUM(oi.total_price), 2)      AS gmv,
    ROUND(AVG(oi.total_price), 2)      AS aov,
    ROUND(AVG(actual_delivery_minutes), 1) AS avg_delivery_min
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND DATE(order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(order_placed_at)
ORDER BY order_date;
