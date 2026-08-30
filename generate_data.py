from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

rng = np.random.default_rng(7)

# 63 days gives three equal 21-day windows.
dates = pd.date_range("2026-06-20", "2026-08-21", freq="D")
regions = ["North", "South", "East", "West"]
products = ["Product A", "Product B", "Product C", "Product D"]

sales = []
inventory = []
customer = []
feedback = []

feedback_templates = [
    "Delivery was fast and the product was good.",
    "Product was out of stock when I tried to buy it.",
    "The price felt expensive compared with alternatives.",
    "Checkout was easy and payment worked well.",
    "Delivery was late and the packaging was damaged.",
    "The product quality was poor and I want a return.",
    "Very happy with the purchase and fast delivery."
]

for d in dates:
    is_current = d >= pd.Timestamp("2026-08-01")
    for region in regions:
        for product in products:
            base = 420 + 35 * regions.index(region) + 25 * products.index(product)
            orders = max(30, int(base + rng.normal(0, 28)))

            # Controlled business event in the latest 21-day window.
            if is_current and region == "West":
                orders = int(orders * 0.84)
            if is_current and product == "Product A":
                orders = int(orders * 0.86)
            if is_current and region == "West" and product == "Product A":
                orders = int(orders * 0.92)

            sessions = max(orders + 200, int(orders / 0.035 + rng.normal(0, 90)))
            units = max(orders, int(orders * rng.uniform(1.15, 1.45)))
            price = 2100 + products.index(product) * 180
            discount = price * units * rng.uniform(0.04, 0.09)
            revenue = max(0, units * price - discount)
            cost = revenue * rng.uniform(0.52, 0.61)
            marketing = revenue * rng.uniform(0.035, 0.07)

            sales.append([
                d.date().isoformat(), region, product, orders, sessions, units,
                price, discount, revenue, cost, marketing
            ])

            stock = max(0, 1500 + rng.normal(0, 120))
            stockouts = max(0, int(rng.normal(3, 2)))

            if is_current and region == "West":
                stock *= 0.80
                stockouts += int(rng.integers(8, 15))
            if is_current and product == "Product A":
                stock *= 0.88
                stockouts += int(rng.integers(2, 7))

            inventory.append([
                d.date().isoformat(), region, product, stock, stockouts
            ])

            complaints = max(0, int(rng.normal(12, 4)))
            returned = max(0, int(units * rng.uniform(0.025, 0.05)))

            if is_current and product == "Product A":
                complaints += int(rng.integers(5, 11))
                returned += int(units * 0.02)

            customer.append([
                d.date().isoformat(), region, product, complaints, returned
            ])

            # A small unstructured source with business text.
            n_feedback = int(rng.integers(1, 4))
            for _ in range(n_feedback):
                if is_current and region == "West" and product == "Product A":
                    text = rng.choice([
                        "Product was out of stock when I tried to buy it.",
                        "Delivery was late and the packaging was damaged.",
                        "The product quality was poor and I want a return."
                    ])
                else:
                    text = rng.choice(feedback_templates)
                feedback.append([
                    d.date().isoformat(), region, product, text
                ])

pd.DataFrame(sales, columns=[
    "date","region","product","orders","sessions","units_sold",
    "unit_price","discount","revenue","product_cost","marketing_spend"
]).to_csv(DATA / "sales.csv", index=False)

pd.DataFrame(inventory, columns=[
    "date","region","product","stock_available","stockouts"
]).to_csv(DATA / "inventory.csv", index=False)

pd.DataFrame(customer, columns=[
    "date","region","product","complaints","returned_units"
]).to_csv(DATA / "customer_metrics.csv", index=False)

pd.DataFrame(feedback, columns=[
    "date","region","product","feedback_text"
]).to_csv(DATA / "customer_feedback.csv", index=False)

(DATA / "feedback_log.json").write_text("[]", encoding="utf-8")

print("Generated 4 data sources in", DATA)
