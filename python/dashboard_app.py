"""
Streamlit Dashboard — Interactive darkstore operations dashboard.
Pages:
  1. Operational KPIs
  2. SLA Analysis
  3. Customer Retention
  4. Demand Forecast
  5. Store Utilization

Run: streamlit run python/dashboard_app.py
"""
import sys
import os
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "sample_data"
OUTPUT_DIR = BASE_DIR / "outputs"


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


st.set_page_config(page_title="Darkstore Analytics", page_icon="🛒", layout="wide")

# Sidebar navigation
st.sidebar.title("Darkstore Analytics")
st.sidebar.markdown("**Quick-commerce operations dashboard**")
page = st.sidebar.radio(
    "Navigate",
    ["📊 KPIs", "⏱ SLA Analysis", "👥 Retention", "📈 Demand Forecast", "🏪 Store Utilization"],
)

# ============================================================
# PAGE 1: Operational KPIs
# ============================================================
if page == "📊 KPIs":
    st.header("📊 Operational KPIs")
    orders = load_csv("orders.csv")
    order_items = load_csv("order_items.csv")

    if orders.empty:
        st.warning("Data not found. Run the data generation scripts first.")
        st.stop()

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["order_placed_at"] = pd.to_datetime(delivered["order_placed_at"])
    delivered["date"] = delivered["order_placed_at"].dt.date

    # KPI Cards
    today = delivered["order_placed_at"].max().date()
    today_data = delivered[delivered["date"] == today]
    total_gmv = today_data.merge(order_items, on="order_id")["total_price"].sum() if not order_items.empty else 0
    total_orders = len(today_data)
    avg_delivery = today_data["actual_delivery_minutes"].mean()
    fulfillment = (len(today_data) / len(delivered[delivered["date"] == today]) * 100) if not delivered[delivered["date"] == today].empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's GMV", f"₹{total_gmv:,.0f}")
    col2.metric("Today's Orders", f"{total_orders:,}")
    col3.metric("Avg Delivery (min)", f"{avg_delivery:.1f}" if pd.notna(avg_delivery) else "N/A")
    col4.metric("Fulfillment Rate", f"{fulfillment:.1f}%")

    # Daily GMV Trend
    st.subheader("Daily GMV Trend (Last 30 Days)")
    daily = delivered.groupby("date").size().reset_index(name="orders")
    if not order_items.empty:
        daily_gmv = delivered.merge(order_items, on="order_id").groupby("date")["total_price"].sum().reset_index(name="gmv")
        daily = daily.merge(daily_gmv, on="date", how="left")

    daily = daily.tail(30)
    fig = px.line(daily, x="date", y="gmv" if "gmv" in daily.columns else "orders",
                  title="Daily GMV Trend", markers=True)
    fig.update_layout(xaxis_title="Date", yaxis_title="GMV (₹)")
    st.plotly_chart(fig, use_container_width=True)

    # Hourly heatmap
    st.subheader("Hourly Order Volume Heatmap")
    delivered["hour"] = delivered["order_placed_at"].dt.hour
    heatmap_data = delivered.groupby(["store_id", "hour"]).size().reset_index(name="orders")
    pivot = heatmap_data.pivot(index="store_id", columns="hour", values="orders").fillna(0)
    fig = px.imshow(pivot.values, labels=dict(x="Hour of Day", y="Store ID", color="Orders"),
                    x=[str(h) for h in pivot.columns], y=[str(i) for i in pivot.index],
                    color_continuous_scale="YlOrRd", aspect="auto")
    fig.update_layout(title="Orders per Store × Hour", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 2: SLA Analysis
# ============================================================
elif page == "⏱ SLA Analysis":
    st.header("⏱ SLA Analysis")
    orders = load_csv("orders.csv")
    if orders.empty:
        st.warning("Data not found.")
        st.stop()

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["breached"] = delivered["actual_delivery_minutes"] > delivered["sla_target_minutes"]

    # Breach rate by store
    st.subheader("SLA Breach Rate by Store")
    store_sla = delivered.groupby("store_id").agg(
        total=("order_id", "count"),
        breached=("breached", "sum"),
        avg_tat=("actual_delivery_minutes", "mean"),
    ).reset_index()
    store_sla["breach_rate_pct"] = (store_sla["breached"] / store_sla["total"] * 100).round(2)
    store_sla = store_sla.sort_values("breach_rate_pct", ascending=False)

    fig = px.bar(store_sla, x="store_id", y="breach_rate_pct", color="breach_rate_pct",
                 color_continuous_scale="Reds", title="Breach Rate by Store (%)")
    fig.update_layout(xaxis_title="Store ID", yaxis_title="Breach Rate %")
    st.plotly_chart(fig, use_container_width=True)

    # Partner leaderboard
    st.subheader("Delivery Partner Leaderboard")
    partner_perf = delivered.groupby("partner_id").agg(
        deliveries=("order_id", "count"),
        on_time=("breached", lambda x: (~x).sum()),
        avg_tat=("actual_delivery_minutes", "mean"),
    ).reset_index()
    partner_perf["on_time_pct"] = (partner_perf["on_time"] / partner_perf["deliveries"] * 100).round(1)
    partner_perf = partner_perf[partner_perf["deliveries"] >= 10].sort_values("on_time_pct", ascending=False).head(20)
    st.dataframe(partner_perf, use_container_width=True)

    # Root cause breakdown
    st.subheader("Breach Root Cause Breakdown")
    orders["pick_delay"] = (pd.to_datetime(orders["picked_at"], errors="coerce") - pd.to_datetime(orders["order_placed_at"], errors="coerce")).dt.total_seconds() / 60
    orders["delivery_delay"] = orders["actual_delivery_minutes"]

    cause_counts = {
        "Rain": orders["is_rain_flag"].sum(),
        "Holiday": orders["is_holiday_flag"].sum(),
        "Late Delivery": delivered["breached"].sum(),
    }
    fig = px.pie(names=list(cause_counts.keys()), values=list(cause_counts.values()), title="Breach Factors")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 3: Retention
# ============================================================
elif page == "👥 Retention":
    st.header("👥 Customer Retention")
    cohort_img = OUTPUT_DIR / "cohort_retention.png"
    ltv_img = OUTPUT_DIR / "cohort_ltv.png"

    if cohort_img.exists():
        st.image(str(cohort_img), caption="Cohort Retention Heatmap", use_column_width=True)
    else:
        st.info("Run `python python/cohort_analysis.py` to generate the retention heatmap.")

    if ltv_img.exists():
        st.image(str(ltv_img), caption="Cumulative LTV by Cohort", use_column_width=True)
    else:
        st.info("Run `python python/cohort_analysis.py` to generate LTV curves.")

    # Channel comparison
    st.subheader("Customer Acquisition by Channel")
    customers = load_csv("customers.csv")
    if not customers.empty:
        channel_data = customers["acquisition_channel"].value_counts().reset_index()
        channel_data.columns = ["channel", "count"]
        fig = px.bar(channel_data, x="channel", y="count", color="channel", title="Customers by Channel")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 4: Demand Forecast
# ============================================================
elif page == "📈 Demand Forecast":
    st.header("📈 Demand Forecast")
    st.info("Run `python python/demand_forecasting.py` to generate forecasts.")

    forecasts_path = OUTPUT_DIR / "forecasts.csv"
    if forecasts_path.exists():
        fc = pd.read_csv(forecasts_path)
        fc["datetime"] = pd.to_datetime(fc["datetime"])

        store_opts = fc["store_id"].unique()
        product_opts = fc["product_id"].unique()
        sel_store = st.selectbox("Select Store", sorted(store_opts))
        sel_product = st.selectbox("Select Product", sorted(product_opts))

        subset = fc[(fc["store_id"] == sel_store) & (fc["product_id"] == sel_product)]
        if not subset.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=subset["datetime"], y=subset["forecast_units"],
                                     mode="lines", name="Forecast", line=dict(color="blue")))
            fig.add_trace(go.Scatter(
                x=pd.concat([subset["datetime"], subset["datetime"][::-1]]),
                y=pd.concat([subset["upper_bound"], subset["lower_bound"][::-1]]),
                fill="toself", fillcolor="rgba(0,100,255,0.2)", line=dict(color="rgba(255,255,255,0)"),
                name="Confidence Interval"
            ))
            fig.update_layout(title=f"Forecast: Store {sel_store}, Product {sel_product}",
                              xaxis_title="Date", yaxis_title="Forecasted Units")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Forecasts not generated yet. Run the demand forecasting script first.")

# ============================================================
# PAGE 5: Store Utilization
# ============================================================
elif page == "🏪 Store Utilization":
    st.header("🏪 Store Utilization")
    stores = load_csv("stores.csv")
    orders = load_csv("orders.csv")

    if stores.empty or orders.empty:
        st.warning("Data not found.")
        st.stop()

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["order_placed_at"] = pd.to_datetime(delivered["order_placed_at"])
    delivered["date"] = delivered["order_placed_at"].dt.date

    # Average daily orders per store vs capacity
    daily = delivered.groupby(["store_id", "date"]).size().reset_index(name="orders")
    avg_daily = daily.groupby("store_id")["orders"].mean().reset_index(name="avg_daily_orders")
    store_cap = stores[["store_id", "capacity_orders_per_day"]].copy()
    util = avg_daily.merge(store_cap, on="store_id")
    util["utilization_pct"] = (util["avg_daily_orders"] / util["capacity_orders_per_day"] * 100).round(1)
    util["status"] = util["utilization_pct"].apply(
        lambda x: "Overloaded" if x > 90 else ("Underutilized" if x < 50 else "Optimal")
    )

    st.subheader("Store Capacity Utilization")
    color_map = {"Overloaded": "red", "Optimal": "green", "Underutilized": "orange"}
    fig = px.bar(util, x="store_id", y="utilization_pct", color="status", color_discrete_map=color_map,
                 title="Avg Daily Utilization % by Store", hover_data=["avg_daily_orders", "capacity_orders_per_day"])
    fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Overload threshold")
    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Underutilized threshold")
    st.plotly_chart(fig, use_container_width=True)

    # Capacity gap table
    st.subheader("Capacity Gap Table")
    gap_table = util[["store_id", "avg_daily_orders", "capacity_orders_per_day", "utilization_pct", "status"]].sort_values("utilization_pct", ascending=False)
    st.dataframe(gap_table, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Darkstore Analytics v1.0**")
st.sidebar.markdown("Built with Streamlit + Plotly")
