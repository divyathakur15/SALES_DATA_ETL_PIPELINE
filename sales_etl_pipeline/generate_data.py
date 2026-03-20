"""
Script to generate realistic sample sales data (1000 rows).
Run this once to create data/raw/sales_data.csv
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

PRODUCTS = {
    "Laptop Pro":     {"category": "Electronics",   "base_price": 1200, "base_cost": 800},
    "Wireless Mouse": {"category": "Electronics",   "base_price": 35,   "base_cost": 12},
    "USB-C Hub":      {"category": "Electronics",   "base_price": 55,   "base_cost": 20},
    "Office Chair":   {"category": "Furniture",     "base_price": 350,  "base_cost": 180},
    "Standing Desk":  {"category": "Furniture",     "base_price": 600,  "base_cost": 320},
    "Notebook A4":    {"category": "Stationery",    "base_price": 8,    "base_cost": 2},
    "Ballpoint Pens": {"category": "Stationery",    "base_price": 12,   "base_cost": 4},
    "Monitor 27in":   {"category": "Electronics",   "base_price": 450,  "base_cost": 270},
    "Webcam HD":      {"category": "Electronics",   "base_price": 90,   "base_cost": 40},
    "Desk Lamp":      {"category": "Furniture",     "base_price": 45,   "base_cost": 18},
}

CUSTOMERS = [
    ("Alice Johnson",  "alice@example.com",   "Enterprise"),
    ("Bob Smith",      "bob@example.com",     "SMB"),
    ("Carol White",    "carol@example.com",   "Enterprise"),
    ("David Brown",    "david@example.com",   "Individual"),
    ("Eva Martinez",   "eva@example.com",     "SMB"),
    ("Frank Lee",      "frank@example.com",   "Individual"),
    ("Grace Kim",      "grace@example.com",   "Enterprise"),
    ("Henry Davis",    "henry@example.com",   "SMB"),
    ("Isla Thomas",    "isla@example.com",    "Individual"),
    ("Jack Wilson",    "jack@example.com",    "SMB"),
    ("Karen Moore",    "karen@example.com",   "Enterprise"),
    ("Liam Taylor",    "liam@example.com",    "Individual"),
    ("Mia Anderson",   "mia@example.com",     "SMB"),
    ("Noah Jackson",   "noah@example.com",    "Enterprise"),
    ("Olivia Harris",  "olivia@example.com",  "Individual"),
]

REGIONS   = ["North", "South", "East", "West", "Central"]
STATUSES  = ["Completed", "Completed", "Completed", "Returned", "Pending"]  # weighted

start_date = datetime(2023, 1, 1)
end_date   = datetime(2023, 12, 31)

rows = []
for order_id in range(1001, 2001):
    product_name = random.choice(list(PRODUCTS.keys()))
    product      = PRODUCTS[product_name]
    customer     = random.choice(CUSTOMERS)
    region       = random.choice(REGIONS)
    status       = random.choice(STATUSES)

    quantity     = random.randint(1, 10)
    price_var    = random.uniform(0.90, 1.10)
    unit_price   = round(product["base_price"] * price_var, 2)
    unit_cost    = round(product["base_cost"]  * random.uniform(0.95, 1.05), 2)

    total_amount = round(unit_price * quantity, 2)
    total_cost   = round(unit_cost  * quantity, 2)
    profit       = round(total_amount - total_cost, 2)

    order_date   = start_date + timedelta(days=random.randint(0, 364))

    rows.append({
        "order_id":       order_id,
        "order_date":     order_date.strftime("%Y-%m-%d"),
        "product_name":   product_name,
        "category":       product["category"],
        "customer_name":  customer[0],
        "customer_email": customer[1],
        "customer_type":  customer[2],
        "region":         region,
        "quantity":       quantity,
        "unit_price":     unit_price,
        "unit_cost":      unit_cost,
        "total_amount":   total_amount,
        "total_cost":     total_cost,
        "profit":         profit,
        "status":         status,
    })

df = pd.DataFrame(rows)
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/sales_data.csv", index=False)
print(f"✅ Generated {len(df)} rows → data/raw/sales_data.csv")
print(df.head())
