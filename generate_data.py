"""
generate_data.py
Generates a realistic retail sales dataset for EDA internship project.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
N = 5000
START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)

CATEGORIES  = ["Electronics", "Clothing", "Furniture", "Groceries", "Sports", "Books", "Toys"]
REGIONS     = ["North", "South", "East", "West", "Central"]
SEGMENTS    = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES  = ["Standard Class", "Second Class", "First Class", "Same Day"]
PAYMENT     = ["Credit Card", "Debit Card", "Cash", "UPI", "Net Banking"]

PRODUCTS = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Smart TV", "Camera"],
    "Clothing":    ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes", "Saree"],
    "Furniture":   ["Chair", "Table", "Sofa", "Bookshelf", "Bed Frame", "Wardrobe"],
    "Groceries":   ["Rice (5kg)", "Oil (1L)", "Sugar (1kg)", "Flour (2kg)", "Spices", "Pulses"],
    "Sports":      ["Cricket Bat", "Football", "Yoga Mat", "Dumbbells", "Cycle", "Badminton Set"],
    "Books":       ["Python Programming", "Data Science Guide", "Novel", "Self-Help", "Textbook", "Comics"],
    "Toys":        ["Lego Set", "Doll", "Board Game", "Action Figure", "Puzzle", "RC Car"],
}

PRICE_RANGE = {
    "Electronics": (5000, 85000),
    "Clothing":    (300, 8000),
    "Furniture":   (2000, 50000),
    "Groceries":   (50, 500),
    "Sports":      (500, 15000),
    "Books":       (150, 1500),
    "Toys":        (200, 5000),
}

CITY_BY_REGION = {
    "North":   ["Delhi", "Chandigarh", "Lucknow", "Jaipur", "Agra"],
    "South":   ["Chennai", "Bangalore", "Hyderabad", "Kochi", "Coimbatore"],
    "East":    ["Kolkata", "Bhubaneswar", "Patna", "Guwahati", "Ranchi"],
    "West":    ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nagpur"],
    "Central": ["Bhopal", "Indore", "Raipur", "Jabalpur", "Gwalior"],
}

# ── Generate ───────────────────────────────────────────────────────────────────
dates = [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) for _ in range(N)]
dates.sort()

categories  = np.random.choice(CATEGORIES, N, p=[0.20, 0.18, 0.12, 0.18, 0.12, 0.10, 0.10])
products    = [random.choice(PRODUCTS[c]) for c in categories]
regions     = np.random.choice(REGIONS, N)
cities      = [random.choice(CITY_BY_REGION[r]) for r in regions]
segments    = np.random.choice(SEGMENTS, N, p=[0.52, 0.30, 0.18])
ship_modes  = np.random.choice(SHIP_MODES, N, p=[0.60, 0.20, 0.14, 0.06])
payments    = np.random.choice(PAYMENT, N, p=[0.30, 0.25, 0.15, 0.20, 0.10])

unit_prices = [round(random.uniform(*PRICE_RANGE[c]), 2) for c in categories]
quantities  = np.random.randint(1, 10, N)
discounts   = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], N,
                               p=[0.35, 0.15, 0.20, 0.15, 0.08, 0.04, 0.03])

sales       = [round(u * q * (1 - d), 2) for u, q, d in zip(unit_prices, quantities, discounts)]
profit_pct  = np.random.uniform(0.05, 0.35, N)
profits     = [round(s * p, 2) for s, p in zip(sales, profit_pct)]

# Inject missing values (realistic ~3%)
def inject_nulls(arr, pct=0.03):
    arr = list(arr)
    idx = random.sample(range(len(arr)), int(len(arr) * pct))
    for i in idx:
        arr[i] = None
    return arr

discounts_null = inject_nulls(discounts, 0.025)
profits_null   = inject_nulls(profits,   0.020)
ship_modes_n   = inject_nulls(ship_modes, 0.015)

df = pd.DataFrame({
    "Order_ID":       [f"ORD-{str(i+1000).zfill(5)}" for i in range(N)],
    "Order_Date":     [d.strftime("%Y-%m-%d") for d in dates],
    "Ship_Mode":      ship_modes_n,
    "Customer_ID":    [f"CUST-{random.randint(1000,2500):04d}" for _ in range(N)],
    "Segment":        segments,
    "City":           cities,
    "Region":         regions,
    "Category":       categories,
    "Product_Name":   products,
    "Payment_Mode":   payments,
    "Unit_Price":     unit_prices,
    "Quantity":       quantities,
    "Discount":       discounts_null,
    "Sales":          sales,
    "Profit":         profits_null,
})

out = os.path.join(os.path.dirname(__file__), "..", "data", "retail_sales.csv")
df.to_csv(out, index=False)
print(f"✅  Dataset saved → {out}  ({len(df):,} rows × {len(df.columns)} columns)")
