"""
Cohort Analysis — Retention heatmap + LTV curves.
Input:  customers.csv + orders.csv
Output: cohort_retention.png + cohort_ltv.png
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


def load_data(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    order_items = pd.read_csv(os.path.join(data_dir, "order_items.csv"))
    # Compute order-level GMV from order_items
    order_gmv = order_items.groupby("order_id")["total_price"].sum().reset_index()
    orders = orders.merge(order_gmv, on="order_id", how="left")
    orders["order_placed_at"] = pd.to_datetime(orders["order_placed_at"])
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    return customers, orders


def cohort_retention_matrix(customers: pd.DataFrame, orders: pd.DataFrame, max_weeks: int = 12):
    """Build cohort retention matrix: rows=cohort, cols=weeks since signup."""
    customers["cohort_week"] = customers["signup_date"] - pd.to_timedelta(
        customers["signup_date"].dt.dayofweek, unit="D"
    )
    customers["cohort_week"] = pd.to_datetime(customers["cohort_week"]).dt.to_period("W").dt.start_time

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["activity_week"] = delivered["order_placed_at"] - pd.to_timedelta(
        delivered["order_placed_at"].dt.dayofweek, unit="D"
    )
    delivered["activity_week"] = pd.to_datetime(delivered["activity_week"]).dt.to_period("W").dt.start_time

    cohort_sizes = customers.groupby("cohort_week")["customer_id"].nunique().rename("cohort_size")

    weeks = pd.RangeIndex(0, max_weeks + 1)
    cohorts = customers["cohort_week"].unique()

    matrix = pd.DataFrame(index=cohort_sizes.index, columns=weeks, dtype=float)
    matrix.index.name = "cohort_week"

    for cohort_week in cohorts:
        cohort_customers = customers[customers["cohort_week"] == cohort_week]["customer_id"]
        for w in weeks:
            activity = delivered[
                (delivered["customer_id"].isin(cohort_customers))
                & (delivered["activity_week"] == cohort_week + pd.Timedelta(weeks=w))
            ]
            active = activity["customer_id"].nunique()
            matrix.loc[cohort_week, w] = active / len(cohort_customers) * 100

    return matrix, cohort_sizes


def plot_retention_heatmap(matrix: pd.DataFrame, output_path: str):
    """Plot cohort retention heatmap."""
    plt.figure(figsize=(14, 10))
    sns.heatmap(
        matrix.iloc[::-1],  # newest cohort on top
        annot=True,
        fmt=".1f",
        cmap="YlGnBu",
        vmin=0, vmax=100,
        linewidths=0.5,
        cbar_kws={"label": "Retention %"},
    )
    plt.title("Cohort Retention Heatmap (% Active per Week)", fontsize=16, pad=20)
    plt.xlabel("Weeks Since Signup", fontsize=12)
    plt.ylabel("Cohort Week", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"     Saved retention heatmap → {output_path}")


def cohort_ltv_curve(customers: pd.DataFrame, orders: pd.DataFrame, max_weeks: int = 12):
    """Compute cumulative LTV per cohort over weeks."""
    customers["cohort_week"] = customers["signup_date"] - pd.to_timedelta(
        customers["signup_date"].dt.dayofweek, unit="D"
    )
    customers["cohort_week"] = pd.to_datetime(customers["cohort_week"]).dt.to_period("W").dt.start_time

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["activity_week"] = delivered["order_placed_at"] - pd.to_timedelta(
        delivered["order_placed_at"].dt.dayofweek, unit="D"
    )
    delivered["activity_week"] = pd.to_datetime(delivered["activity_week"]).dt.to_period("W").dt.start_time

    # Merge orders with cohort
    merged = delivered.merge(customers[["customer_id", "cohort_week"]], on="customer_id", how="left")
    merged["weeks_since_signup"] = (merged["activity_week"] - merged["cohort_week"]).dt.days / 7
    merged = merged[merged["weeks_since_signup"].between(0, max_weeks)]

    weekly_ltv = (
        merged.groupby(["cohort_week", "weeks_since_signup"])
        .agg(total_gmv=("total_price", "sum"), customers=("customer_id", "nunique"))
        .reset_index()
    )
    cohort_sizes = customers.groupby("cohort_week")["customer_id"].nunique().rename("cohort_size")
    weekly_ltv = weekly_ltv.merge(cohort_sizes, on="cohort_week")
    weekly_ltv["ltv_per_customer"] = weekly_ltv["total_gmv"] / weekly_ltv["cohort_size"]

    # Pivot for plotting
    ltv_pivot = weekly_ltv.pivot(index="cohort_week", columns="weeks_since_signup", values="ltv_per_customer")
    ltv_pivot = ltv_pivot.cumsum(axis=1)

    return ltv_pivot


def plot_ltv_curves(ltv_pivot: pd.DataFrame, output_path: str):
    """Plot LTV curves by cohort."""
    plt.figure(figsize=(12, 7))
    top_cohorts = ltv_pivot.iloc[::-1].head(8)  # show last 8 cohorts
    for cohort in top_cohorts.index:
        plt.plot(ltv_pivot.columns, ltv_pivot.loc[cohort], marker="o", label=str(cohort.date()), alpha=0.8)

    plt.title("Cumulative LTV by Cohort (₹ per customer)", fontsize=16, pad=20)
    plt.xlabel("Weeks Since Signup", fontsize=12)
    plt.ylabel("Cumulative GMV per Customer (₹)", fontsize=12)
    plt.legend(title="Cohort Week", fontsize=8, loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"     Saved LTV curves → {output_path}")


def run(data_dir: str, output_dir: str):
    print("[1/3] Loading data...")
    customers, orders = load_data(data_dir)
    print(f"     {len(customers):,} customers, {len(orders):,} orders")

    print("[2/3] Building cohort retention matrix...")
    matrix, cohort_sizes = cohort_retention_matrix(customers, orders)
    plot_retention_heatmap(matrix, os.path.join(output_dir, "cohort_retention.png"))

    print("[3/3] Computing LTV curves...")
    ltv_pivot = cohort_ltv_curve(customers, orders)
    plot_ltv_curves(ltv_pivot, os.path.join(output_dir, "cohort_ltv.png"))

    print("Done!")


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    data_dir = str(base / "data" / "sample_data")
    output_dir = str(base / "outputs")
    os.makedirs(output_dir, exist_ok=True)
    run(data_dir, output_dir)
