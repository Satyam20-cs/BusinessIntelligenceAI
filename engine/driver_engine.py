import numpy as np
import pandas as pd
from scipy.stats import pearsonr

def period_split(df, days=21):
    d = df.copy()
    latest = d["date"].max()
    current_start = latest - pd.Timedelta(days=days - 1)
    previous_end = current_start - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=days - 1)

    prev = d[(d["date"] >= previous_start) & (d["date"] <= previous_end)]
    curr = d[(d["date"] >= current_start) & (d["date"] <= latest)]
    return prev, curr

def contribution_table(df, dimension, metric="revenue", days=21):
    prev, curr = period_split(df, days)
    a = prev.groupby(dimension)[metric].sum().rename("previous")
    b = curr.groupby(dimension)[metric].sum().rename("current")
    out = pd.concat([a, b], axis=1).fillna(0)
    out["delta"] = out["current"] - out["previous"]

    total_negative = abs(out.loc[out["delta"] < 0, "delta"].sum())
    out["contribution_pct"] = np.where(
        out["delta"] < 0,
        abs(out["delta"]) / max(total_negative, 1) * 100,
        0
    )
    return out.sort_values("contribution_pct", ascending=False)

def correlation_signal(sales, inventory, customer, days=42):
    # Daily regional signals; correlation is evidence of association, not causality.
    s = sales.groupby("date").agg(
        revenue=("revenue", "sum"),
        orders=("orders", "sum")
    )
    i = inventory.groupby("date").agg(stockouts=("stockouts", "sum"))
    c = customer.groupby("date").agg(complaints=("complaints", "sum"))

    merged = s.join(i, how="inner").join(c, how="inner").tail(days).dropna()
    result = []

    for x, y, label in [
        ("stockouts", "revenue", "stockouts ↔ revenue"),
        ("complaints", "revenue", "complaints ↔ revenue"),
        ("stockouts", "orders", "stockouts ↔ orders")
    ]:
        if len(merged) >= 8 and merged[x].nunique() > 1 and merged[y].nunique() > 1:
            r, p = pearsonr(merged[x], merged[y])
            result.append({
                "relationship": label,
                "pearson_r": round(float(r), 3),
                "p_value": round(float(p), 4),
                "interpretation": "association only; not proof of causality"
            })
    return pd.DataFrame(result)

def build_revenue_driver_pack(sales, inventory, customer, days=21):
    region = contribution_table(sales, "region", "revenue", days).head(5).reset_index()
    product = contribution_table(sales, "product", "revenue", days).head(5).reset_index()

    inv_prev, inv_curr = period_split(inventory, days)
    stockouts_prev = inv_prev["stockouts"].sum()
    stockouts_curr = inv_curr["stockouts"].sum()
    stockout_change = ((stockouts_curr - stockouts_prev) /
                       max(abs(stockouts_prev), 1)) * 100

    cust_prev, cust_curr = period_split(customer, days)
    complaints_prev = cust_prev["complaints"].sum()
    complaints_curr = cust_curr["complaints"].sum()
    complaint_change = ((complaints_curr - complaints_prev) /
                        max(abs(complaints_prev), 1)) * 100

    return {
        "regions": region,
        "products": product,
        "inventory": {
            "previous": float(stockouts_prev),
            "current": float(stockouts_curr),
            "change_pct": float(stockout_change)
        },
        "complaints": {
            "previous": float(complaints_prev),
            "current": float(complaints_curr),
            "change_pct": float(complaint_change)
        },
        "correlations": correlation_signal(sales, inventory, customer, days=42)
    }
