import pandas as pd

def reconcile_sources(sales, inventory, customer, feedback):
    sources = {
        "sales": sales,
        "inventory": inventory,
        "customer_metrics": customer,
        "customer_feedback": feedback
    }

    rows = []
    for name, df in sources.items():
        rows.append({
            "source": name,
            "rows": len(df),
            "min_date": df["date"].min().date().isoformat() if "date" in df.columns and len(df) else "n/a",
            "max_date": df["date"].max().date().isoformat() if "date" in df.columns and len(df) else "n/a",
            "missing_pct": round(float(df.isna().mean().mean() * 100), 2),
            "grain": "date × region × product"
        })

    # Check common dimensions.
    common = set(sales[["region", "product"]].itertuples(index=False, name=None))
    inv = set(inventory[["region", "product"]].itertuples(index=False, name=None))
    cust = set(customer[["region", "product"]].itertuples(index=False, name=None))

    return {
        "sources": pd.DataFrame(rows),
        "dimension_overlap": {
            "sales_inventory_pct": round(len(common & inv) / max(len(common), 1) * 100, 1),
            "sales_customer_pct": round(len(common & cust) / max(len(common), 1) * 100, 1)
        }
    }

def source_completeness(df):
    if df.empty:
        return 0.0
    missing = df.isna().mean().mean()
    return max(0.0, 1.0 - float(missing))
