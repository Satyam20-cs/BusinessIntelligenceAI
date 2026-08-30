import numpy as np
import pandas as pd


def safe_pct_change(current, previous):
    """
    Calculate percentage change safely.
    """

    if previous == 0:
        return 0.0

    return (
        (current - previous)
        / abs(previous)
        * 100.0
    )


def add_period(df, days=21):
    """
    Assign observations into two equal-length periods:

    previous = previous N days
    current  = latest N days

    This avoids partial-month comparison bias.
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

    d["period"] = np.select(
        [
            (
                (d["date"] >= previous_start)
                &
                (d["date"] <= previous_end)
            ),

            (
                (d["date"] >= current_start)
                &
                (d["date"] <= latest)
            ),
        ],
        [
            "previous",
            "current",
        ],
        default="outside",
    )

    return (
        d,
        previous_start,
        previous_end,
        current_start,
        latest,
    )


def calculate_kpis(
    sales,
    customer,
    days=21,
):
    """
    Calculate core business KPIs for
    previous and current equal-length periods.
    """

    sales_periods, *_ = add_period(
        sales,
        days
    )

    customer_periods, *_ = add_period(
        customer,
        days
    )

    rows = []

    for period in [
        "previous",
        "current",
    ]:

        sp = sales_periods[
            sales_periods["period"] == period
        ]

        cp = customer_periods[
            customer_periods["period"] == period
        ]

        revenue = sp["revenue"].sum()

        profit = (
            sp["revenue"]
            - sp["product_cost"]
            - sp["marketing_spend"]
        ).sum()

        orders = sp["orders"].sum()

        sessions = sp["sessions"].sum()

        units = sp["units_sold"].sum()

        returned = cp["returned_units"].sum()

        conversion_rate = (
            orders / sessions * 100
            if sessions
            else 0
        )

        return_rate = (
            returned / units * 100
            if units
            else 0
        )

        rows.append(
            {
                "period": period,
                "Revenue": float(revenue),
                "Profit": float(profit),
                "Orders": float(orders),
                "Conversion Rate": float(
                    conversion_rate
                ),
                "Return Rate": float(
                    return_rate
                ),
            }
        )

    return pd.DataFrame(rows)


def compare_kpis(kpi_df):
    """
    Convert the previous/current KPI table
    into an easy comparison dictionary.
    """

    previous = kpi_df[
        kpi_df["period"] == "previous"
    ].iloc[0]

    current = kpi_df[
        kpi_df["period"] == "current"
    ].iloc[0]

    result = {}

    metrics = [
        "Revenue",
        "Profit",
        "Orders",
        "Conversion Rate",
        "Return Rate",
    ]

    for metric in metrics:

        current_value = float(
            current[metric]
        )

        previous_value = float(
            previous[metric]
        )

        result[metric] = {
            "current": current_value,
            "previous": previous_value,
            "change_pct": safe_pct_change(
                current_value,
                previous_value
            ),
        }

    return result


def daily_revenue(sales):
    """
    Aggregate revenue by date.
    """

    return (
        sales
        .groupby(
            "date",
            as_index=False
        )["revenue"]
        .sum()
        .sort_values("date")
    )