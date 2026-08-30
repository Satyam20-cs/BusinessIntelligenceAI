def lineage_rows():
    return [
        {
            "claim": "Revenue movement",
            "source": "sales.csv",
            "method": "Equal-window aggregation",
            "type": "deterministic"
        },
        {
            "claim": "Regional contribution",
            "source": "sales.csv",
            "method": "Period-over-period contribution analysis",
            "type": "deterministic"
        },
        {
            "claim": "Inventory signal",
            "source": "inventory.csv",
            "method": "Period-over-period comparison",
            "type": "deterministic"
        },
        {
            "claim": "Customer themes",
            "source": "customer_feedback.csv",
            "method": "Theme extraction + sentiment heuristic",
            "type": "unstructured analytics"
        },
        {
            "claim": "Association tests",
            "source": "sales + inventory + customer_metrics",
            "method": "Pearson correlation",
            "type": "statistical; not causal"
        },
        {
            "claim": "Narrative",
            "source": "verified analytics payload",
            "method": "LLM synthesis",
            "type": "generative AI"
        }
    ]
