def recommend_actions(driver_pack, confidence):
    if confidence < 0.55:
        return [{
            "priority": "P0",
            "driver": "Evidence quality",
            "lever": "Data validation",
            "action": "Validate missing/contradictory source data before taking a major corrective action.",
            "owner": "Business Analyst",
            "expected_impact": "Reduce decision risk",
            "monitoring": "Refresh data and rerun the investigation."
        }]

    region = (
        str(driver_pack["regions"].iloc[0]["region"])
        if len(driver_pack["regions"]) else "priority region"
    )
    product = (
        str(driver_pack["products"].iloc[0]["product"])
        if len(driver_pack["products"]) else "priority product"
    )

    return [
        {
            "priority": "P0",
            "driver": f"{region} revenue decline",
            "lever": "Regional execution",
            "action": f"Investigate order loss in {region} and assign a regional recovery owner.",
            "owner": "Regional Operations Manager",
            "expected_impact": "Recover a portion of the observed revenue gap",
            "monitoring": "Daily revenue and orders for 7 days"
        },
        {
            "priority": "P1",
            "driver": f"{product} performance",
            "lever": "Product availability and experience",
            "action": f"Review {product} stock availability, customer complaints and returns.",
            "owner": "Product + Supply Lead",
            "expected_impact": "Reduce lost orders and customer friction",
            "monitoring": "Stockouts, returns and complaint rate"
        }
    ]
