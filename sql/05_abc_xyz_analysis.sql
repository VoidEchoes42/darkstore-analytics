-- =============================================================================
-- SQL Module 05: ABC/XYZ Analysis
-- =============================================================================
-- ABC: Revenue contribution (A = top 80%, B = next 15%, C = last 5%)
-- XYZ: Demand volatility (X = stable, Y = seasonal, Z = erratic)
-- Combined matrix for assortment optimization
-- =============================================================================

-- ============================================================
-- Q5.1: Revenue per product (for ABC classification)
-- ============================================================
WITH product_revenue AS (
    SELECT
        oi.product_id,
        p.product_name,
        c.category_name,
        s.store_id,
        s.store_name,
        COUNT(DISTINCT o.order_id)                AS order_count,
        SUM(oi.quantity)                           AS total_units,
        ROUND(SUM(oi.total_price), 2)              AS total_revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories c ON c.category_id = p.category_id
    JOIN orders o ON o.order_id = oi.order_id
    LEFT JOIN stores s ON s.store_id = o.store_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id, p.product_name, c.category_name, s.store_id, s.store_name
),
ranked AS (
    SELECT
        *,
        SUM(total_revenue) OVER (PARTITION BY store_id ORDER BY total_revenue DESC) AS cum_revenue,
        SUM(total_revenue) OVER (PARTITION BY store_id) AS store_total_revenue
    FROM product_revenue
)
SELECT
    store_id,
    store_name,
    product_id,
    product_name,
    category_name,
    order_count,
    total_units,
    total_revenue,
    ROUND(cum_revenue::NUMERIC / NULLIF(store_total_revenue, 0) * 100, 2) AS cum_pct,
    store_total_revenue
FROM ranked
ORDER BY store_id, cum_pct;

-- ============================================================
-- Q5.2: ABC Classification per store
-- A = top 80% cumulative revenue
-- B = next 15%
-- C = last 5%
-- ============================================================
WITH product_revenue AS (
    SELECT
        oi.product_id,
        s.store_id,
        ROUND(SUM(oi.total_price), 2) AS total_revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    LEFT JOIN stores s ON s.store_id = o.store_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id, s.store_id
),
ranked AS (
    SELECT
        *,
        SUM(total_revenue) OVER (PARTITION BY store_id ORDER BY total_revenue DESC) AS cum_revenue,
        SUM(total_revenue) OVER (PARTITION BY store_id) AS store_total_revenue
    FROM product_revenue
),
abc_classified AS (
    SELECT
        store_id,
        product_id,
        total_revenue,
        ROUND(cum_revenue::NUMERIC / NULLIF(store_total_revenue, 0) * 100, 2) AS cum_pct,
        CASE
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(store_total_revenue, 0) * 100, 2) <= 80 THEN 'A'
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(store_total_revenue, 0) * 100, 2) <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
)
SELECT
    store_id,
    abc_class,
    COUNT(*)                           AS product_count,
    SUM(total_revenue)                 AS total_revenue,
    ROUND(SUM(total_revenue)::NUMERIC / SUM(SUM(total_revenue)) OVER () * 100, 2) AS pct_of_total
FROM abc_classified
GROUP BY store_id, abc_class
ORDER BY store_id,
    CASE abc_class WHEN 'A' THEN 1 WHEN 'B' THEN 2 ELSE 3 END;

-- ============================================================
-- Q5.3: XYZ Classification (demand volatility)
-- X = stable demand (CV < 0.5)
-- Y = seasonal (CV 0.5 - 1.0)
-- Z = erratic (CV > 1.0)
-- CV = standard deviation / mean
-- ============================================================
WITH weekly_demand AS (
    SELECT
        oi.product_id,
        DATE_TRUNC('week', o.order_placed_at)::DATE AS week_start,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.quantity) AS units
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id, DATE_TRUNC('week', o.order_placed_at)
),
demand_stats AS (
    SELECT
        product_id,
        ROUND(STDDEV(units), 2)      AS std_dev,
        ROUND(AVG(units), 2)         AS avg_units,
        COUNT(*)                     AS weeks_with_data
    FROM weekly_demand
    GROUP BY product_id
    HAVING COUNT(*) >= 4  -- at least 4 weeks of data
),
xyz_classified AS (
    SELECT
        product_id,
        std_dev,
        avg_units,
        weeks_with_data,
        CASE
            WHEN avg_units = 0 THEN 'Z'
            WHEN ROUND(std_dev::NUMERIC / NULLIF(avg_units, 0), 2) < 0.5 THEN 'X'
            WHEN ROUND(std_dev::NUMERIC / NULLIF(avg_units, 0), 2) <= 1.0 THEN 'Y'
            ELSE 'Z'
        END AS xyz_class
    FROM demand_stats
)
SELECT
    xyz_class,
    COUNT(*) AS product_count,
    ROUND(AVG(std_dev), 2) AS avg_std_dev,
    ROUND(AVG(avg_units), 2) AS avg_weekly_units
FROM xyz_classified
GROUP BY xyz_class
ORDER BY xyz_class;

-- ============================================================
-- Q5.4: Combined ABC/XYZ Matrix
-- ============================================================
WITH product_revenue AS (
    SELECT
        oi.product_id,
        ROUND(SUM(oi.total_price), 2) AS total_revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id
),
ranked AS (
    SELECT
        *,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cum_revenue,
        SUM(total_revenue) OVER () AS total_revenue_all
    FROM product_revenue
),
abc AS (
    SELECT
        product_id,
        total_revenue,
        CASE
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(total_revenue_all, 0) * 100, 2) <= 80 THEN 'A'
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(total_revenue_all, 0) * 100, 2) <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
),
weekly_demand AS (
    SELECT
        oi.product_id,
        DATE_TRUNC('week', o.order_placed_at)::DATE AS week_start,
        SUM(oi.quantity) AS units
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id, DATE_TRUNC('week', o.order_placed_at)
),
demand_stats AS (
    SELECT
        product_id,
        ROUND(STDDEV(units), 2) AS std_dev,
        ROUND(AVG(units), 2) AS avg_units
    FROM weekly_demand
    GROUP BY product_id
    HAVING COUNT(*) >= 4
),
xyz AS (
    SELECT
        product_id,
        CASE
            WHEN avg_units = 0 THEN 'Z'
            WHEN ROUND(std_dev::NUMERIC / NULLIF(avg_units, 0), 2) < 0.5 THEN 'X'
            WHEN ROUND(std_dev::NUMERIC / NULLIF(avg_units, 0), 2) <= 1.0 THEN 'Y'
            ELSE 'Z'
        END AS xyz_class
    FROM demand_stats
)
SELECT
    COALESCE(a.abc_class, 'N/A') AS abc_class,
    COALESCE(x.xyz_class, 'N/A') AS xyz_class,
    COUNT(*)                     AS product_count,
    ROUND(SUM(a.total_revenue), 2) AS total_revenue
FROM abc a
JOIN xyz x ON x.product_id = a.product_id
GROUP BY COALESCE(a.abc_class, 'N/A'), COALESCE(x.xyz_class, 'N/A')
ORDER BY abc_class, xyz_class;

-- ============================================================
-- Q5.5: Per-store assortment recommendations
-- ============================================================
WITH store_abc AS (
    SELECT
        o.store_id,
        oi.product_id,
        p.product_name,
        c.category_name,
        ROUND(SUM(oi.total_price), 2) AS total_revenue,
        SUM(oi.quantity) AS total_units,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories c ON c.category_id = p.category_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.store_id, oi.product_id, p.product_name, c.category_name
),
ranked AS (
    SELECT
        *,
        SUM(total_revenue) OVER (PARTITION BY store_id ORDER BY total_revenue DESC) AS cum_revenue,
        SUM(total_revenue) OVER (PARTITION BY store_id) AS store_total
    FROM store_abc
),
classified AS (
    SELECT
        store_id,
        product_id,
        product_name,
        category_name,
        total_revenue,
        total_units,
        order_count,
        CASE
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(store_total, 0) * 100, 2) <= 80 THEN 'A'
            WHEN ROUND(cum_revenue::NUMERIC / NULLIF(store_total, 0) * 100, 2) <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
)
SELECT
    store_id,
    abc_class,
    category_name,
    COUNT(*) AS product_count,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(SUM(total_units)) AS total_units,
    ARRAY_AGG(product_name ORDER BY total_revenue DESC LIMIT 5) AS top_products
FROM classified
GROUP BY store_id, abc_class, category_name
ORDER BY store_id,
    CASE abc_class WHEN 'A' THEN 1 WHEN 'B' THEN 2 ELSE 3 END,
    total_revenue DESC;
