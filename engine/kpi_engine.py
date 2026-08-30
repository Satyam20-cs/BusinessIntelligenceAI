import pandas as pd
import numpy as np

def safe_pct_change(current, previous):
    if previous == 0:
        return 0.0
    return (current - previous) / abs(previous) * 100.0

def add_period(df, days=21):
    """Use equal-length comparison windows to avoid partial-month bias."""
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    latest = d["date"].max()
    current_start = latest - pd.Timedelta(days=days - 1)
    previous_end = current_start - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=days - 1)

    d["period"] = np.select(
        [
            (d["date"] >= previous_start) & (d["date"] <= previous_end),
            (d["date"] >= current_start) & (d["date"] <= latest)
        ],
        ["previous", "current"],
        default="outside"
    )
    return d, previous_start, previous_end, current_start, latest

def calculate_kpis(sales, customer, days=21):
    s, *_ = add_period(sales, days)
    c, *_ = add_period(customer, days)

    rows = []
    for period in ["previous", "current"]:
        sp = s[s["period"] == period]
        cp = c[c["period"] == period]

        revenue = sp["revenue"].sum()
        profit = (sp["revenue"] - sp["product_cost"] - sp["marketing_spend"]).sum()
        orders = sp["orders"].sum()
        sessions = sp["sessions"].sum()
        units = sp["units_sold"].sum()
        returned = cp["returned_units"].sum()

        rows.append({
            "period": period,
            "Revenue": revenue,
            "Profit": profit,
            "Orders": orders,
            "Conversion Rate": orders / sessions * 100 if sessions else 0,
            "Return Rate": returned / units * 100 if units else 0
        })
    return pd.DataFrame(rows)

def compare_kpis(kpi_df):
    prev = kpi_df[kpi_df["period"] == "previous"].iloc[0]
    curr = kpi_df[kpi_df["period"] == "current"].iloc[0]
    result = {}
    for kpi in ["Revenue", "Profit", "Orders", "Conversion Rate", "Return Rate"]:
        result[kpi] = {
            "current": float(curr[kpi]),
            "previous": float(prev[kpi]),
            "change_pct": safe_pct_change(curr[kpi], prev[kpi])
        }
    return result

def daily_revenue(sales):
    return sales.groupby("date", as_index=False)["revenue"].sum()
