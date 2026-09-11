-- =============================================================================
-- SQL Module 06: Store Utilization
-- =============================================================================
-- Key Questions:
--   - Orders per hour vs capacity
--   - Peak load identification (>90% utilization)
--   - Capacity gap: overloaded vs underutilized stores
--   - Where to open a new store
-- =============================================================================

-- ============================================================
-- Q6.1: Orders per store per hour vs capacity
-- ============================================================
SELECT
    s.store_id,
    s.store_name,
    s.city,
    s.zone,
    s.capacity_orders_per_hour,
    EXTRACT(HOUR FROM o.order_placed_at) AS hour_of_day,
    COUNT(*)                             AS actual_orders,
    ROUND(
        COUNT(*)::NUMERIC / NULLIF(s.capacity_orders_per_hour, 0) * 100, 2
    )                                     AS utilization_pct,
    s.capacity_orders_per_hour - COUNT(*) AS spare_capacity
FROM orders o
JOIN stores s ON s.store_id = o.store_id
WHERE o.order_status = 'delivered'
  AND DATE(o.order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.store_id, s.store_name, s.city, s.zone,
         s.capacity_orders_per_hour, EXTRACT(HOUR FROM o.order_placed_at)
ORDER BY s.store_id, hour_of_day;

-- ============================================================
-- Q6.2: Peak load identification — hours where utilization > 90%
-- ============================================================
WITH hourly_util AS (
    SELECT
        s.store_id,
        s.store_name,
        s.capacity_orders_per_hour,
        EXTRACT(HOUR FROM o.order_placed_at) AS hour_of_day,
        COUNT(*) AS actual_orders
    FROM orders o
    JOIN stores s ON s.store_id = o.store_id
    WHERE o.order_status = 'delivered'
      AND DATE(o.order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY s.store_id, s.store_name, s.capacity_orders_per_hour,
             EXTRACT(HOUR FROM o.order_placed_at)
)
SELECT
    store_id,
    store_name,
    hour_of_day,
    actual_orders,
    capacity_orders_per_hour,
    ROUND(actual_orders::NUMERIC / NULLIF(capacity_orders_per_hour, 0) * 100, 2) AS utilization_pct
FROM hourly_util
WHERE ROUND(actual_orders::NUMERIC / NULLIF(capacity_orders_per_hour, 0) * 100, 2) > 90
ORDER BY utilization_pct DESC;

-- ============================================================
-- Q6.3: Daily capacity gap — overloaded vs underutilized stores
-- ============================================================
WITH daily_orders AS (
    SELECT
        store_id,
        DATE(order_placed_at) AS order_date,
        COUNT(*) AS orders_this_day
    FROM orders
    WHERE order_status = 'delivered'
      AND DATE(order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY store_id, DATE(order_placed_at)
)
SELECT
    s.store_id,
    s.store_name,
    s.city,
    s.zone,
    s.capacity_orders_per_day,
    ROUND(AVG(do.orders_this_day), 0)               AS avg_daily_orders,
    s.capacity_orders_per_day - ROUND(AVG(do.orders_this_day), 0) AS daily_gap,
    ROUND(
        AVG(do.orders_this_day)::NUMERIC / NULLIF(s.capacity_orders_per_day, 0) * 100, 2
    )                                                AS avg_utilization_pct,
    CASE
        WHEN ROUND(AVG(do.orders_this_day), 0) > s.capacity_orders_per_day * 0.9 THEN 'Overloaded'
        WHEN ROUND(AVG(do.orders_this_day), 0) < s.capacity_orders_per_day * 0.5 THEN 'Underutilized'
        ELSE 'Optimal'
    END                                              AS capacity_status
FROM daily_orders do
JOIN stores s ON s.store_id = do.store_id
GROUP BY s.store_id, s.store_name, s.city, s.zone, s.capacity_orders_per_day
ORDER BY avg_utilization_pct DESC;

-- ============================================================
-- Q6.4: Demand density by zone — where to open next store
-- ============================================================
WITH zone_demand AS (
    SELECT
        c.city,
        c.zone,
        COUNT(DISTINCT o.order_id)                          AS total_orders_30d,
        COUNT(DISTINCT o.customer_id)                       AS unique_customers,
        ROUND(SUM(oi.total_price), 2)                       AS gmv_30d,
        ROUND(AVG(oi.total_price), 2)                       AS aov,
        COUNT(DISTINCT s.store_id)                          AS existing_stores
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN stores s ON s.store_id = o.store_id
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND DATE(o.order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY c.city, c.zone
),
store_capacity AS (
    SELECT city, zone, SUM(capacity_orders_per_day) AS total_capacity
    FROM stores
    WHERE is_active = TRUE
    GROUP BY city, zone
)
SELECT
    zd.city,
    zd.zone,
    zd.existing_stores,
    zd.total_orders_30d,
    zd.unique_customers,
    zd.gmv_30d,
    zd.aov,
    COALESCE(sc.total_capacity, 0) AS total_daily_capacity,
    ROUND(
        zd.total_orders_30d::NUMERIC / NULLIF(COALESCE(sc.total_capacity, 0) * 30, 0) * 100, 2
    ) AS demand_vs_capacity_pct
FROM zone_demand zd
LEFT JOIN store_capacity sc ON sc.city = zd.city AND sc.zone = zd.zone
ORDER BY demand_vs_capacity_pct DESC;

-- ============================================================
-- Q6.5: Store-level capacity summary (30-day average)
-- ============================================================
WITH store_hourly AS (
    SELECT
        s.store_id,
        s.store_name,
        s.capacity_orders_per_hour,
        EXTRACT(HOUR FROM o.order_placed_at) AS hour_of_day,
        COUNT(*) AS actual_orders
    FROM orders o
    JOIN stores s ON s.store_id = o.store_id
    WHERE o.order_status = 'delivered'
      AND DATE(o.order_placed_at) >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY s.store_id, s.store_name, s.capacity_orders_per_hour,
             EXTRACT(HOUR FROM o.order_placed_at)
)
SELECT
    store_id,
    store_name,
    MAX(capacity_orders_per_hour)       AS capacity_per_hour,
    MAX(capacity_orders_per_hour) * 12   AS capacity_per_day,
    ROUND(AVG(actual_orders), 0)         AS avg_orders_per_hour,
    ROUND(MAX(actual_orders), 0)         AS peak_orders_per_hour,
    ROUND(
        AVG(actual_orders)::NUMERIC / NULLIF(MAX(capacity_orders_per_hour), 0) * 100, 2
    )                                    AS avg_utilization_pct,
    ROUND(
        MAX(actual_orders)::NUMERIC / NULLIF(MAX(capacity_orders_per_hour), 0) * 100, 2
    )                                    AS peak_utilization_pct
FROM store_hourly
GROUP BY store_id, store_name
ORDER BY avg_utilization_pct DESC;
