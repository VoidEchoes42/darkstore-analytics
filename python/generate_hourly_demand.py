"""
Generate hourly_demand.csv from orders + order_items (replaces SQL Module 04 Q4.1).
This is the input for demand_forecasting.py
"""
import pandas as pd
import os

DATA_DIR = "data/sample_data"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading orders and order_items...")
orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"), usecols=["order_id", "store_id", "order_status", "order_placed_at"])
order_items = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"), usecols=["order_item_id", "order_id", "product_id", "quantity", "total_price"])
products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"), usecols=["product_id", "product_name", "category_id", "category_name"])

print("Merging and aggregating...")
merged = orders.merge(order_items, on="order_id").merge(products, on="product_id")
merged = merged[merged["order_status"] == "delivered"]
merged["order_placed_at"] = pd.to_datetime(merged["order_placed_at"])
merged["order_date"] = merged["order_placed_at"].dt.date
merged["hour_of_day"] = merged["order_placed_at"].dt.hour

hourly = merged.groupby(["store_id", "product_id", "product_name", "category_name", "order_date", "hour_of_day"]).agg(
    orders=("order_id", "nunique"),
    units_sold=("quantity", "sum"),
    revenue=("total_price", "sum")
).reset_index()

out_path = os.path.join(OUTPUT_DIR, "hourly_demand.csv")
hourly.to_csv(out_path, index=False)
print(f"Generated {len(hourly):,} rows -> {out_path}")
print(f"Covering {hourly['store_id'].nunique()} stores x {hourly['product_id'].nunique()} products")
