"""
Generate 500 delivery partners for darkstore analytics.
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

partners = []
for i in range(1, 501):
    city = random.choice(list(CITIES.keys()))
    zone = random.choice(CITIES[city])
    shift_hour = random.choice([6, 8, 10, 14, 18, 22])
    end_hour = (shift_hour + random.randint(4, 8)) % 24

    partners.append({
        "partner_id": i,
        "name": f"Partner_{i:03d}",
        "phone_number": f"+91{random.randint(7000000000, 9999999999)}",
        "city": city,
        "zone": zone,
        "vehicle_type": random.choices(["bike", "scooter", "cycle"], weights=[40, 55, 5])[0],
        "shift_start_time": f"{shift_hour:02d}:00",
        "shift_end_time": f"{end_hour:02d}:00",
        "is_active": random.choice([True] * 85 + [False] * 15),
        "joined_at": f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "avg_rating": round(random.uniform(3.2, 5.0), 1),
    })

filepath = os.path.join(OUTPUT_DIR, "delivery_partners.csv")
fieldnames = partners[0].keys()
with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(partners)

print(f"Generated {len(partners)} delivery partners -> {filepath}")
