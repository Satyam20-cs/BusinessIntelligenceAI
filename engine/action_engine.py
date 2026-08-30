def recommend_actions(
    driver_pack,
    confidence,
):
    """
    Generate structured business actions.

    Low confidence:
        validate evidence first.

    Normal confidence:
        generate operational actions based
        on strongest identified contributors.
    """

    if confidence < 0.55:

        return [
            {
                "priority": "P0",
                "driver": "Evidence quality",
                "lever": "Data validation",

                "action": (
                    "Validate missing or contradictory "
                    "source data before taking a major "
                    "corrective action."
                ),

                "owner": "Business Analyst",

                "expected_impact": (
                    "Reduce decision risk"
                ),

                "monitoring": (
                    "Refresh data and rerun "
                    "the investigation."
                ),
            }
        ]

    regions = driver_pack.get(
        "regions"
    )

    products = driver_pack.get(
        "products"
    )

    region = (
        str(
            regions.iloc[0]["region"]
        )
        if regions is not None
        and not regions.empty
        else "priority region"
    )

    product = (
        str(
            products.iloc[0]["product"]
        )
        if products is not None
        and not products.empty
        else "priority product"
    )

    return [
        {
            "priority": "P0",

            "driver": (
                f"{region} revenue decline"
            ),

            "lever": (
                "Regional execution"
            ),

            "action": (
                f"Investigate order loss in "
                f"{region} and assign a regional "
                f"recovery owner."
            ),

            "owner": (
                "Regional Operations Manager"
            ),

            "expected_impact": (
                "Recover a portion of the "
                "observed revenue gap"
            ),

            "monitoring": (
                "Daily revenue and orders "
                "for 7 days"
            ),
        },

        {
            "priority": "P1",

            "driver": (
                f"{product} performance"
            ),

            "lever": (
                "Product availability "
                "and experience"
            ),

            "action": (
                f"Review {product} stock "
                f"availability, customer "
                f"complaints and returns."
            ),

            "owner": (
                "Product + Supply Lead"
            ),

            "expected_impact": (
                "Reduce lost orders and "
                "customer friction"
            ),

            "monitoring": (
                "Stockouts, returns and "
                "complaint rate"
            ),
        },
    ]