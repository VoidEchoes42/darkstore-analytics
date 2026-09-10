# Darkstore Analytics

An end-to-end operations analytics platform for quick-commerce, modeled on Blinkit's dark store delivery model.

Analyzes 1M+ orders across 50 stores to uncover SLA breach patterns, optimize demand forecasting, and quantify the business impact of operational changes.

## Tech Stack

| Tool | Purpose |
|---|---|
| **SQL** | All analytical queries — KPIs, SLA analysis, cohorts, ABC/XYZ, capacity planning |
| **Python** | Demand forecasting, anomaly detection, cohort heatmaps, Streamlit dashboard |
| **Excel** | Financial model (P&L, LTV/CAC), scenario analysis, A/B test calculator |
| **Streamlit** | Interactive operations dashboard |

## Project Structure

```
darkstore-analytics/
├── README.md                    ← You are here
├── PROJECT_ROADMAP.md           ← Detailed build plan & task checklist
│
├── data/
│   ├── schema.sql               ← Complete DB schema (8 tables, ER diagram)
│   └── sample_data/             ← Scripts to generate 1M+ row mock datasets
│       ├── generate_stores.py
│       ├── generate_products.py
│       ├── generate_customers.py
│       ├── generate_delivery_partners.py
│       └── generate_orders.py
│
├── sql/                         ← 6 analytical query modules
│   ├── 01_operational_kpis.sql
│   ├── 02_sla_analysis.sql
│   ├── 03_cohort_retention.sql
│   ├── 04_demand_forecasting.sql
│   ├── 05_abc_xyz_analysis.sql
│   └── 06_store_utilization.sql
│
├── python/
│   ├── demand_forecasting.py    ← Prophet/ARIMA hourly demand by store+SKU
│   ├── cohort_analysis.py       ← Retention heatmap generator
│   ├── sla_anomaly_detection.py ← Statistical outlier detection
│   └── dashboard_app.py         ← Streamlit interactive dashboard
│
├── excel/
│   ├── financial_model.xlsx     ← Store P&L, LTV/CAC, contribution margin
│   ├── ops_dashboard_template.xlsx ← Pivot + slicer live dashboard
│   └── ab_test_calculator.xlsx  ← Sample size, significance, power analysis
│
├── insights/
│   ├── recommendation_memo.md   ← Cross-functional decision doc (Category+Supply+Ops+Product)
│   └── ground_ops_observations.md ← Field notes / learnings
│
├── notebooks/
│   └── exploratory_analysis.ipynb ← EDA with plots and findings
│
└── tests/
    └── test_queries.sql          ← Validation queries for data integrity
```

## Modules at a Glance

| # | Module | Key Questions Answered |
|---|--------|----------------------|
| 1 | **Operational KPIs** | Daily/hourly order volume, GMV, avg order value, fulfillment rate |
| 2 | **SLA Analysis** | Which stores breach TAT? At what hour? Which delivery partners underperform? |
| 3 | **Cohort Retention** | Do customers acquired via referral retain better? How does frequency decay? |
| 4 | **Demand Forecasting** | What will Zone A, Store 3 need at 7 PM tomorrow? |
| 5 | **ABC/XYZ Analysis** | Which SKUs drive revenue? Which are volatile? Optimize assortment. |
| 6 | **Store Utilization** | Are stores over/under capacity? Where to open new dark stores? |

## Build Order

1. `data/schema.sql` — Define the data model
2. `data/sample_data/` — Generate mock data (1M+ orders)
3. `sql/01` through `sql/06` — Build analytical queries one by one
4. `python/` — Forecasting, anomaly detection, dashboard
5. `excel/` — Financial model and scenario analysis
6. `insights/` — Write up findings as if presenting to Blinkit leadership

See `PROJECT_ROADMAP.md` for detailed task breakdowns.
