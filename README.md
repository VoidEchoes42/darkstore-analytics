# Darkstore Analytics

An end-to-end operations analytics platform for quick-commerce, modeled on Blinkit's dark store delivery model.

Analyzes 1.2M+ orders across 50 stores (5 cities) to uncover SLA breach patterns, optimize demand forecasting, and quantify the business impact of operational changes — from SKU assortment to delivery partner shifts.

## Key Findings

| Finding | Impact |
|---------|--------|
| 30% of SKUs generate <2% of revenue — CZ-class items are shelf-space waste | ₹2.9L/month gain across 8 stores |
| Evening SLA breach rate hits 18% during 7-9 PM dinner rush | ₹3L/month from night shift addition |
| Referral customers have 833:1 LTV:CAC — 4x better than paid ads | ₹50L/month in incremental LTV |
| 2 stores critically overloaded (>90%), 4 underutilized (<20%) | Open stores in Noida + South Delhi East |

## Tech Stack

| Tool | Purpose |
|------|---------|
| **SQL** | 42 analytical queries across 6 modules (KPIs, SLA, cohorts, demand, ABC/XYZ, utilization) |
| **Python** | Prophet demand forecasting, cohort heatmaps, Z-score/IQR anomaly detection, Streamlit dashboard |
| **Excel** | Financial P&L model, ops dashboard template, A/B test calculator |
| **Streamlit** | Interactive 5-page operations dashboard |

## Project Structure

```
darkstore-analytics/
├── README.md                        ← You are here
├── PROJECT_ROADMAP.md               ← Detailed build plan & task checklist
├── LICENSE                          ← MIT License
│
├── data/
│   ├── schema.sql                   ← 8-table DB schema with ER diagram
│   └── sample_data/                 ← 5 Python scripts to generate 1.2M+ rows
│       ├── generate_stores.py       ← 50 stores across 5 cities
│       ├── generate_products.py     ← 210 products across 12 FMCG categories
│       ├── generate_customers.py    ← 50,000 customers with signup dates & channels
│       ├── generate_delivery_partners.py ← 500 partners with shifts & ratings
│       └── generate_orders.py       ← 1.2M orders with dinner-rush spikes, rain/holiday flags
│
├── sql/                             ← 6 analytical query modules (42 queries total)
│   ├── 01_operational_kpis.sql      ← Daily GMV, AOV, fulfillment, category mix, top products
│   ├── 02_sla_analysis.sql          ← Breach rates by store/hour, partner ranking, root causes
│   ├── 03_cohort_retention.sql      ← Weekly retention, LTV by channel, frequency decay
│   ├── 04_demand_forecasting.sql    ← Hourly demand aggregation, stockout/overstock, market basket
│   ├── 05_abc_xyz_analysis.sql      ← SKU classification (revenue ABC, demand volatility XYZ)
│   └── 06_store_utilization.sql     ← Capacity vs actual orders, peak load, new store recommendations
│
├── python/
│   ├── demand_forecasting.py        ← Prophet hourly demand forecast by store×SKU (7 days ahead)
│   ├── cohort_analysis.py            ← Retention heatmap + LTV curve generator (matplotlib/seaborn)
│   ├── sla_anomaly_detection.py     ← Z-score + IQR anomaly detection on daily breach rates
│   └── dashboard_app.py              ← Streamlit 5-page dashboard (KPIs, SLA, Retention, Forecast, Utilization)
│
├── excel/
│   ├── build_financial_model.py     ← Generates P&L, LTV:CAC, break-even, scenario toggle
│   ├── build_ops_dashboard.py        ← Generates pivot tables + charts for ad-hoc analysis
│   └── build_ab_test_calculator.py  ← Sample size, significance tester, power analysis
│
├── insights/
│   ├── recommendation_memo.md       ← 4 data-backed recommendations with ₹ impact estimates
│   └── ground_ops_observations.md   ← 6 first-hand field observations linked to SQL findings
│
└── tests/
    └── test_queries.sql              ← Data integrity validation queries
```

## Modules at a Glance

| # | Module | Key Questions Answered | Queries |
|---|--------|----------------------|---------|
| 1 | **Operational KPIs** | Daily/hourly GMV, AOV, fulfillment rate, top products | 8 |
| 2 | **SLA Analysis** | Which stores breach TAT? Root causes? Partner performance? | 7 |
| 3 | **Cohort Retention** | Does referral retain better? Frequency decay? Cohort LTV? | 6 |
| 4 | **Demand Forecasting** | Hourly demand by store+SKU, stockouts, market basket | 6 |
| 5 | **ABC/XYZ Analysis** | Which SKUs drive revenue? Which are volatile? Assortment optimization | 5 |
| 6 | **Store Utilization** | Overloaded vs underutilized? Where to open next store? | 5 |

## Build Order

1. `data/schema.sql` + `data/sample_data/` — Define model and generate 1.2M rows of mock data
2. `sql/01` through `sql/06` — Run analytical queries against PostgreSQL/MySQL
3. `python/` — Forecasting, anomaly detection, cohort analysis, Streamlit dashboard
4. `excel/` — Financial model, ops dashboard, A/B calculator
5. `insights/` — Recommendation memo and ground ops observations

## Estimated Timeline

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1: Data Foundation | Schema + data generation | 2-3 days |
| Phase 2: SQL Analytics | 6 query modules | 5-7 days |
| Phase 3: Python | 4 scripts + dashboard | 4-5 days |
| Phase 4: Excel | 3 files | 2-3 days |
| Phase 5: Insights | Memo + observations | 2-3 days |
| Phase 6: Polish | README + deployment | 1-2 days |
| **Total** | | **~2-3 weeks** |

## Why This Project

Quick-commerce (10-min grocery delivery) is one of the fastest-growing segments in India. Dark store operations are the backbone — poorly optimized stores lead to SLA breaches, customer churn, and margin erosion. This project demonstrates end-to-end data analytics skills (SQL, Python, Excel, visualization) applied to a real-world business problem similar to Blinkit, Swiggy Instamart, and Zepto.

## License

MIT — see [LICENSE](LICENSE) for details.

