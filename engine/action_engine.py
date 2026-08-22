def recommend_action(drivers, confidence):
    region = drivers["region_drivers"][0]["driver"] if drivers["region_drivers"] else "priority region"
    product = drivers["product_drivers"][0]["driver"] if drivers["product_drivers"] else "priority product"

    if confidence < 0.55:
        return {
            "driver": "Insufficiently supported driver",
            "lever": "Data validation",
            "action": "Validate missing or contradictory data before taking a major corrective action.",
            "expected_impact": "Avoid premature intervention",
            "owner": "Business Analyst",
            "confidence": confidence,
            "monitoring": "Re-run the investigation after data refresh."
        }

    return {
        "driver": f"{region} + {product} performance",
        "lever": "Inventory and regional sales execution",
        "action": f"Prioritize {product} availability in the {region.replace(' region','')} and investigate order-loss reasons.",
        "expected_impact": "Potential recovery of 2–4% of monthly revenue if the identified drivers return toward baseline.",
        "owner": "Regional Operations Manager",
        "confidence": confidence,
        "monitoring": "Track stockouts, orders and regional revenue daily for 7 days."
    }
