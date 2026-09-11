"""
SLA Anomaly Detection — Z-score + IQR on daily breach rates.
Input:  orders.csv (SQL Module 02 output)
Output: sla_anomalies.csv + sla_anomaly_plot.png
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")


def load_orders(data_dir: str) -> pd.DataFrame:
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    orders["order_placed_at"] = pd.to_datetime(orders["order_placed_at"])
    return orders


def compute_daily_sla(orders: pd.DataFrame) -> pd.DataFrame:
    """Compute daily SLA metrics per store."""
    delivered = orders[orders["order_status"] == "delivered"].copy()

    daily = (
        delivered.groupby([delivered["store_id"], delivered["order_placed_at"].dt.date])
        .agg(
            total_orders=("order_id", "count"),
            late_orders=("actual_delivery_minutes", lambda x: (x > delivered.loc[x.index, "sla_target_minutes"]).sum()),
            avg_delivery_min=("actual_delivery_minutes", "mean"),
            rain_days=("is_rain_flag", "sum"),
            holiday_days=("is_holiday_flag", "sum"),
        )
        .reset_index()
    )
    daily.columns = ["store_id", "order_date", "total_orders", "late_orders", "avg_delivery_min", "rain_days", "holiday_days"]
    daily["breach_rate_pct"] = (daily["late_orders"] / daily["total_orders"].clip(lower=1) * 100).round(2)
    daily["order_date"] = pd.to_datetime(daily["order_date"])
    return daily


def detect_anomalies(daily: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    """Flag anomalous days using Z-score and IQR per store."""
    results = []
    for store_id, group in daily.groupby("store_id"):
        group = group.sort_values("order_date").reset_index(drop=True)
        if len(group) < 5:
            continue

        # Z-score
        mean_br = group["breach_rate_pct"].mean()
        std_br = group["breach_rate_pct"].std()
        std_br = 1 if pd.isna(std_br) or std_br == 0 else std_br
        group["z_score"] = ((group["breach_rate_pct"] - mean_br) / std_br).round(2)

        # IQR
        q1 = group["breach_rate_pct"].quantile(0.25)
        q3 = group["breach_rate_pct"].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        group["iqr_anomaly"] = group["breach_rate_pct"] > upper_bound

        # Combined flag
        group["is_anomaly"] = (abs(group["z_score"]) > z_threshold) | group["iqr_anomaly"]
        results.append(group)

    return pd.concat(results, ignore_index=True)


def plot_anomalies(anomalies: pd.DataFrame, output_path: str, sample_stores: int = 5):
    """Plot breach rate with anomaly markers for a few sample stores."""
    top_stores = anomalies.groupby("store_id")["total_orders"].sum().nlargest(sample_stores).index
    fig, axes = plt.subplots(sample_stores, 1, figsize=(14, 3 * sample_stores), sharex=False)

    for idx, store_id in enumerate(top_stores):
        ax = axes[idx] if sample_stores > 1 else axes
        data = anomalies[anomalies["store_id"] == store_id].sort_values("order_date")
        normal = data[~data["is_anomaly"]]
        anomaly_days = data[data["is_anomaly"]]

        ax.plot(normal["order_date"], normal["breach_rate_pct"], "b-o", markersize=3, label="Normal", alpha=0.7)
        ax.scatter(anomaly_days["order_date"], anomaly_days["breach_rate_pct"], color="red", s=50, zorder=5, label="Anomaly")
        ax.axhline(y=data["breach_rate_pct"].mean(), color="gray", linestyle="--", alpha=0.5, label="Mean")
        ax.set_title(f"Store {store_id} — Daily SLA Breach Rate", fontsize=12)
        ax.set_ylabel("Breach Rate %")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"     Saved anomaly plot → {output_path}")


def run(data_dir: str, output_dir: str):
    print("[1/4] Loading orders...")
    orders = load_orders(data_dir)
    print(f"     {len(orders):,} orders loaded")

    print("[2/4] Computing daily SLA metrics...")
    daily = compute_daily_sla(orders)
    print(f"     {len(daily):,} store-day records computed")

    print("[3/4] Detecting anomalies (Z-score + IQR)...")
    anomalies = detect_anomalies(daily)
    n_anomalies = anomalies["is_anomaly"].sum()
    print(f"     {n_anomalies} anomalous store-days flagged")

    out_csv = os.path.join(output_dir, "sla_anomalies.csv")
    output_cols = ["store_id", "order_date", "total_orders", "breach_rate_pct", "z_score", "is_anomaly", "rain_days", "holiday_days", "avg_delivery_min"]
    anomalies[output_cols].to_csv(out_csv, index=False)
    print(f"     Saved → {out_csv}")

    print("[4/4] Generating anomaly plot...")
    plot_anomalies(anomalies, os.path.join(output_dir, "sla_anomaly_plot.png"))

    # Summary
    anomaly_days = anomalies[anomalies["is_anomaly"]]
    print(f"\n     Anomaly summary:")
    print(f"     - Total anomalous store-days: {n_anomalies}")
    print(f"     - Days with rain flag: {anomaly_days['rain_days'].gt(0).sum()}")
    print(f"     - Days with holiday flag: {anomaly_days['holiday_days'].gt(0).sum()}")
    print(f"     - Avg breach rate on anomaly days: {anomaly_days['breach_rate_pct'].mean():.1f}%")
    print(f"     - Avg breach rate on normal days: {anomalies[~anomalies['is_anomaly']]['breach_rate_pct'].mean():.1f}%")
    print("Done!")


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    data_dir = str(base / "data" / "sample_data")
    output_dir = str(base / "outputs")
    os.makedirs(output_dir, exist_ok=True)
    run(data_dir, output_dir)
