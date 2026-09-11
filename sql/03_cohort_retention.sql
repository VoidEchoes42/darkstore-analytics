-- =============================================================================
-- SQL Module 03: Cohort Retention
-- =============================================================================
-- Key Questions:
--   - Weekly cohort retention (N-week retention for each signup week)
--   - Retention by acquisition channel
--   - Frequency decay curve
--   - Cohort LTV estimation
--   - Repeat purchase rate by category
-- =============================================================================

-- ============================================================
-- Q3.1: Weekly cohort retention table
-- Each row = customers who signed up in the same week
-- Each column = % of that cohort active in week N after signup
-- ============================================================
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('week', signup_date)::DATE AS cohort_week,
        signup_date
    FROM customers
),
activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('week', o.order_placed_at)::DATE AS activity_week
    FROM orders o
    WHERE o.order_status = 'delivered'
),
cohort_sizes AS (
    SELECT cohort_week, COUNT(*) AS cohort_size
    FROM cohorts
    GROUP BY cohort_week
),
weeks AS (
    SELECT generate_series(0, 12) AS week_num  -- track for 12 weeks
),
cohort_activity AS (
    SELECT
        c.cohort_week,
        w.week_num,
        COUNT(DISTINCT co.customer_id) AS active_customers
    FROM cohorts c
    CROSS JOIN weeks w
    LEFT JOIN activity co
        ON co.customer_id = c.customer_id
        AND co.activity_week = c.cohort_week + (w.week_num || ' weeks')::INTERVAL
    GROUP BY c.cohort_week, w.week_num
)
SELECT
    ca.cohort_week,
    cs.cohort_size,
    ca.week_num,
    ca.active_customers,
    ROUND(ca.active_customers::NUMERIC / NULLIF(cs.cohort_size, 0) * 100, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.cohort_week = ca.cohort_week
ORDER BY ca.cohort_week, ca.week_num;

-- ============================================================
-- Q3.2: Retention by acquisition channel
-- ============================================================
WITH cohorts AS (
    SELECT
        customer_id,
        acquisition_channel,
        DATE_TRUNC('week', signup_date)::DATE AS cohort_week
    FROM customers
),
activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('week', o.order_placed_at)::DATE AS activity_week
    FROM orders o
    WHERE o.order_status = 'delivered'
),
cohort_sizes AS (
    SELECT cohort_week, acquisition_channel, COUNT(*) AS cohort_size
    FROM cohorts
    GROUP BY cohort_week, acquisition_channel
),
weeks AS (
    SELECT generate_series(0, 12) AS week_num
),
cohort_activity AS (
    SELECT
        c.acquisition_channel,
        w.week_num,
        COUNT(DISTINCT co.customer_id) AS active_customers
    FROM cohorts c
    CROSS JOIN weeks w
    LEFT JOIN activity co
        ON co.customer_id = c.customer_id
        AND co.activity_week = c.cohort_week + (w.week_num || ' weeks')::INTERVAL
    GROUP BY c.acquisition_channel, w.week_num
),
channel_sizes AS (
    SELECT acquisition_channel, SUM(cohort_size) AS total_customers
    FROM cohort_sizes
    GROUP BY acquisition_channel
)
SELECT
    ca.acquisition_channel,
    ca.week_num,
    ROUND(SUM(cs.cohort_size)) AS cohort_size,
    ca.active_customers,
    ROUND(ca.active_customers::NUMERIC / NULLIF(SUM(cs.cohort_size), 0) * 100, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.acquisition_channel = ca.acquisition_channel
GROUP BY ca.acquisition_channel, ca.week_num, ca.active_customers
ORDER BY ca.acquisition_channel, ca.week_num;

-- ============================================================
-- Q3.3: Frequency decay curve
-- Average orders per user over weeks since signup
-- ============================================================
WITH customer_first_signup AS (
    SELECT customer_id, signup_date
    FROM customers
),
weeks AS (
    SELECT generate_series(0, 24) AS week_num
),
weekly_orders AS (
    SELECT
        c.customer_id,
        w.week_num,
        COUNT(DISTINCT o.order_id) AS orders_this_week
    FROM customer_first_signup c
    CROSS JOIN weeks w
    LEFT JOIN orders o
        ON o.customer_id = c.customer_id
        AND o.order_status = 'delivered'
        AND DATE_TRUNC('week', o.order_placed_at)::DATE
            = c.signup_date + (w.week_num || ' weeks')::INTERVAL
    GROUP BY c.customer_id, w.week_num
)
SELECT
    week_num,
    ROUND(AVG(orders_this_week), 2)    AS avg_orders_per_user,
    COUNT(DISTINCT customer_id)        AS active_users,
    SUM(orders_this_week)              AS total_orders
FROM weekly_orders
GROUP BY week_num
ORDER BY week_num;

-- ============================================================
-- Q3.4: Cohort-level LTV (cumulative GMV per customer over time)
-- ============================================================
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('week', signup_date)::DATE AS cohort_week
    FROM customers
),
weekly_gmv AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('week', o.order_placed_at)::DATE AS activity_week,
        SUM(oi.total_price)                          AS week_gmv
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id, DATE_TRUNC('week', o.order_placed_at)
),
weeks AS (
    SELECT generate_series(0, 12) AS week_num
),
cumulative AS (
    SELECT
        c.cohort_week,
        w.week_num,
        COUNT(DISTINCT c.customer_id)                           AS cohort_size,
        ROUND(SUM(COALESCE(wg.week_gmv, 0)), 2)                 AS total_weekly_gmv,
        ROUND(SUM(COALESCE(wg.week_gmv, 0)) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS ltv_per_customer
    FROM cohorts c
    CROSS JOIN weeks w
    LEFT JOIN weekly_gmv wg
        ON wg.customer_id = c.customer_id
        AND wg.activity_week = c.cohort_week + (w.week_num || ' weeks')::INTERVAL
    GROUP BY c.cohort_week, w.week_num
)
SELECT
    cohort_week,
    week_num,
    cohort_size,
    total_weekly_gmv,
    ltv_per_customer
FROM cumulative
ORDER BY cohort_week, week_num;

-- ============================================================
-- Q3.5: Repeat purchase rate by category
-- ============================================================
WITH category_orders AS (
    SELECT
        o.customer_id,
        c.category_name,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories c ON c.category_id = p.category_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id, c.category_name
)
SELECT
    category_name,
    COUNT(*)                                             AS customers,
    COUNT(*) FILTER (WHERE order_count = 1)              AS one_time_buyers,
    COUNT(*) FILTER (WHERE order_count >= 2)             AS repeat_buyers,
    ROUND(COUNT(*) FILTER (WHERE order_count >= 2)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS repeat_rate_pct,
    ROUND(AVG(order_count), 2)                           AS avg_orders_per_customer
FROM category_orders
GROUP BY category_name
ORDER BY repeat_rate_pct DESC;
