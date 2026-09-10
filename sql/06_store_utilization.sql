-- =============================================================================
-- SQL Module 06: Store Utilization & Capacity Planning
-- =============================================================================
-- Questions this module answers:
--   - Orders per store per hour vs. capacity
--   - Peak load identification
--   - Capacity gap analysis (overloaded vs. underutilized stores)
--   - "Where to open next store" recommendation
--
-- Tables used: orders, stores
-- Key technique: CTEs, window functions, aggregation, CASE WHEN
-- =============================================================================

-- Q6.1: Hourly Utilization per Store (last 30 days)
-- Expected: store_id, city, zone, hour_of_day, avg_orders, max_orders,
--           capacity_orders_per_hour, utilization_pct

-- Q6.2: Peak Load Identification
-- Expected: store_id, date, hour, orders, capacity, utilization_pct,
--           is_overloaded (boolean: > 90%)

-- Q6.3: Daily Utilization Summary
-- Expected: store_id, date, total_orders, daily_capacity, utilization_pct,
--           is_overloaded_flag

-- Q6.4: Capacity Gap Analysis (30-day averages)
-- Expected: store_id, city, zone, avg_daily_orders, daily_capacity,
--           utilization_pct, status (overloaded / optimal / underutilized)

-- Q6.5: New Store Location Recommendation
-- Identify zones with high demand but no store, or stores consistently
-- hitting capacity limits.
-- Expected: city, zone, total_demand_orders, existing_store_count,
--           avg_utilization_pct, recommendation

-- Q6.6: Demand Density Heatmap Data
-- Expected: city, zone, hour, avg_orders_per_store, store_count,
--           demand_per_store, gap_flag

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


