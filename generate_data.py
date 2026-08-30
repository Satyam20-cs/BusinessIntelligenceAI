from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

DATA.mkdir(
    parents=True,
    exist_ok=True
)


RNG = np.random.default_rng(42)


REGIONS = [
    "North",
    "South",
    "East",
    "West",
]

PRODUCTS = [
    "Product A",
    "Product B",
    "Product C",
    "Product D",
]


START_DATE = pd.Timestamp("2026-07-01")
END_DATE = pd.Timestamp("2026-08-21")

dates = pd.date_range(
    START_DATE,
    END_DATE,
    freq="D"
)


sales_rows = []
inventory_rows = []
customer_rows = []
feedback_rows = []


REGION_MULTIPLIERS = {
    "North": 1.05,
    "South": 0.95,
    "East": 1.00,
    "West": 1.08,
}


PRODUCT_MULTIPLIERS = {
    "Product A": 1.15,
    "Product B": 1.00,
    "Product C": 0.92,
    "Product D": 0.88,
}


AVERAGE_PRICES = {
    "Product A": 42000,
    "Product B": 36000,
    "Product C": 28000,
    "Product D": 22000,
}


feedback_templates = [
    "Product A was unavailable when I tried to order.",
    "Delivery was late and arrived after the promised date.",
    "The product quality was good but delivery was delayed.",
    "The item was out of stock again.",
    "Checkout was easy and the product arrived quickly.",
    "The price felt expensive compared with alternatives.",
    "The product arrived damaged and I requested a return.",
    "The website checkout process was difficult.",
    "Delivery was fast and the product was excellent.",
    "I had to return the product because it was defective.",
]


for date in dates:

    date = pd.Timestamp(date)

    date_str = date.date().isoformat()

    is_late_period = (
        date >= pd.Timestamp("2026-08-01")
    )

    for region in REGIONS:

        for product in PRODUCTS:

            base_orders = 95

            region_multiplier = (
                REGION_MULTIPLIERS[region]
            )

            product_multiplier = (
                PRODUCT_MULTIPLIERS[product]
            )

            orders_mean = (
                base_orders
                * region_multiplier
                * product_multiplier
            )

            if is_late_period:

                if region == "West":
                    orders_mean *= 0.88

                if product == "Product A":
                    orders_mean *= 0.90

            orders = max(
                1,
                int(
                    RNG.normal(
                        orders_mean,
                        orders_mean * 0.08
                    )
                )
            )

            average_price = (
                AVERAGE_PRICES[product]
            )

            units_sold = max(
                1,
                int(
                    orders
                    * RNG.uniform(
                        1.05,
                        1.30
                    )
                )
            )

            revenue = (
                units_sold
                * average_price
            )

            revenue *= RNG.uniform(
                0.94,
                1.06
            )

            product_cost = (
                revenue
                * RNG.uniform(
                    0.58,
                    0.68
                )
            )

            marketing_spend = (
                revenue
                * RNG.uniform(
                    0.06,
                    0.11
                )
            )

            sessions = max(
                orders + 1,
                int(
                    orders
                    * RNG.uniform(
                        7,
                        10
                    )
                )
            )

            sales_rows.append(
                {
                    "date": date_str,
                    "region": region,
                    "product": product,
                    "revenue": round(
                        revenue,
                        2
                    ),
                    "orders": orders,
                    "sessions": sessions,
                    "units_sold": units_sold,
                    "product_cost": round(
                        product_cost,
                        2
                    ),
                    "marketing_spend": round(
                        marketing_spend,
                        2
                    ),
                }
            )

            stock_available = (
                1500
                + RNG.normal(
                    0,
                    120
                )
            )

            stockouts = max(
                0,
                int(
                    RNG.normal(
                        3,
                        2
                    )
                )
            )

            if (
                is_late_period
                and region == "West"
            ):

                stock_available *= 0.82

                stockouts += int(
                    RNG.integers(
                        8,
                        16
                    )
                )

            if (
                is_late_period
                and product == "Product A"
            ):

                stock_available *= 0.88

                stockouts += int(
                    RNG.integers(
                        3,
                        8
                    )
                )

            inventory_rows.append(
                {
                    "date": date_str,
                    "region": region,
                    "product": product,
                    "stock_available": round(
                        max(
                            0,
                            stock_available
                        ),
                        2
                    ),
                    "stockouts": stockouts,
                }
            )

            complaints = max(
                0,
                int(
                    RNG.normal(
                        12,
                        4
                    )
                )
            )

            returned_units = max(
                0,
                int(
                    units_sold
                    * RNG.uniform(
                        0.025,
                        0.055
                    )
                )
            )

            sentiment = np.clip(
                RNG.normal(
                    0.72,
                    0.08
                ),
                0,
                1
            )

            if (
                is_late_period
                and product == "Product A"
            ):

                complaints += int(
                    RNG.integers(
                        5,
                        12
                    )
                )

                returned_units += int(
                    units_sold
                    * 0.025
                )

                sentiment = np.clip(
                    sentiment - 0.10,
                    0,
                    1
                )

            customer_rows.append(
                {
                    "date": date_str,
                    "region": region,
                    "product": product,
                    "complaints": complaints,
                    "returned_units": returned_units,
                    "sentiment_score": round(
                        float(sentiment),
                        3
                    ),
                }
            )


for _ in range(250):

    random_date = pd.Timestamp(
        RNG.choice(dates)
    )

    feedback_rows.append(
        {
            "date": random_date.date().isoformat(),
            "region": RNG.choice(
                REGIONS
            ),
            "product": RNG.choice(
                PRODUCTS
            ),
            "feedback_text": RNG.choice(
                feedback_templates
            ),
        }
    )


sales_df = pd.DataFrame(
    sales_rows
)

inventory_df = pd.DataFrame(
    inventory_rows
)

customer_df = pd.DataFrame(
    customer_rows
)

feedback_df = pd.DataFrame(
    feedback_rows
)


sales_df.to_csv(
    DATA / "sales.csv",
    index=False
)

inventory_df.to_csv(
    DATA / "inventory.csv",
    index=False
)

customer_df.to_csv(
    DATA / "customer_metrics.csv",
    index=False
)

feedback_df.to_csv(
    DATA / "customer_feedback.csv",
    index=False
)


feedback_log = DATA / "feedback_log.json"

if not feedback_log.exists():

    feedback_log.write_text(
        "[]",
        encoding="utf-8"
    )


print()
print("=" * 60)
print("InsightX demo data generated successfully.")
print("=" * 60)
print()

print(
    f"Date range: "
    f"{START_DATE.date()} → {END_DATE.date()}"
)

print(
    f"Regions: {len(REGIONS)}"
)

print(
    f"Products: {len(PRODUCTS)}"
)

print(
    f"Sales rows: {len(sales_df):,}"
)

print(
    f"Inventory rows: {len(inventory_df):,}"
)

print(
    f"Customer metric rows: {len(customer_df):,}"
)

print(
    f"Feedback rows: {len(feedback_df):,}"
)

print()


for filename in [
    "sales.csv",
    "inventory.csv",
    "customer_metrics.csv",
    "customer_feedback.csv",
]:

    path = DATA / filename

    print(
        f"{filename}: "
        f"{path.stat().st_size:,} bytes"
    )


print()
print("=" * 60)