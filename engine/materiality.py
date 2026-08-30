def classify_change(
    change_pct,
    materiality_pct=5,
    critical_pct=10,
):
    """
    Classify the magnitude of a KPI movement.
    """

    magnitude = abs(
        float(change_pct)
    )

    if magnitude >= critical_pct:
        return "CRITICAL"

    if magnitude >= materiality_pct:
        return "MATERIAL"

    if magnitude >= 2:
        return "WATCH"

    return "NORMAL"