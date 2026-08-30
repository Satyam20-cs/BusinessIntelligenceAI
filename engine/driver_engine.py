import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def period_split(df, days=21):
    """
    Split a dataset into previous/current
    equal-length windows.
    """

    d = df.copy()

    d["date"] = pd.to_datetime(
        d["date"],
        errors="coerce"
    )

    latest = d["date"].max()

    current_start = (
        latest
        - pd.Timedelta(days=days - 1)
    )

    previous_end = (
        current_start
        - pd.Timedelta(days=1)
    )

    previous_start = (
        previous_end
        - pd.Timedelta(days=days - 1)
    )

    previous = d[
        (d["date"] >= previous_start)
        &
        (d["date"] <= previous_end)
    ]

    current = d[
        (d["date"] >= current_start)
        &
        (d["date"] <= latest)
    ]

    return previous, current


def contribution_table(
    df,
    dimension,
    metric="revenue",
    days=21,
):
    """
    Calculate how much each dimension contributes
    to the total negative movement.
    """

    previous, current = period_split(
        df,
        days
    )

    previous_values = (
        previous
        .groupby(dimension)[metric]
        .sum()
        .rename("previous")
    )

    current_values = (
        current
        .groupby(dimension)[metric]
        .sum()
        .rename("current")
    )

    out = pd.concat(
        [
            previous_values,
            current_values,
        ],
        axis=1
    ).fillna(0)

    out["delta"] = (
        out["current"]
        - out["previous"]
    )

    negative = out[
        out["delta"] < 0
    ]

    total_negative = abs(
        negative["delta"].sum()
    )

    out["contribution_pct"] = np.where(
        out["delta"] < 0,

        abs(out["delta"])
        / max(total_negative, 1)
        * 100,

        0,
    )

    return (
        out
        .sort_values(
            "contribution_pct",
            ascending=False
        )
    )


def correlation_signal(
    sales,
    inventory,
    customer,
    days=42,
):
    """
    Test statistical associations between
    operational/customer signals and revenue/orders.

    Important:
    Correlation is treated as association,
    NOT proof of causality.
    """

    sales_daily = (
        sales
        .groupby("date")
        .agg(
            revenue=("revenue", "sum"),
            orders=("orders", "sum"),
        )
    )

    inventory_daily = (
        inventory
        .groupby("date")
        .agg(
            stockouts=("stockouts", "sum")
        )
    )

    customer_daily = (
        customer
        .groupby("date")
        .agg(
            complaints=("complaints", "sum")
        )
    )

    merged = (
        sales_daily
        .join(
            inventory_daily,
            how="inner"
        )
        .join(
            customer_daily,
            how="inner"
        )
        .tail(days)
        .dropna()
    )

    results = []

    relationships = [
        (
            "stockouts",
            "revenue",
            "Stockouts ↔ Revenue",
        ),
        (
            "complaints",
            "revenue",
            "Complaints ↔ Revenue",
        ),
        (
            "stockouts",
            "orders",
            "Stockouts ↔ Orders",
        ),
    ]

    for x, y, relationship in relationships:

        if len(merged) < 8:
            continue

        if (
            merged[x].nunique() <= 1
            or
            merged[y].nunique() <= 1
        ):
            continue

        try:

            r, p = pearsonr(
                merged[x],
                merged[y]
            )

            results.append(
                {
                    "relationship": relationship,
                    "pearson_r": round(
                        float(r),
                        3
                    ),
                    "p_value": round(
                        float(p),
                        4
                    ),
                    "interpretation":
                        "Association only; "
                        "not proof of causality",
                }
            )

        except Exception:
            continue

    return pd.DataFrame(results)


def build_revenue_driver_pack(
    sales,
    inventory,
    customer,
    days=21,
):
    """
    Build the complete evidence pack
    for a revenue investigation.
    """

    regions = (
        contribution_table(
            sales,
            "region",
            "revenue",
            days
        )
        .head(5)
        .reset_index()
    )

    products = (
        contribution_table(
            sales,
            "product",
            "revenue",
            days
        )
        .head(5)
        .reset_index()
    )

    inventory_previous, inventory_current = (
        period_split(
            inventory,
            days
        )
    )

    previous_stockouts = (
        inventory_previous["stockouts"]
        .sum()
    )

    current_stockouts = (
        inventory_current["stockouts"]
        .sum()
    )

    stockout_change = (
        (
            current_stockouts
            - previous_stockouts
        )
        /
        max(
            abs(previous_stockouts),
            1
        )
        * 100
    )

    customer_previous, customer_current = (
        period_split(
            customer,
            days
        )
    )

    previous_complaints = (
        customer_previous["complaints"]
        .sum()
    )

    current_complaints = (
        customer_current["complaints"]
        .sum()
    )

    complaint_change = (
        (
            current_complaints
            - previous_complaints
        )
        /
        max(
            abs(previous_complaints),
            1
        )
        * 100
    )

    correlations = correlation_signal(
        sales,
        inventory,
        customer,
        days=42
    )

    return {
        "regions": regions,
        "products": products,

        "inventory": {
            "previous": float(
                previous_stockouts
            ),
            "current": float(
                current_stockouts
            ),
            "change_pct": float(
                stockout_change
            ),
        },

        "complaints": {
            "previous": float(
                previous_complaints
            ),
            "current": float(
                current_complaints
            ),
            "change_pct": float(
                complaint_change
            ),
        },

        "correlations": correlations,
    }


def build_driver_tree(driver_pack):
    """
    Convert the driver pack into a simple
    Revenue → contributing signals structure.
    """

    tree = [
        {
            "level": 0,
            "label": "Revenue movement",
            "parent": None,
        }
    ]

    regions = driver_pack.get(
        "regions",
        pd.DataFrame()
    )

    products = driver_pack.get(
        "products",
        pd.DataFrame()
    )

    if not regions.empty:

        row = regions.iloc[0]

        tree.append(
            {
                "level": 1,
                "label": (
                    f"{row['region']} region "
                    f"({row['contribution_pct']:.0f}% "
                    f"of negative movement)"
                ),
                "parent": "Revenue movement",
            }
        )

    if not products.empty:

        row = products.iloc[0]

        tree.append(
            {
                "level": 1,
                "label": (
                    f"{row['product']} "
                    f"({row['contribution_pct']:.0f}% "
                    f"of negative movement)"
                ),
                "parent": "Revenue movement",
            }
        )

    inventory = driver_pack.get(
        "inventory"
    )

    if inventory:

        if inventory["change_pct"] > 0:

            tree.append(
                {
                    "level": 1,
                    "label": "Inventory stockouts increased",
                    "parent": "Revenue movement",
                }
            )

    complaints = driver_pack.get(
        "complaints"
    )

    if complaints:

        if complaints["change_pct"] > 0:

            tree.append(
                {
                    "level": 1,
                    "label": "Customer complaints increased",
                    "parent": "Revenue movement",
                }
            )

    return tree