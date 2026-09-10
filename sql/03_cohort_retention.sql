-- =============================================================================
-- SQL Module 03: Customer Cohort Retention Analysis
-- =============================================================================
-- Questions this module answers:
--   - Weekly cohort retention (N-week retention for each acquisition week)
--   - Retention by acquisition channel
--   - Frequency decay curve (orders per user over weeks since signup)
--   - Cohort-level LTV estimation
--   - Repeat purchase rate by category
--
-- Tables used: customers, orders
-- Key technique: CTEs, date_trunc, conditional aggregation
-- =============================================================================

-- Q3.1: Weekly Cohort Retention Matrix
-- Rows = signup week, Columns = week number since signup (0, 1, 2, ... 12)
-- Cell value = % of cohort still active (placed at least 1 order in that week)
-- Expected: signup_week, cohort_size, week_0_pct, week_1_pct, ..., week_12_pct

-- Q3.2: Retention by Acquisition Channel
-- Expected: acquisition_channel, cohort_size, week_0_pct, week_4_pct, week_12_pct

-- Q3.3: Frequency Decay Curve
-- Expected: weeks_since_signup, avg_orders_per_user, median_orders_per_user,
--           pct_active_users

-- Q3.4: Cohort LTV (cumulative GMV per customer)
-- Expected: signup_week, cohort_size, avg_cumulative_gmv_week0, week1, ... week12

-- Q3.5: Repeat Purchase Rate by Category
-- Expected: category_name, total_customers, repeat_buyers, repeat_rate_pct,
--           avg_orders_per_repeat_buyer

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


