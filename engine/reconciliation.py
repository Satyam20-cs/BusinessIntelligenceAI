import pandas as pd


def _source_row(name, df):

    if df is None:
        return {
            "source": name,
            "rows": 0,
            "min_date": "n/a",
            "max_date": "n/a",
            "missing_pct": 100.0,
            "grain": "unavailable",
        }

    if df.empty:
        return {
            "source": name,
            "rows": 0,
            "min_date": "n/a",
            "max_date": "n/a",
            "missing_pct": 100.0,
            "grain": "empty",
        }

    min_date = "n/a"
    max_date = "n/a"

    if "date" in df.columns:

        dates = pd.to_datetime(
            df["date"],
            errors="coerce"
        ).dropna()

        if not dates.empty:

            min_date = (
                dates.min()
                .date()
                .isoformat()
            )

            max_date = (
                dates.max()
                .date()
                .isoformat()
            )

    missing_pct = round(
        float(
            df.isna()
            .mean()
            .mean()
            * 100
        ),
        2
    )

    if {
        "date",
        "region",
        "product",
    }.issubset(df.columns):

        grain = "date × region × product"

    elif "date" in df.columns:

        grain = "date"

    else:

        grain = "text/event"

    return {
        "source": name,
        "rows": len(df),
        "min_date": min_date,
        "max_date": max_date,
        "missing_pct": missing_pct,
        "grain": grain,
    }


def reconcile_sources(
    sales,
    inventory,
    customer,
    feedback,
):
    """
    Validate basic source coverage and
    common business dimensions.
    """

    sources = {
        "sales": sales,
        "inventory": inventory,
        "customer_metrics": customer,
        "customer_feedback": feedback,
    }

    rows = [
        _source_row(
            name,
            df
        )
        for name, df in sources.items()
    ]

    common = set()

    inventory_keys = set()

    customer_keys = set()

    if {
        "region",
        "product",
    }.issubset(sales.columns):

        common = set(
            sales[
                [
                    "region",
                    "product",
                ]
            ]
            .drop_duplicates()
            .itertuples(
                index=False,
                name=None
            )
        )

    if {
        "region",
        "product",
    }.issubset(inventory.columns):

        inventory_keys = set(
            inventory[
                [
                    "region",
                    "product",
                ]
            ]
            .drop_duplicates()
            .itertuples(
                index=False,
                name=None
            )
        )

    if {
        "region",
        "product",
    }.issubset(customer.columns):

        customer_keys = set(
            customer[
                [
                    "region",
                    "product",
                ]
            ]
            .drop_duplicates()
            .itertuples(
                index=False,
                name=None
            )
        )

    denominator = max(
        len(common),
        1
    )

    sales_inventory_overlap = round(
        len(common & inventory_keys)
        / denominator
        * 100,
        1
    )

    sales_customer_overlap = round(
        len(common & customer_keys)
        / denominator
        * 100,
        1
    )

    return {
        "sources": pd.DataFrame(rows),

        "dimension_overlap": {
            "sales_inventory_pct":
                sales_inventory_overlap,

            "sales_customer_pct":
                sales_customer_overlap,
        },
    }


def source_completeness(df):
    """
    Return a 0–1 completeness score.
    """

    if df is None or df.empty:
        return 0.0

    missing = (
        df.isna()
        .mean()
        .mean()
    )

    return max(
        0.0,
        1.0 - float(missing)
    )