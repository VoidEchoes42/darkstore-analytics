-- =============================================================================
-- SQL Module 02: Delivery SLA Analysis
-- =============================================================================
-- Questions this module answers:
--   - Breach rate by store, hour, day of week
--   - Average delivery TAT by zone and partner
--   - Partner performance ranking (on-time %, avg TAT, orders delivered)
--   - Root-cause breakdown: picking delay vs. delivery delay vs. system delay
--   - Impact of rain/holiday flags on SLA
--
-- Tables used: orders, order_items, delivery_partners, stores
-- Key technique: Window functions, CTEs, time-based joins
-- =============================================================================

-- Q2.1: SLA Breach Summary by Store and Hour
-- Expected: store_id, date, hour, total_orders, sla_breaches, breach_rate_pct,
--           avg_delivery_minutes, median_delivery_minutes

-- Q2.2: Delivery Partner Performance Leaderboard
-- Expected: partner_id, partner_name, zone, total_deliveries, avg_tat_minutes,
--           breach_count, breach_rate_pct, avg_rating, on_time_rate_pct

-- Q2.3: Root-Cause Breakdown of SLA Breaches
-- Categorize each breach into:
--   - "picking_delay": picked_at - order_placed_at > 3 min
--   - "packing_delay": packed_at - picked_at > 2 min
--   - "dispatch_delay": dispatched_at - packed_at > 3 min
--   - "delivery_delay": delivered_at - dispatched_at > (sla - 8 min)
-- Expected: breach_type, count, pct_of_total_breaches

-- Q2.4: Rain vs Non-Rain SLA Comparison
-- Expected: is_rain_flag, total_orders, avg_delivery_minutes, breach_rate_pct

-- Q2.5: Day-of-Week SLA Pattern
-- Expected: day_of_week, avg_orders, avg_delivery_minutes, breach_rate_pct

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


