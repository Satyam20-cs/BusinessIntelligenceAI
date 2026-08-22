import pandas as pd
import numpy as np

def revenue_drivers(sales: pd.DataFrame, inventory: pd.DataFrame, customer: pd.DataFrame):
    # Region contribution to revenue decline
    s = sales.copy()
    s["month"] = s["date"].dt.to_period("M")
    months = sorted(s["month"].unique())
    prev_m, curr_m = months[-2], months[-1]

    reg = s.groupby(["region", "month"])["revenue"].sum().unstack(fill_value=0)
    reg["delta"] = reg[curr_m] - reg[prev_m]
    negative = reg[reg["delta"] < 0].copy()
    total_decline = abs(negative["delta"].sum())
    negative["contribution_pct"] = np.where(
        total_decline > 0, abs(negative["delta"]) / total_decline * 100, 0
    )
    region_rows = [
        {"driver": f"{idx} region", "change": float(row["delta"]),
         "contribution_pct": float(row["contribution_pct"])}
        for idx, row in negative.sort_values("contribution_pct", ascending=False).head(5).iterrows()
    ]

    # Product contribution
    prod = s.groupby(["product", "month"])["revenue"].sum().unstack(fill_value=0)
    prod["delta"] = prod[curr_m] - prod[prev_m]
    pneg = prod[prod["delta"] < 0].copy()
    ptotal = abs(pneg["delta"].sum())
    pneg["contribution_pct"] = np.where(ptotal > 0, abs(pneg["delta"]) / ptotal * 100, 0)
    product_rows = [
        {"driver": f"{idx}", "change": float(row["delta"]),
         "contribution_pct": float(row["contribution_pct"])}
        for idx, row in pneg.sort_values("contribution_pct", ascending=False).head(5).iterrows()
    ]

    # Inventory signal
    inv = inventory.copy()
    inv["month"] = inv["date"].dt.to_period("M")
    inv_month = inv.groupby("month").agg(stockouts=("stockouts", "sum"), stock_available=("stock_available", "mean"))
    inv_signal = {}
    if prev_m in inv_month.index and curr_m in inv_month.index:
        inv_signal = {
            "driver": "Inventory stockouts",
            "previous": float(inv_month.loc[prev_m, "stockouts"]),
            "current": float(inv_month.loc[curr_m, "stockouts"]),
            "change_pct": float((inv_month.loc[curr_m, "stockouts"] - inv_month.loc[prev_m, "stockouts"]) /
                                max(abs(inv_month.loc[prev_m, "stockouts"]), 1) * 100)
        }

    # Customer complaints signal
    c = customer.copy()
    c["month"] = c["date"].dt.to_period("M")
    cm = c.groupby("month").agg(complaints=("complaints", "sum"), returned_units=("returned_units", "sum"))
    complaint_signal = {}
    if prev_m in cm.index and curr_m in cm.index:
        complaint_signal = {
            "driver": "Customer complaints",
            "previous": float(cm.loc[prev_m, "complaints"]),
            "current": float(cm.loc[curr_m, "complaints"]),
            "change_pct": float((cm.loc[curr_m, "complaints"] - cm.loc[prev_m, "complaints"]) /
                                max(abs(cm.loc[prev_m, "complaints"]), 1) * 100)
        }

    return {
        "region_drivers": region_rows,
        "product_drivers": product_rows,
        "inventory_signal": inv_signal,
        "complaint_signal": complaint_signal,
    }

def build_driver_tree(drivers):
    region = drivers["region_drivers"][0] if drivers["region_drivers"] else None
    product = drivers["product_drivers"][0] if drivers["product_drivers"] else None
    tree = [
        {"level": 0, "label": "Revenue ↓", "parent": None},
    ]
    if region:
        tree.append({"level": 1, "label": f"{region['driver']} ({region['contribution_pct']:.0f}% contribution)", "parent": "Revenue ↓"})
    if product:
        tree.append({"level": 1, "label": f"{product['driver']} ({product['contribution_pct']:.0f}% contribution)", "parent": "Revenue ↓"})
    if drivers["inventory_signal"]:
        tree.append({"level": 1, "label": "Inventory stockouts ↑", "parent": "Revenue ↓"})
    if drivers["complaint_signal"]:
        tree.append({"level": 1, "label": "Customer complaints ↑", "parent": "Revenue ↓"})
    return tree
