def get_lineage():
    return [
        {"output": "Revenue", "source": "sales.csv", "method": "Deterministic aggregation", "freshness": "10 min ago"},
        {"output": "Region contribution", "source": "sales.csv", "method": "Period-over-period contribution analysis", "freshness": "10 min ago"},
        {"output": "Inventory signal", "source": "inventory.csv", "method": "Period-over-period comparison", "freshness": "2 hours ago"},
        {"output": "Customer complaint signal", "source": "customer_metrics.csv", "method": "Period-over-period comparison", "freshness": "35 min ago"},
        {"output": "Confidence", "source": "analytics engine", "method": "Weighted evidence score", "freshness": "Live"},
        {"output": "Narrative", "source": "verified analytics payload", "method": "LLM or deterministic fallback", "freshness": "Live"},
    ]

def evidence_summary():
    return {
        "data_completeness": 0.95,
        "evidence_strength": 0.88,
        "history_strength": 0.90,
        "consistency": 0.92,
    }
