def classify_change(change_pct):
    magnitude = abs(change_pct)
    if magnitude >= 10:
        return "CRITICAL"
    if magnitude >= 5:
        return "HIGH"
    if magnitude >= 2:
        return "MODERATE"
    return "NORMAL"
