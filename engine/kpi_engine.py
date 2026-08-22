import pandas as pd
import numpy as np

def _safe_pct_change(current, previous):
    if previous == 0:
        return 0.0
    return (current - previous) / abs(previous) * 100.0

def calculate_kpis(sales, inventory, customer):
    revenue = sales["revenue"].sum()
    profit = (sales["revenue"] - sales["product_cost"] - sales["marketing_spend"]).sum()
    orders = sales["orders"].sum()
    sessions = sales["sessions"].sum()
    conversion = orders / sessions * 100 if sessions else 0
    return_units = customer["returned_units"].sum()
    sold_units = sales["units_sold"].sum()
    return_rate = return_units / sold_units * 100 if sold_units else 0

    return {
        "Revenue": float(revenue),
        "Profit": float(profit),
        "Orders": float(orders),
        "Conversion Rate": float(conversion),
        "Return Rate": float(return_rate),
    }

def monthly_kpis(sales, customer):
    s = sales.copy()
    s["month"] = s["date"].dt.to_period("M").astype(str)
    c = customer.copy()
    c["month"] = c["date"].dt.to_period("M").astype(str)

    out = s.groupby("month").agg(
        revenue=("revenue", "sum"),
        profit=("revenue", "sum"),
        orders=("orders", "sum"),
        sessions=("sessions", "sum"),
        units_sold=("units_sold", "sum"),
        product_cost=("product_cost", "sum"),
        marketing_spend=("marketing_spend", "sum")
    ).reset_index()

    out["profit"] = out["revenue"] - out["product_cost"] - out["marketing_spend"]

    c2 = c.groupby("month").agg(returned_units=("returned_units", "sum")).reset_index()
    out = out.merge(c2, on="month", how="left")
    out["conversion_rate"] = np.where(out["sessions"] > 0, out["orders"] / out["sessions"] * 100, 0)
    out["return_rate"] = np.where(out["units_sold"] > 0, out["returned_units"] / out["units_sold"] * 100, 0)
    return out

def compare_periods(monthly_df):
    if len(monthly_df) < 2:
        raise ValueError("Need at least two months of data.")
    prev = monthly_df.iloc[-2]
    curr = monthly_df.iloc[-1]
    metrics = {
        "Revenue": (curr["revenue"], prev["revenue"]),
        "Profit": (curr["profit"], prev["profit"]),
        "Orders": (curr["orders"], prev["orders"]),
        "Conversion Rate": (curr["conversion_rate"], prev["conversion_rate"]),
        "Return Rate": (curr["return_rate"], prev["return_rate"]),
    }
    result = {}
    for k, (current, previous) in metrics.items():
        result[k] = {
            "current": float(current),
            "previous": float(previous),
            "change_pct": _safe_pct_change(current, previous)
        }
    return result
