def lineage_rows():
    """
    Define how important outputs are produced.
    """

    return [
        {
            "claim": "Revenue movement",
            "source": "sales.csv",
            "method": "Equal-window aggregation",
            "type": "deterministic",
        },

        {
            "claim": "Regional contribution",
            "source": "sales.csv",
            "method": (
                "Period-over-period "
                "contribution analysis"
            ),
            "type": "deterministic",
        },

        {
            "claim": "Product contribution",
            "source": "sales.csv",
            "method": (
                "Period-over-period "
                "contribution analysis"
            ),
            "type": "deterministic",
        },

        {
            "claim": "Inventory signal",
            "source": "inventory.csv",
            "method": (
                "Period-over-period comparison"
            ),
            "type": "deterministic",
        },

        {
            "claim": "Customer themes",
            "source": "customer_feedback.csv",
            "method": (
                "Theme extraction + "
                "sentiment heuristic"
            ),
            "type": "unstructured analytics",
        },

        {
            "claim": "Association tests",
            "source": (
                "sales + inventory + "
                "customer_metrics"
            ),
            "method": "Pearson correlation",
            "type": (
                "statistical; not causal"
            ),
        },

        {
            "claim": "Confidence",
            "source": "analytics engine",
            "method": "Weighted evidence score",
            "type": "deterministic",
        },

        {
            "claim": "Recommendation",
            "source": "verified driver pack",
            "method": "Rule-based action engine",
            "type": "deterministic",
        },

        {
            "claim": "Narrative",
            "source": "verified analytics payload",
            "method": "LLM synthesis or fallback",
            "type": "generative AI",
        },
    ]