-- =============================================================================
-- SQL Module 04: Demand Forecasting Support
-- =============================================================================
-- Questions this module answers:
--   - Hourly demand aggregation by store + SKU (input for Python models)
--   - Seasonality: day-of-week patterns, peak-hour identification
--   - Stockout detection: days when inventory ran out vs. demand
--   - Overstock identification: products with >30 days of inventory
--   - Market basket: which products are bought together
--
-- Tables used: orders, order_items, products, categories, stores,
--              product_store_inventory
-- =============================================================================

-- Q4.1: Hourly Demand by Store + SKU (aggregation for forecasting)
-- Expected: date, hour, store_id, city, product_id, product_name, category_name,
--           units_sold, revenue

-- Q4.2: Peak Hour Identification per Store
-- Expected: store_id, city, peak_hour, peak_hour_orders, avg_daily_orders

-- Q4.3: Day-of-Week Demand Pattern
-- Expected: store_id, day_of_week, avg_orders, avg_gmv, pct_of_weekly_volume

-- Q4.4: Stockout Detection
-- Expected: store_id, product_id, date, stock_quantity, units_demanded,
--           stockout_flag, lost_revenue_estimate

-- Q4.5: Overstock Detection
-- Expected: store_id, product_id, stock_quantity, avg_daily_sales,
--           days_of_inventory_remaining, overstock_flag

-- Q4.6: Market Basket Analysis (product pairs frequently bought together)
-- Expected: product_a_id, product_b_id, times_bought_together, co_occurrence_rate

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


