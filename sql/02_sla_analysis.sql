-- =============================================================================
-- SQL Module 02: SLA Analysis
-- =============================================================================
-- Key Questions:
--   - Which stores breach TAT? At what hour? Which partners underperform?
--   - Root-cause breakdown: picking vs delivery vs system delay
--   - Impact of rain/holiday flags
-- =============================================================================

-- ============================================================
-- Q2.1: Breach rate by store (delivered but late vs target)
-- ============================================================
SELECT
    store_id,
    COUNT(*)                                          AS total_delivered,
    COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes) AS late_orders,
    ROUND(
        COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                 AS breach_rate_pct,
    ROUND(AVG(actual_delivery_minutes), 1)            AS avg_delivery_min,
    MIN(actual_delivery_minutes)                      AS min_delivery_min,
    MAX(actual_delivery_minutes)                      AS max_delivery_min
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_minutes IS NOT NULL
GROUP BY store_id
ORDER BY breach_rate_pct DESC;

-- ============================================================
-- Q2.2: Breach rate by hour of day (all stores combined)
-- ============================================================
SELECT
    EXTRACT(HOUR FROM order_placed_at) AS hour_of_day,
    COUNT(*)                           AS total_delivered,
    COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes) AS late_orders,
    ROUND(
        COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                  AS breach_rate_pct,
    ROUND(AVG(actual_delivery_minutes), 1) AS avg_delivery_min
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_minutes IS NOT NULL
GROUP BY EXTRACT(HOUR FROM order_placed_at)
ORDER BY hour_of_day;

-- ============================================================
-- Q2.3: Breach rate by day of week
-- ============================================================
SELECT
    TO_CHAR(order_placed_at, 'Day') AS day_of_week,
    EXTRACT(DOW FROM order_placed_at) AS dow_num,
    COUNT(*)                        AS total_delivered,
    COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes) AS late_orders,
    ROUND(
        COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                               AS breach_rate_pct,
    ROUND(AVG(actual_delivery_minutes), 1) AS avg_delivery_min
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_minutes IS NOT NULL
GROUP BY TO_CHAR(order_placed_at, 'Day'), EXTRACT(DOW FROM order_placed_at)
ORDER BY dow_num;

-- ============================================================
-- Q2.4: Partner performance ranking
-- ============================================================
SELECT
    dp.partner_id,
    dp.name,
    dp.zone,
    dp.vehicle_type,
    COUNT(o.order_id)                                        AS total_deliveries,
    ROUND(AVG(o.actual_delivery_minutes), 1)                AS avg_tat_min,
    COUNT(*) FILTER (WHERE o.actual_delivery_minutes <= o.sla_target_minutes) AS on_time_deliveries,
    ROUND(
        COUNT(*) FILTER (WHERE o.actual_delivery_minutes <= o.sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(o.order_id), 0) * 100, 2
    )                                                         AS on_time_pct,
    COUNT(*) FILTER (WHERE o.actual_delivery_minutes > o.sla_target_minutes) AS late_deliveries,
    ROUND(dp.avg_rating, 1)                                  AS rating
FROM delivery_partners dp
JOIN orders o ON o.partner_id = dp.partner_id
WHERE o.order_status = 'delivered'
  AND o.actual_delivery_minutes IS NOT NULL
GROUP BY dp.partner_id, dp.name, dp.zone, dp.vehicle_type, dp.avg_rating
HAVING COUNT(o.order_id) >= 10  -- filter out partners with too few orders
ORDER BY on_time_pct DESC
LIMIT 50;

-- ============================================================
-- Q2.5: Root-cause breakdown of SLA breaches
-- ============================================================
-- Breach causes:
--   1. Picking delay = picked_at - placed_at (target: < 5 min)
--   2. Packing delay  = packed_at - picked_at (target: < 3 min)
--   3. Dispatch delay = dispatched_at - packed_at (target: < 5 min)
--   4. Delivery delay = actual_delivery_minutes - (picked→dispatched time)
-- ============================================================
SELECT
    o.store_id,
    s.city,
    s.zone,
    COUNT(*)                                                         AS total_late_orders,
    -- Picking delay category
    COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (o.picked_at - o.order_placed_at))/60 > 5) AS picking_delay_count,
    COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (o.packed_at - o.picked_at))/60 > 3)      AS packing_delay_count,
    COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (o.dispatched_at - o.packed_at))/60 > 5)   AS dispatch_delay_count,
    ROUND(AVG(o.actual_delivery_minutes), 1)                          AS avg_delivery_min
FROM orders o
JOIN stores s ON s.store_id = o.store_id
WHERE o.order_status = 'delivered'
  AND o.actual_delivery_minutes > o.sla_target_minutes
GROUP BY o.store_id, s.city, s.zone
ORDER BY total_late_orders DESC;

-- ============================================================
-- Q2.6: Impact of rain on SLA
-- ============================================================
SELECT
    is_rain_flag,
    COUNT(*)                                                         AS total_orders,
    COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes) AS late_orders,
    ROUND(
        COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                                AS breach_rate_pct,
    ROUND(AVG(actual_delivery_minutes), 1)                           AS avg_delivery_min
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_minutes IS NOT NULL
GROUP BY is_rain_flag
ORDER BY is_rain_flag;

-- ============================================================
-- Q2.7: Impact of holidays on SLA
-- ============================================================
SELECT
    is_holiday_flag,
    COUNT(*)                                                         AS total_orders,
    COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes) AS late_orders,
    ROUND(
        COUNT(*) FILTER (WHERE actual_delivery_minutes > sla_target_minutes)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                                AS breach_rate_pct,
    ROUND(AVG(actual_delivery_minutes), 1)                           AS avg_delivery_min
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_minutes IS NOT NULL
GROUP BY is_holiday_flag
ORDER BY is_holiday_flag;
