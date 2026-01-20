import random
from datetime import date, timedelta
import pandas as pd

# ---- Config ----
N_ROWS = 100_000               # change to 50_000, 200_000, 500_000 if you want
START_DATE = date(2024, 1, 1)  # spread across 2 years
END_DATE = date(2025, 12, 31)
OUT_PATH = "data/sample.csv"   # overwrite your current sample.csv

random.seed(42)

# ---- Catalog (category -> items with base prices) ----
CATALOG = {
    "Clothing": {
        "Hoodie": 55.00, "Socks": 6.00, "Jacket": 120.00, "T-Shirt": 22.00,
        "Jeans": 65.00, "Sweatpants": 48.00, "Cap": 18.00, "Sneakers": 95.00
    },
    "Beauty": {
        "Moisturizer": 18.50, "Lip Balm": 3.99, "Serum": 28.00, "Shampoo": 12.50,
        "Conditioner": 12.50, "Sunscreen": 16.00, "Face Wash": 11.00
    },
    "Electronics": {
        "Headphones": 79.99, "Mouse": 22.00, "Keyboard": 55.00, "USB-C Cable": 9.99,
        "Smartwatch": 149.99, "Bluetooth Speaker": 45.00, "Power Bank": 29.99
    },
    "Home": {
        "Blender": 49.99, "Toaster": 34.99, "Coffee Maker": 79.99, "Lamp": 24.99,
        "Pillow Set": 29.99, "Vacuum": 129.99, "Air Fryer": 99.99
    },
}

SHIPPING_TYPES = ["Standard", "Express"]
GENDERS = ["M", "F"]

# Discount distribution (more realistic: mostly 0–15, sometimes 20–40)
DISCOUNT_BUCKETS = [
    (0, 45),   # 45% of rows have 0%
    (5, 15),   # 30% have 5-15%
    (15, 25),  # 20% have 15-25%
    (25, 40),  # 5% have 25-40%
]
DISCOUNT_WEIGHTS = [0.45, 0.30, 0.20, 0.05]

def random_date(start: date, end: date) -> date:
    days = (end - start).days
    d = start + timedelta(days=random.randint(0, days))
    # add seasonality: more purchases in Nov/Dec and weekends
    boost = 0
    if d.month in (11, 12):
        boost += 2
    if d.weekday() in (5, 6):  # Sat/Sun
        boost += 1
    # simple trick: if boost > 0, nudge date selection to keep it but increase chance via re-roll
    if boost > 0 and random.random() < 0.25 * boost:
        return d
    return d

def pick_discount_pct() -> int:
    bucket = random.choices(DISCOUNT_BUCKETS, weights=DISCOUNT_WEIGHTS, k=1)[0]
    low, high = bucket
    if low == high:
        return low
    return random.randint(low, high)

def pick_quantity(category: str) -> int:
    # smaller items tend to have higher quantity
    if category in ("Beauty",):
        return random.choices([1, 2, 3, 4], weights=[0.35, 0.35, 0.20, 0.10], k=1)[0]
    if category in ("Clothing",):
        return random.choices([1, 2, 3], weights=[0.55, 0.30, 0.15], k=1)[0]
    return random.choices([1, 2], weights=[0.80, 0.20], k=1)[0]

def price_with_noise(base: float) -> float:
    # small randomness around base price
    noise = random.uniform(-0.06, 0.06)  # +/- 6%
    p = base * (1 + noise)
    return round(max(0.99, p), 2)

def gen_customer_id(i: int, n_customers: int) -> str:
    return f"C{str(i % n_customers + 1).zfill(4)}"

def gen_age() -> int:
    # weighted age distribution
    bands = [
        (18, 24, 0.22),
        (25, 34, 0.28),
        (35, 44, 0.22),
        (45, 54, 0.16),
        (55, 70, 0.12),
    ]
    r = random.random()
    cum = 0
    for lo, hi, w in bands:
        cum += w
        if r <= cum:
            return random.randint(lo, hi)
    return random.randint(25, 40)

def subscription_for_customer(is_repeat_customer: bool) -> str:
    # repeat customers more likely subscribed
    if is_repeat_customer:
        return "Yes" if random.random() < 0.45 else "No"
    return "Yes" if random.random() < 0.20 else "No"

def shipping_for_row(subscription: str) -> str:
    # subscribers slightly more likely to use standard shipping
    if subscription == "Yes":
        return "Express" if random.random() < 0.35 else "Standard"
    return "Express" if random.random() < 0.45 else "Standard"

def main():
    # pick number of customers to create repeat behavior
    n_customers = max(500, min(12000, N_ROWS // 8))

    rows = []
    for order_id in range(1, N_ROWS + 1):
        order_date = random_date(START_DATE, END_DATE)

        # repeat customers: many orders come from a smaller set of customers
        customer_index = int(random.random() ** 2 * n_customers)  # skew toward smaller IDs
        customer_id = f"C{str(customer_index + 1).zfill(4)}"

        gender = random.choices(GENDERS, weights=[0.48, 0.52], k=1)[0]
        age = gen_age()

        category = random.choice(list(CATALOG.keys()))
        item = random.choice(list(CATALOG[category].keys()))
        quantity = pick_quantity(category)

        base_price = CATALOG[category][item]
        price = price_with_noise(base_price)

        discount_pct = pick_discount_pct()
        # small boost discounts during holiday months
        if order_date.month in (11, 12) and random.random() < 0.25:
            discount_pct = min(40, discount_pct + random.choice([5, 10]))

        # treat customers with lower index as more repeat -> more subscription
        is_repeat = (customer_index < int(0.35 * n_customers))
        subscription = subscription_for_customer(is_repeat)
        shipping_type = shipping_for_row(subscription)

        rows.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": customer_id,
            "gender": gender,
            "age": age,
            "category": category,
            "item": item,
            "quantity": quantity,
            "price": price,
            "discount_pct": discount_pct,
            "shipping_type": shipping_type,
            "subscription": subscription
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print(f"✅ Wrote {len(df):,} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()
