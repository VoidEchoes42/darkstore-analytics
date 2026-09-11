"""
Generate 50 stores across 5 Indian cities for darkstore analytics.
"""
import random
import csv
import os

random.seed(42)

CITIES = {
    "Bangalore": ["Koramangala", "HSR Layout", "Indiranagar", "JP Nagar", "Whitefield"],
    "Delhi": ["South Delhi", "East Delhi", "West Delhi", "North Delhi", "Central Delhi"],
    "Mumbai": ["Bandra", "Andheri", "Powai", "Goregaon", "Malad"],
    "NCR": ["Gurgaon", "Noida", "Faridabad", "Ghaziabad"],
    "Hyderabad": ["Hitech City", "Banjara Hills", "Secunderabad", "Gachibowli"],
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

store_names = [
    "DS-BLR-{num:03d}", "DS-DEL-{num:03d}", "DS-MUM-{num:03d}",
    "DS-NCR-{num:03d}", "DS-HYD-{num:03d}"
]

city_prefix = ["Bangalore", "Delhi", "Mumbai", "NCR", "Hyderabad"]

stores = []
store_id = 1

for c_idx, (city, zones) in enumerate(CITIES.items()):
    for zone in zones:
        for i in range(2):  # 2 stores per zone = 50 total
            lat = round(random.uniform(12.9, 19.1), 6)
            lng = round(random.uniform(77.5, 72.9), 6)
            cap_hour = random.choice([40, 50, 60, 70, 80])
            cap_day = cap_hour * 12  # 12 active hours
            sla = random.choice([8, 10, 12, 15])
            stores.append({
                "store_id": store_id,
                "store_name": store_names[c_idx].format(num=store_id),
                "city": city,
                "zone": zone,
                "address": f"{random.randint(1,99)} {zone} Main Road, {city}",
                "latitude": lat,
                "longitude": lng,
                "capacity_orders_per_hour": cap_hour,
                "capacity_orders_per_day": cap_day,
                "sla_target_minutes": sla,
                "is_active": True,
                "opened_at": f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            })
            store_id += 1

filepath = os.path.join(OUTPUT_DIR, "stores.csv")
with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=stores[0].keys())
    writer.writeheader()
    writer.writerows(stores)

print(f"Generated {len(stores)} stores -> {filepath}")
