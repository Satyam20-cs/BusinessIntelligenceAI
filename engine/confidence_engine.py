def confidence_score(
    data_completeness,
    driver_strength,
    history_strength,
    source_agreement,
    unstructured_support
):
    score = (
        0.25 * data_completeness +
        0.30 * driver_strength +
        0.15 * history_strength +
        0.20 * source_agreement +
        0.10 * unstructured_support
    )
    return round(max(0.0, min(1.0, score)), 2)

def label(score):
    if score >= 0.80:
        return "HIGH"
    if score >= 0.55:
        return "MEDIUM"
    return "LOW"

def reason(score, missing_source=False, sparse_history=False):
    reasons = []
    if missing_source:
        reasons.append("a required source is incomplete")
    if sparse_history:
        reasons.append("historical baseline is too short")
    if score < 0.55 and not reasons:
        reasons.append("evidence is weak or conflicting")
    return "; ".join(reasons) if reasons else "multiple independent signals agree"
