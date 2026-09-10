# Project Roadmap

Build in this order. Each step builds on the previous one. Check off as you go.

---

## Phase 1: Data Foundation

### Task 1.1 — Database Schema (`data/schema.sql`)
- [ ] Design 8 tables: `stores`, `products`, `categories`, `customers`, `delivery_partners`, `orders`, `order_items`, `store_capacity`
- [ ] Include proper foreign keys, indexes on `store_id`, `order_timestamp`, `customer_id`
- [ ] Add ER diagram (mermaid or draw.io export)
- [ ] Include realistic constraints: delivery SLA defaults, store active hours, product availability windows

### Task 1.2 — Data Generation Scripts (`data/sample_data/`)
- [ ] `generate_stores.py` — 50 stores across 5 cities, with lat/long, capacity, SLA targets
- [ ] `generate_products.py` — 200+ SKUs across 12 categories (FMCG: snacks, beverages, dairy, etc.)
- [ ] `generate_customers.py` — 50K customers with acquisition channel, signup date, location
- [ ] `generate_delivery_partners.py` — 500 delivery partners with shift timings, zones
- [ ] `generate_orders.py` — 1M+ orders with realistic patterns:
  - Spike during 6-9 PM (dinner rush)
  - Lower on weekday afternoons
  ~5% SLA breach rate (higher during peak)
  - Realistic basket sizes (₹300-800)
  - Order statuses: placed → picked → packed → dispatched → delivered (with some cancelled)

---

## Phase 2: SQL Analytics (Core — 6 modules)

### Task 2.1 — Operational KPIs (`sql/01_operational_kpis.sql`)
- [ ] Daily GMV, order count, AOV per store
- [ ] Hourly order volume heatmap (store × hour of day)
- [ ] Fulfillment rate (orders delivered / orders placed) daily
- [ ] Category-wise revenue mix per store
- [ ] Top 20 products by volume and by revenue
- [ ] Customer acquisition rate by channel

### Task 2.2 — SLA Analysis (`sql/02_sla_analysis.sql`)
- [ ] Breach rate by store, hour, day of week
- [ ] Average delivery TAT by zone and partner
- [ ] Partner performance ranking (on-time %, avg TAT, orders delivered)
- [ ] Root-cause breakdown: breach due to picking delay vs. delivery delay vs. system delay
- [ ] Impact of rain/holiday flags on SLA (add weather/holiday dimension if possible)

### Task 2.3 — Cohort Retention (`sql/03_cohort_retention.sql`)
- [ ] Weekly cohort retention table (N-week retention for each acquisition week)
- [ ] Retention by acquisition channel (organic, referral, paid ads)
- [ ] Frequency decay curve (avg orders per user over weeks since signup)
- [ ] Cohort-level LTV estimation
- [ ] Repeat purchase rate by category

### Task 2.4 — Demand Forecasting Support (`sql/04_demand_forecasting.sql`)
- [ ] Hourly demand aggregation by store + SKU (input for Python models)
- [ ] Seasonality: day-of-week patterns, peak-hour identification
- [ ] Stockout detection: days when inventory ran out vs. demand
- [ ] Overstock identification: products with >30 days of inventory
- [ ] Demand correlation: which products are bought together (market basket)

### Task 2.5 — ABC/XYZ Analysis (`sql/05_abc_xyz_analysis.sql`)
- [ ] ABC classification: A (top 80% revenue), B (next 15%), C (last 5%)
- [ ] XYZ classification: X (stable demand), Y (seasonal), Z (erratic)
- [ ] Combined matrix: AX = stock aggressively, CZ = reconsider carrying
- [ ] Per-store assortment recommendations

### Task 2.6 — Store Utilization (`sql/06_store_utilization.sql`)
- [ ] Orders per store per hour vs. capacity
- [ ] Peak load identification (hours where utilization > 90%)
- [ ] Capacity gap analysis: stores consistently overloaded vs. underutilized
- [ ] "Where to open next store" recommendation based on demand density

---

## Phase 3: Python Analytics

### Task 3.1 — Demand Forecasting (`python/demand_forecasting.py`)
- [ ] Prophet model: hourly demand forecast by store × SKU (next 7 days)
- [ ] ARIMA baseline for comparison
- [ ] Evaluation metrics: MAE, RMSE, MAPE
- [ ] Save forecasts to CSV for dashboard consumption

### Task 3.2 — Cohort Analysis (`python/cohort_analysis.py`)
- [ ] Generate cohort retention heatmap (matplotlib/seaborn)
- [ ] LTV curve by cohort
- [ ] Churn probability estimation (simple survival analysis or Kaplan-Meier)
- [ ] Export charts as PNGs for README/report

### Task 3.3 — SLA Anomaly Detection (`python/sla_anomaly_detection.py`)
- [ ] Statistical outlier detection: z-score / IQR method on delivery TAT
- [ ] Flag anomalous breach days (possible rain, staff shortage, system issue)
- [ ] Correlate anomalies with external factors (hour, day, weather flag)

### Task 3.4 — Streamlit Dashboard (`python/dashboard_app.py`)
- [ ] Page 1: Store-level KPI cards + daily trend chart
- [ ] Page 2: SLA breach map (store heatmap + partner leaderboard)
- [ ] Page 3: Cohort retention heatmap + LTV curve
- [ ] Page 4: Demand forecast vs. actual (store + SKU selector)
- [ ] Page 5: Store utilization gauge + capacity recommendation

---

## Phase 4: Excel Models

### Task 4.1 — Financial Model (`excel/financial_model.xlsx`)
- [ ] Store P&L sheet: revenue, COGS, delivery cost, contribution margin per store
- [ ] CAC by acquisition channel
- [ ] LTV:CAC ratio by cohort
- [ ] Break-even analysis: how many orders/day to cover store fixed costs
- [ ] Scenario tab: toggle delivery TAT / AOV / churn to see margin impact

### Task 4.2 — Ops Dashboard Template (`excel/ops_dashboard_template.xlsx`)
- [ ] Pivot table on orders table (store × date → orders, GMV, AOV, breach rate)
- [ ] Slicers for city, category, delivery partner
- [ ] Pre-built charts: daily GMV trend, SLA breach trend, category mix

### Task 4.3 — A/B Test Calculator (`excel/ab_test_calculator.xlsx`)
- [ ] Sample size calculator (given baseline conversion, MDE, power, significance)
- [ ] Significance tester: input control vs. treatment results → get p-value
- [ ] Power analysis: what MDE can you detect with N=10K users?
- [ ] Pre-built example: "Free delivery threshold ₹99 vs ₹49"

---

## Phase 5: Insights & Communication

### Task 5.1 — Recommendation Memo (`insights/recommendation_memo.md`)
Write a 1-page decision document structured as:
- **Situation:** What's the current state? (backed by data)
- **Problem:** What's broken or suboptimal?
- **Analysis:** Key findings from your SQL/Python work
- **Recommendation:** What should Blinkit do? (specific, actionable)
- **Impact:** Quantified business impact (₹ or %)
- **Risks & Mitigations**

Target 3-4 concrete recommendations, e.g.:
1. "Reduce SKU count in Store #17 by 30% — CZ-class items are consuming 15% of shelf space and driving <2% of revenue"
2. "Add a 9-11 PM delivery partner shift in South Delhi — SLA breach rate is 18% during these hours vs. 4% company average"

### Task 5.2 — Ground Ops Observations (`insights/ground_ops_observations.md`)
- [ ] Shadow or interview a local delivery team (Swiggy/Zomato/Blinkit)
- [ ] Document 5-6 first-hand observations: how pickers work, how routes are assigned, pain points
- [ ] Connect observations to your data analysis — this shows interviewers you bridge "data" and "reality"

---

## Phase 6: Polish

### Task 6.1 — README Finalization
- [ ] Write compelling project description (2-3 sentences)
- [ ] Add 3-5 key findings with embedded charts
- [ ] Add tech stack badges
- [ ] Add "Why this project" section (explain Blinkit connection)

### Task 6.2 — GitHub Polish
- [ ] Add `.gitignore` (data/, venv/, __pycache__, .xlsx cache files)
- [ ] Add `LICENSE` (MIT)
- [ ] Ensure clean commit history (one commit per module)
- [ ] Pin the repo, add topics: `sql`, `python`, `analytics`, `blinkit`, `quick-commerce`, `streamlit`

### Task 6.3 — Validation
- [ ] Run all SQL queries — verify no errors, all return sensible results
- [ ] Run Python scripts — verify no import errors, outputs look correct
- [ ] Deploy Streamlit app (Streamlit Cloud is free) — add link to README
- [ ] Ask a friend to clone and run it — fix any setup issues

---

## Estimated Timeline

| Phase | Tasks | Time |
|---|---|---|
| Phase 1: Data Foundation | Schema + data generation | 2-3 days |
| Phase 2: SQL Analytics | 6 query modules | 5-7 days |
| Phase 3: Python | 4 scripts + dashboard | 4-5 days |
| Phase 4: Excel | 3 files | 2-3 days |
| Phase 5: Insights | Memo + observations | 2-3 days |
| Phase 6: Polish | README + GitHub | 1-2 days |
| **Total** | | **~2-3 weeks** |
