from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

rng = np.random.default_rng(42)

dates = pd.date_range("2026-06-01", "2026-08-21", freq="D")
regions = ["North", "South", "East", "West"]
products = ["Product A", "Product B", "Product C", "Product D"]

sales_rows = []
inventory_rows = []
customer_rows = []

for d in dates:
    day_index = (d - dates[0]).days
    current_month = d.month
    is_aug = current_month == 8

    for region in regions:
        for product in products:
            base_orders = 420 + 30 * regions.index(region) + 25 * products.index(product)
            noise = rng.normal(0, 35)

            # Deliberately create the competition demo story in August.
            west_factor = 0.86 if is_aug and region == "West" else 1.0
            product_a_factor = 0.84 if is_aug and product == "Product A" else 1.0
            stockout_factor = 0.92 if is_aug and region == "West" and product == "Product A" else 1.0

            orders = max(20, int((base_orders + noise) * west_factor * product_a_factor * stockout_factor))
            sessions = max(orders + 100, int(orders / 0.035 + rng.normal(0, 100)))
            units = max(orders, int(orders * rng.uniform(1.15, 1.45)))
            price = 2100 + 180 * products.index(product)
            discount = max(0, price * units * rng.uniform(0.04, 0.10))
            revenue = max(0, units * price - discount)
            cost = revenue * rng.uniform(0.52, 0.61)
            marketing = revenue * rng.uniform(0.035, 0.07)

            sales_rows.append({
                "date": d.date().isoformat(),
                "region": region,
                "product": product,
                "orders": orders,
                "sessions": sessions,
                "units_sold": units,
                "unit_price": round(price, 2),
                "discount": round(discount, 2),
                "revenue": round(revenue, 2),
                "product_cost": round(cost, 2),
                "marketing_spend": round(marketing, 2)
            })

            base_stock = 1500
            stock_available = base_stock + rng.normal(0, 120)
            stockouts = max(0, int(rng.normal(3, 2)))

            if is_aug and region == "West":
                stock_available *= 0.82
                stockouts += int(rng.integers(8, 16))
            if is_aug and product == "Product A":
                stock_available *= 0.88
                stockouts += int(rng.integers(3, 8))

            inventory_rows.append({
                "date": d.date().isoformat(),
                "region": region,
                "product": product,
                "stock_available": round(max(0, stock_available), 2),
                "stockouts": stockouts
            })

            complaints = int(max(0, rng.normal(12, 4)))
            returned_units = int(max(0, units * rng.uniform(0.025, 0.055)))

            if is_aug and product == "Product A":
                complaints += int(rng.integers(5, 12))
                returned_units += int(units * 0.025)

            sentiment = round(np.clip(rng.normal(0.72, 0.08) - (0.10 if is_aug and product == "Product A" else 0), 0, 1), 3)

            customer_rows.append({
                "date": d.date().isoformat(),
                "region": region,
                "product": product,
                "complaints": complaints,
                "returned_units": returned_units,
                "sentiment_score": sentiment
            })

pd.DataFrame(sales_rows).to_csv(DATA / "sales.csv", index=False)
pd.DataFrame(inventory_rows).to_csv(DATA / "inventory.csv", index=False)
pd.DataFrame(customer_rows).to_csv(DATA / "customer_metrics.csv", index=False)

print("Created:")
for name in ["sales.csv", "inventory.csv", "customer_metrics.csv"]:
    print(DATA / name)
