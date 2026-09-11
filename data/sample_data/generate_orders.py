"""
Generate 1M+ orders for darkstore analytics with realistic patterns:
  - Dinner rush spike (6-9 PM)
  - Lower weekday afternoons
  - ~5% SLA breach rate (higher during peak)
  - Basket sizes: ₹300-800
  - Order status flow: placed → picked → packed → dispatched → delivered
"""
import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data")
TOTAL_ORDERS = 1_200_000

# Load lookups
def load_csv(fname):
    rows = []
    with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

print("Loading reference data...")
stores = load_csv("stores.csv")
products = load_csv("products.csv")
customers = load_csv("customers.csv")
partners = load_csv("delivery_partners.csv")

store_ids = [int(s["store_id"]) for s in stores]
product_ids = [int(p["product_id"]) for p in products]
customer_ids = [int(c["customer_id"]) for c in customers]
partner_ids = [int(p["partner_id"]) for p in partners if p["is_active"] == "True"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 8, 31)
total_days = (end_date - start_date).days

# Hour weights: higher during 6-9 PM (dinner rush)
HOUR_WEIGHTS = {}
for h in range(24):
    if 18 <= h <= 20:
        HOUR_WEIGHTS[h] = 18  # peak dinner
    elif 11 <= h <= 13:
        HOUR_WEIGHTS[h] = 12  # lunch
    elif 20 <= h <= 21:
        HOUR_WEIGHTS[h] = 10  # late evening
    elif 6 <= h <= 10:
        HOUR_WEIGHTS[h] = 8   # morning
    else:
        HOUR_WEIGHTS[h] = 3   # low traffic

hour_choices = list(HOUR_WEIGHTS.keys())
hour_weights = [HOUR_WEIGHTS[h] for h in hour_choices]

# Seasonality: monsoon months (Jun-Sep) have ~20% more orders
# Monsoons: July=7, Aug=8, Sep=9, June=6

orders_path = os.path.join(DATA_DIR, "orders.csv")
order_items_path = os.path.join(DATA_DIR, "order_items.csv")

print(f"Generating {TOTAL_ORDERS:,} orders...")

with open(orders_path, "w", newline="", encoding="utf-8") as of, \
     open(order_items_path, "w", newline="", encoding="utf-8") as oif:

    order_writer = csv.DictWriter(of, fieldnames=[
        "order_id", "customer_id", "store_id", "partner_id",
        "order_status", "order_placed_at", "picked_at", "packed_at",
        "dispatched_at", "delivered_at", "cancelled_at",
        "cancellation_reason", "sla_target_minutes", "actual_delivery_minutes",
        "is_rain_flag", "is_holiday_flag", "payment_mode"
    ])
    order_writer.writeheader()

    item_writer = csv.DictWriter(oif, fieldnames=[
        "order_item_id", "order_id", "product_id", "quantity",
        "unit_price", "discount_amount", "total_price"
    ])
    item_writer.writeheader()

    order_item_id = 1

    for order_id in range(1, TOTAL_ORDERS + 1):
        # Timestamp
        day_offset = random.randint(0, total_days)
        base_date = start_date + timedelta(days=day_offset)

        # Seasonality: monsoon boost
        month = base_date.month
        seasonality = 1.2 if month in [6, 7, 8, 9] else (0.9 if month in [1, 2] else 1.0)

        # Weekend boost
        weekday = base_date.weekday()
        weekend = 1.15 if weekday >= 5 else 1.0

        # Hour
        hour = random.choices(hour_choices, weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        placed_at = base_date + timedelta(hours=hour, minutes=minute)

        # Weather/holiday flags
        is_rain = random.random() < 0.08  # 8% chance of rain
        is_holiday = random.random() < 0.03  # 3% holidays

        # Store and customer
        store_id = random.choice(store_ids)
        customer_id = random.choice(customer_ids)
        partner_id = random.choice(partner_ids) if random.random() > 0.05 else None

        store = next(s for s in stores if s["store_id"] == str(store_id))
        sla_target = int(store["sla_target_minutes"])

        # Determine status
        is_cancelled = random.random() < 0.03

        # Delivery TAT (in minutes)
        # Base: SLA target + some randomness
        if is_cancelled:
            actual_tat = None
            # Timestamps for cancelled order
            picked = placed_at + timedelta(minutes=random.randint(1, 15))
            packed = picked + timedelta(minutes=random.randint(2, 20))
            status = "cancelled"
            cancelled_at = packed + timedelta(minutes=random.randint(1, 10))
            dispatched_at = None
            delivered_at = None
            cancel_reason = random.choice(["customer_cancelled", "item_out_of_stock", "store_cancelled"])
        else:
            # Simulate stage delays
            picked_at = placed_at + timedelta(minutes=random.randint(1, 12))
            packed_at = picked_at + timedelta(minutes=random.randint(2, 18))
            dispatched_at = packed_at + timedelta(minutes=random.randint(3, 15))

            # Peak hour and rain increase delivery time
            peak_delay = 1.4 if 18 <= hour <= 20 else 1.0
            rain_delay = 1.3 if is_rain else 1.0
            holiday_delay = 1.2 if is_holiday else 1.0

            base_delivery_minutes = int(sla_target * peak_delay * rain_delay * holiday_delay)
            actual_tat = max(base_delivery_minutes + random.randint(-3, 10), 3)

            delivered_at = placed_at + timedelta(minutes=actual_tat)
            cancelled_at = None
            cancel_reason = ""

            # Determine status based on completion
            if actual_tat <= sla_target:
                status = "delivered"
            elif random.random() < 0.3:
                status = "delivered"  # late but delivered
            else:
                status = "delivered"

        # Payment mode
        payment = random.choices(["upi", "cash", "card", "wallet"], weights=[60, 20, 12, 8])[0]

        order_writer.writerow({
            "order_id": order_id,
            "customer_id": customer_id,
            "store_id": store_id,
            "partner_id": partner_id,
            "order_status": status,
            "order_placed_at": placed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "picked_at": picked_at.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
            "packed_at": packed_at.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
            "dispatched_at": dispatched_at.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
            "delivered_at": delivered_at.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
            "cancelled_at": cancelled_at.strftime("%Y-%m-%d %H:%M:%S") if is_cancelled else "",
            "cancellation_reason": cancel_reason,
            "sla_target_minutes": sla_target,
            "actual_delivery_minutes": actual_tat if actual_tat else "",
            "is_rain_flag": is_rain,
            "is_holiday_flag": is_holiday,
            "payment_mode": payment,
        })

        # Generate 1-6 order items
        n_items = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 30, 20, 12, 5, 3])[0]
        basket_total = 0
        chosen_products = random.sample(product_ids, min(n_items, len(product_ids)))

        for prod_id in chosen_products:
            product = next(p for p in products if p["product_id"] == str(prod_id))
            qty = random.randint(1, 3)
            unit_price = float(product["selling_price"])
            discount = round(unit_price * random.uniform(0, 0.1), 2) if random.random() < 0.3 else 0
            total = round((unit_price - discount) * qty, 2)
            basket_total += total

            item_writer.writerow({
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": prod_id,
                "quantity": qty,
                "unit_price": unit_price,
                "discount_amount": discount,
                "total_price": total,
            })
            order_item_id += 1

    print(f"Generated {TOTAL_ORDERS:,} orders and {order_item_id - 1:,} order items")

print("Done!")
