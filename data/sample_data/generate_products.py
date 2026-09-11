"""
Generate 200+ products across 12 FMCG categories for darkstore analytics.
"""
import random
import csv
import os

random.seed(42)

CATEGORIES = [
    "Snacks", "Beverages", "Dairy", "Fruits & Vegetables", "Bakery",
    "Personal Care", "Household", "Baby Care", "Meat & Seafood",
    "Frozen Foods", "Grocery & Staples", "Ice Cream"
]

PRODUCT_TEMPLATES = {
    "Snacks": [
        ("Lays Classic", 20, 20), ("Lays Magic Masala", 20, 20), ("Kurkure Masala Munch", 20, 18),
        ("Haldiram's Bhujia", 60, 55), ("Haldiram's Namkeen Mix", 100, 90),
        ("Parle-G", 10, 10), ("Britannia Good Day", 30, 28), ("Oreo Biscuits", 30, 28),
        ("Hide & Seek", 30, 28), ("Dark Fantasy", 40, 38), ("Bourbon", 25, 23),
        ("Too Yumm Multigrain", 50, 45), ("Yoga Bar Granola", 120, 110),
        ("Kellogg's Corn Flakes", 180, 160), ("Kellogg's Muesli", 250, 230),
    ],
    "Beverages": [
        ("Coca-Cola 600ml", 35, 35), ("Pepsi 600ml", 35, 35), ("Sprite 600ml", 35, 35),
        ("Thumbs Up 600ml", 35, 35), ("Maaza 600ml", 35, 35),
        ("Amul Masti 500ml", 20, 18), ("Yakult 5-pack", 90, 85),
        ("Real Fruit Juice 1L", 110, 100), ("Tropicana 1L", 120, 108),
        ("Bournvita 500g", 195, 185), ("Horlicks 500g", 190, 178),
        ("Nescafe Coffee", 150, 138), ("Bru Instant Coffee", 120, 108),
        ("Tetley Green Tea", 175, 160), ("Lipton Yellow Label", 140, 128),
    ],
    "Dairy": [
        ("Amul Cow Milk 1L", 60, 58), ("Amul Toned Milk 1L", 55, 53),
        ("Amul Butter 100g", 52, 50), ("Amul Cheese Slices 200g", 135, 128),
        ("Amul Paneer 200g", 85, 80), ("Mother Dairy Curd 400g", 30, 28),
        ("Epigamia Greek Yogurt", 50, 45), ("Nestle Dahi", 35, 33),
    ],
    "Fruits & Vegetables": [
        ("Banana (1 dozen)", 40, 38), ("Apples (1kg)", 120, 110),
        ("Tomato (1kg)", 30, 25), ("Potato (1kg)", 25, 20),
        ("Onion (1kg)", 30, 25), ("Spinach 250g", 20, 17),
        ("Broccoli 500g", 60, 52), ("Carrot 1kg", 40, 35),
    ],
    "Bakery": [
        ("Britannia Bread", 35, 32), ("Whole Wheat Bread", 40, 36),
        ("Brown Bread", 35, 32), ("Multigrain Bread", 50, 45),
        ("Cream Rolls 4pc", 40, 36), ("Croissant", 45, 40),
        ("Chocolate Muffin", 55, 48),
    ],
    "Personal Care": [
        ("Colgate Strong Teeth 200g", 85, 80), ("Pepsodent 200g", 75, 70),
        ("Head & Shoulders 180ml", 195, 180), ("Dove Shampoo 180ml", 210, 195),
        ("Lifebuoy Soap", 28, 25), ("Dove Soap", 55, 50),
        ("Lux Soap", 35, 30), ("Pears Soap", 45, 40),
        ("Gillette Razor", 45, 40), ("Veet Wax Strips", 120, 110),
        ("Nivea Face Cream 50ml", 120, 108), ("Lakme Face Wash 100ml", 140, 128),
        ("Himalaya Face Wash 100ml", 110, 100), ("Mamaearth Sunscreen", 250, 230),
    ],
    "Household": [
        ("Surf Excel 1kg", 150, 138), ("Ariel 1kg", 210, 195),
        ("Tide 1kg", 140, 128), ("Vim Dish Bar", 20, 17),
        ("Pril Dishwash 500ml", 75, 68), ("Harpic 500ml", 85, 78),
        ("Lizol Floor Cleaner 1L", 110, 98), ("Colin 500ml", 75, 68),
        ("Mortein Refill 450ml", 90, 82), ("All Out Liquid 45ml", 55, 48),
        ("Scotch Brite Scrub", 50, 45), ("Garbage Bags (30 pcs)", 90, 82),
    ],
    "Baby Care": [
        ("Pampers Large 20pc", 750, 699), ("Huggies Large 20pc", 720, 669),
        ("Johnson's Baby Powder 400g", 195, 178), ("Johnson's Baby Soap", 55, 50),
        ("Cerelac 300g", 170, 155), ("Nestle Cerelac Stage 2", 190, 175),
        ("Himalaya Baby Lotion", 120, 108), ("Sebamed Baby Lotion", 250, 230),
    ],
    "Meat & Seafood": [
        ("Chicken Breast 500g", 180, 170), ("Mutton Curry Cut 500g", 320, 300),
        ("Fish Fillet 500g", 250, 235), ("Prawns 250g", 280, 260),
        ("Eggs 12pc", 80, 75), ("Soya Chunks 200g", 60, 52),
    ],
    "Frozen Foods": [
        ("McCain Fries 400g", 120, 112), ("McCain Smiles 400g", 120, 112),
        ("Ahluwalia Chicken Nuggets", 180, 168), ("Soya Chunks 200g", 60, 52),
        ("Frozen Peas 500g", 80, 72), ("Frozen Corn 500g", 70, 63),
    ],
    "Grocery & Staples": [
        ("Aashirvaad Atta 5kg", 250, 235), ("Fortune Atta 5kg", 230, 218),
        ("India Gate Basmati 1kg", 150, 138), ("Tata Salt 1kg", 22, 20),
        ("Tata Tea Premium 250g", 95, 88), ("Bru Gold 100g", 55, 50),
        ("Maggi 2-Minute Noodles 4pc", 60, 55), ("Yippee Noodles 4pc", 55, 50),
        ("Knorr Soup 45g", 25, 22), ("MTR Ready Meals", 85, 78),
        ("Everest Garam Masala 50g", 45, 42), ("MDH Masala 50g", 40, 37),
        ("Toor Dal 1kg", 140, 130), ("Chana Dal 1kg", 120, 110),
        ("Moong Dal 1kg", 110, 100), ("Sugar 1kg", 48, 44),
        ("Cooking Oil 1L", 140, 128), ("Fortune Oil 1L", 150, 138),
    ],
    "Ice Cream": [
        ("Amul Vanilla Tub 500ml", 85, 80), ("Amul Chocolate Tub 500ml", 95, 88),
        ("Kwality Walls Magnum", 120, 110), ("Cornetto Choco", 30, 28),
        ("Amul Masti Icecream Cup", 20, 18),
    ],
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

products = []
product_id = 1

for cat_idx, category in enumerate(CATEGORIES):
    templates = PRODUCT_TEMPLATES.get(category, [])
    # Add some randomized variants
    for name, mrp, price in templates:
        products.append({
            "product_id": product_id,
            "product_name": name,
            "category_id": cat_idx + 1,
            "category_name": category,
            "brand": name.split()[0] if name else "Generic",
            "unit": random.choice(["1L", "500g", "1kg", "200g", "100g", "pack", "pc", "dozen"]),
            "mrp": mrp,
            "selling_price": price,
            "cost_price": round(price * random.uniform(0.55, 0.75), 2),
            "weight_grams": random.randint(50, 2000),
            "is_available": random.choice([True] * 9 + [False]),
        })
        product_id += 1

# Ensure 200+ products
while len(products) < 205:
    cat = random.choice(CATEGORIES)
    products.append({
        "product_id": product_id,
        "product_name": f"{cat} Product {product_id}",
        "category_id": CATEGORIES.index(cat) + 1,
        "category_name": cat,
        "brand": "Generic",
        "unit": "1pc",
        "mrp": random.randint(20, 200),
        "selling_price": random.randint(15, 180),
        "cost_price": round(random.randint(10, 150) * 0.7, 2),
        "weight_grams": random.randint(50, 1000),
        "is_available": True,
    })
    product_id += 1

filepath = os.path.join(OUTPUT_DIR, "products.csv")
fieldnames = products[0].keys()
with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(products)

print(f"Generated {len(products)} products across {len(CATEGORIES)} categories -> {filepath}")

# Write categories too
categories_path = os.path.join(OUTPUT_DIR, "..", "categories.csv")
with open(categories_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["category_id", "category_name", "parent_category", "is_perishable", "shelf_life_days"])
    perishable = {"Fruits & Vegetables", "Dairy", "Meat & Seafood", "Bakery", "Ice Cream"}
    for i, cat in enumerate(CATEGORIES, 1):
        writer.writerow([i, cat, "FMCG", cat in perishable, random.randint(1, 30) if cat in perishable else 180])
