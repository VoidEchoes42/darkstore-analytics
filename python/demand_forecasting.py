"""
Demand Forecasting — Prophet/ARIMA hourly demand by store x SKU.
Input:  SQL Module 04 output (hourly aggregation)
Output: forecasts.csv + forecast_accuracy_report.txt
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    HAS_ARIMA = True
except ImportError:
    HAS_ARIMA = False


def load_hourly_demand(csv_path: str) -> pd.DataFrame:
    """Load hourly demand data from SQL Module 04 output."""
    df = pd.read_csv(csv_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["datetime"] = pd.to_datetime(
        df["order_date"].astype(str) + " " + df["hour_of_day"].astype(str).str.zfill(2) + ":00:00"
    )
    df = df.rename(columns={"datetime": "ds", "units_sold": "y"})
    df = df.sort_values(["store_id", "product_id", "ds"]).reset_index(drop=True)
    return df


def train_prophet(group: pd.DataFrame, horizon: int = 168) -> pd.DataFrame:
    """Train Prophet on one (store_id, product_id) group and forecast horizon hours ahead."""
    ts = group[["ds", "y"]].drop_duplicates("ds").sort_values("ds").reset_index(drop=True)
    if len(ts) < 24:
        return pd.DataFrame()

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        interval_width=0.8,
        mcmc_samples=0,  # Use MAP estimation instead of full MCMC (faster)
    )
    model.fit(ts)

    future = model.make_future_dataframe(periods=horizon, freq="h")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).copy()
    result["store_id"] = group["store_id"].iloc[0]
    result["product_id"] = group["product_id"].iloc[0]
    result = result.rename(columns={"ds": "datetime", "yhat": "forecast_units",
                                     "yhat_lower": "lower_bound", "yhat_upper": "upper_bound"})
    return result


def train_arima(group: pd.DataFrame, horizon: int = 168) -> pd.DataFrame:
    """Fallback: ARIMA forecast for one (store_id, product_id) group."""
    ts = group[["ds", "y"]].drop_duplicates("ds").sort_values("ds").reset_index(drop=True)
    if len(ts) < 24:
        return pd.DataFrame()

    try:
        model = ARIMA(ts["y"], order=(2, 1, 2))
        fitted = model.fit()
        forecast = fitted.forecast(steps=horizon)
        std = fitted.get_forecast(steps=horizon).conf_int()
        lower = std.iloc[:, 0].values
        upper = std.iloc[:, 1].values

        last_dt = ts["ds"].iloc[-1]
        future_dts = pd.date_range(start=last_dt + pd.Timedelta(hours=1), periods=horizon, freq="h")

        result = pd.DataFrame({
            "datetime": future_dts,
            "forecast_units": np.maximum(forecast.values, 0),
            "lower_bound": np.maximum(lower, 0),
            "upper_bound": np.maximum(upper, 0),
            "store_id": group["store_id"].iloc[0],
            "product_id": group["product_id"].iloc[0],
        })
        return result
    except Exception:
        return pd.DataFrame()


def evaluate(group: pd.DataFrame, horizon: int = 168) -> dict:
    """Evaluate forecast accuracy using last 168 hours as holdout."""
    ts = group[["ds", "y", "store_id", "product_id"]].drop_duplicates("ds").sort_values("ds").reset_index(drop=True)
    if len(ts) < horizon + 24:
        return None

    train = ts.iloc[:-horizon]
    test = ts.iloc[-horizon:]

    if HAS_PROPHET:
        preds = train_prophet(train, horizon=horizon)
    elif HAS_ARIMA:
        preds = train_arima(train, horizon=horizon)
    else:
        return None

    if preds.empty:
        return None

    merged = test.merge(preds[["datetime", "forecast_units"]], left_on="ds", right_on="datetime", how="inner")
    if len(merged) < 10:
        return None

    actual = merged["y"].values
    predicted = merged["forecast_units"].values

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, 0.1))) * 100

    return {
        "store_id": group["store_id"].iloc[0],
        "product_id": group["product_id"].iloc[0],
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "holdout_points": len(merged),
    }


def run(input_csv: str, output_dir: str, top_n: int = 5):
    """Main pipeline: load → forecast → evaluate → save."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"[1/4] Loading hourly demand from {input_csv}")
    df = load_hourly_demand(input_csv)
    print(f"     Loaded {len(df):,} rows for {df['store_id'].nunique()} stores x {df['product_id'].nunique()} products")

    # Select top N store-SKU pairs by total volume for forecasting
    top_pairs = df.groupby(["store_id", "product_id"])["y"].sum().nlargest(top_n)
    print(f"[2/4] Forecasting demand for top {top_n} (store, SKU) pairs")

    all_forecasts = []
    for (store_id, product_id), _ in top_pairs.items():
        group = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)]
        if HAS_PROPHET:
            fc = train_prophet(group)
        elif HAS_ARIMA:
            fc = train_arima(group)
        else:
            print("     WARNING: Neither Prophet nor ARIMA available. Skipping forecast.")
            break
        if not fc.empty:
            all_forecasts.append(fc)

    if all_forecasts:
        forecasts_df = pd.concat(all_forecasts, ignore_index=True)
        out_path = os.path.join(output_dir, "forecasts.csv")
        forecasts_df.to_csv(out_path, index=False)
        print(f"     Saved {len(forecasts_df):,} forecast rows → {out_path}")
    else:
        print("     No forecasts generated.")

    print(f"[3/4] Evaluating forecast accuracy (holdout on last 72h)")
    evaluations = []
    # Evaluate groups that have enough data
    group_sizes = df.groupby(["store_id", "product_id"]).size()
    dense_groups = group_sizes[group_sizes >= 200].index.tolist()
    import random; random.seed(42)
    sampled = random.sample(dense_groups, k=min(6, len(dense_groups)))
    for store_id, product_id in sampled:
        group = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)].copy()
        ts = group[["ds", "y", "store_id", "product_id"]].drop_duplicates("ds").sort_values("ds").reset_index(drop=True)
        if len(ts) < 120:
            continue
        # Build daily series for simpler evaluation
        daily = ts.set_index("ds")["y"].resample("D").sum().fillna(0).reset_index()
        daily = daily.rename(columns={"date": "ds"})
        daily["ds"] = pd.to_datetime(daily["ds"]).dt.tz_localize(None)
        if len(daily) < 30:
            continue
        holdout_days = min(7, len(daily) // 5)
        train_daily = daily.iloc[:-holdout_days][["ds", "y"]].rename(columns={"ds": "ds", "y": "y"})
        test_daily = daily.iloc[-holdout_days:]
        if HAS_PROPHET:
            m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
            m.fit(train_daily)
            future = m.make_future_dataframe(periods=holdout_days, freq="D")
            fc = m.predict(future)[["ds", "yhat"]].tail(holdout_days)
            fc["ds"] = pd.to_datetime(fc["ds"]).dt.tz_localize(None)
            merged = test_daily.merge(fc, on="ds", how="inner")
            if len(merged) >= 3:
                actual = merged["y"].values
                predicted = merged["yhat"].values
                mae = np.mean(np.abs(actual - predicted))
                rmse = np.sqrt(np.mean((actual - predicted) ** 2))
                mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, 0.1))) * 100
                evaluations.append({
                    "store_id": store_id, "product_id": product_id,
                    "mae": round(mae, 2), "rmse": round(rmse, 2),
                    "mape": round(mape, 2), "holdout_points": len(merged),
                })
                print(f"     store={store_id} prod={product_id}: MAPE={mape:.1f}% ({len(merged)} days)")

    eval_df = pd.DataFrame(evaluations)
    if not eval_df.empty:
        eval_path = os.path.join(output_dir, "forecast_accuracy_report.txt")
        with open(eval_path, "w") as f:
            f.write(f"{'='*60}\n")
            f.write(f"Demand Forecast Accuracy Report\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Model: {'Prophet' if HAS_PROPHET else 'ARIMA (fallback)'}\n")
            f.write(f"Store-SKU pairs evaluated: {len(eval_df)}\n\n")
            f.write(f"{'Store ID':<12}{'Product ID':<14}{'MAE':<10}{'RMSE':<10}{'MAPE%':<10}{'Points':<10}\n")
            f.write(f"{'-'*66}\n")
            for _, row in eval_df.iterrows():
                f.write(f"{row['store_id']:<12}{row['product_id']:<14}{row['mae']:<10}{row['rmse']:<10}{row['mape']:<10}{row['holdout_points']:<10}\n")
            f.write(f"\n{'='*60}\n")
            f.write(f"AVERAGE across all pairs:\n")
            f.write(f"  MAE:  {eval_df['mae'].mean():.2f}\n")
            f.write(f"  RMSE: {eval_df['rmse'].mean():.2f}\n")
            f.write(f"  MAPE: {eval_df['mape'].mean():.2f}%\n")
        print(f"     Avg MAPE: {eval_df['mape'].mean():.2f}% across {len(eval_df)} pairs")
        print(f"     Saved → {eval_path}")
    else:
        print("     No evaluations computed (not enough data per group).")

    print(f"[4/4] Done. Outputs in {output_dir}")


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    input_csv = str(base / "data" / "sample_data" / "hourly_demand.csv")
    output_dir = str(base / "outputs")

    if not os.path.exists(input_csv):
        print(f"ERROR: {input_csv} not found.")
        print("Run the SQL Module 04 Q4.1 query first and export to CSV.")
        sys.exit(1)

    run(input_csv, output_dir)
