-- =============================================================================
-- SQL Module 05: ABC/XYZ Inventory Analysis
-- =============================================================================
-- Questions this module answers:
--   - ABC classification: A (top 80% revenue), B (next 15%), C (last 5%)
--   - XYZ classification: X (stable demand), Y (seasonal), Z (erratic)
--   - Combined matrix: AX = stock aggressively, CZ = reconsider carrying
--   - Per-store assortment recommendations
--
-- Tables used: products, categories, order_items, orders, product_store_inventory
-- Key technique: PERCENT_RANK / NTILE, standard deviation for XYZ,
--                CASE WHEN for classification
-- =============================================================================

-- Q5.1: ABC Classification (company-wide, last 30 days)
-- Expected: product_id, product_name, category_name, total_revenue,
--           revenue_pct, cumulative_revenue_pct, abc_class

-- Q5.2: XYZ Classification (demand stability)
-- Compute coefficient of variation (stddev / mean) of daily demand per SKU
-- X = CV < 0.5 (stable), Y = CV 0.5-1.5 (seasonal), Z = CV > 1.5 (erratic)
-- Expected: product_id, avg_daily_demand, stddev_daily_demand, cv, xyz_class

-- Q5.3: Combined ABC/XYZ Matrix
-- Expected: abc_class, xyz_class, product_count, total_revenue,
--           avg_daily_demand, recommendation

-- Q5.4: Per-Store Assortment Recommendations
-- Expected: store_id, abc_class, xyz_class, count_products,
--           revenue_pct, recommendation

-- Q5.5: Slow-Moving Inventory (C/Z class products to reconsider)
-- Expected: store_id, product_id, product_name, stock_quantity,
--           last_30d_units_sold, days_since_last_sale, recommendation

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


