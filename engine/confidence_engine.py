def calculate_confidence(data_completeness=0.95, evidence_strength=0.88,
                         history_strength=0.90, consistency=0.92):
    score = (
        0.30 * data_completeness +
        0.30 * evidence_strength +
        0.20 * history_strength +
        0.20 * consistency
    )
    return round(max(0.0, min(1.0, score)), 2)

def label_confidence(score):
    if score >= 0.80:
        return "HIGH"
    if score >= 0.55:
        return "MEDIUM"
    return "LOW"

def scenario_confidence(scenario):
    return {
        "normal": 0.84,
        "low_confidence": 0.38,
        "sparse_history": 0.42
    }.get(scenario, 0.70)
