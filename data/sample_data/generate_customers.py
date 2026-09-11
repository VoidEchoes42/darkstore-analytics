"""
Generate 50,000 customers for darkstore analytics.
"""
import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

CITIES = {
    "Bangalore": ["Koramangala", "HSR Layout", "Indiranagar", "JP Nagar", "Whitefield"],
    "Delhi": ["South Delhi", "East Delhi", "West Delhi", "North Delhi", "Central Delhi"],
    "Mumbai": ["Bandra", "Andheri", "Powai", "Goregaon", "Malad"],
    "NCR": ["Gurgaon", "Noida", "Faridabad", "Ghaziabad"],
    "Hyderabad": ["Hitech City", "Banjara Hills", "Secunderabad", "Gachibowli"],
}

CHANNELS = ["organic", "referral", "paid_ads", "offline"]
CHANNEL_WEIGHTS = [40, 20, 30, 10]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

N = 50000
customers = []
customer_id = 1
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 8, 31)
date_range_days = (end_date - start_date).days

for idx in range(N):
    city = random.choice(list(CITIES.keys()))
    zone = random.choice(CITIES[city])
    signup_offset = random.randint(0, date_range_days)
    signup_date = (start_date + timedelta(days=signup_offset)).strftime("%Y-%m-%d")

    customers.append({
        "customer_id": customer_id,
        "phone_number": "+91" + str(random.randint(7000000000, 9999999999)),
        "name": "Customer_" + str(customer_id),
        "city": city,
        "zone": zone,
        "signup_date": signup_date,
        "acquisition_channel": random.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0],
        "total_orders": 0,
        "total_gmv": 0,
        "is_active": random.choice([True] * 8 + [False] * 2),
    })
    customer_id += 1

filepath = os.path.join(OUTPUT_DIR, "customers.csv")
fieldnames = list(customers[0].keys())
with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(customers)

print("Generated {} customers -> {}".format(len(customers), filepath))
