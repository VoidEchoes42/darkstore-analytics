-- =============================================================================
-- SQL Module 01: Operational KPIs
-- =============================================================================
-- Questions this module answers:
--   - Daily/hourly GMV, order count, AOV per store
--   - Hourly order volume heatmap (store × hour of day)
--   - Fulfillment rate (orders delivered / orders placed) daily
--   - Category-wise revenue mix per store
--   - Top 20 products by volume and by revenue
--   - Customer acquisition rate by channel
--
-- Tables used: orders, order_items, products, categories, customers, stores
-- =============================================================================

-- Q1.1: Daily Store-level KPIs
-- Expected columns: date, store_id, store_name, city, total_orders, gmv,
--                   aov, delivered_orders, fulfilment_rate_pct

-- Q1.2: Hourly Order Volume (for heatmap)
-- Expected columns: date, hour, store_id, city, order_count, gmv

-- Q1.3: Category Revenue Mix per Store (weekly)
-- Expected columns: week_start, store_id, category_name, revenue, pct_of_store_revenue

-- Q1.4: Top 20 Products by Revenue (last 30 days)
-- Expected columns: rank, product_id, product_name, category_name, total_qty_sold,
--                   total_revenue, avg_selling_price

-- Q1.5: Customer Acquisition by Channel (weekly cohort)
-- Expected columns: signup_week, acquisition_channel, new_customers, cumulative_customers

-- Q1.6: Fulfillment Rate Trend (daily, company-wide and by store)
-- Expected columns: date, store_id, total_orders, delivered, cancelled, fulfilment_rate_pct

-- =============================================================================
-- Write your queries below this line
-- =============================================================================


