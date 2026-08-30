def confidence_score(
    data_completeness,
    driver_strength,
    history_strength,
    source_agreement,
    unstructured_support,
):
    """
    Weighted evidence confidence score.

    All inputs should be between 0 and 1.
    """

    score = (
        0.25 * data_completeness
        + 0.30 * driver_strength
        + 0.15 * history_strength
        + 0.20 * source_agreement
        + 0.10 * unstructured_support
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                score
            )
        ),
        2
    )


def label(score):

    if score >= 0.80:
        return "HIGH"

    if score >= 0.55:
        return "MEDIUM"

    return "LOW"


def reason(
    score,
    missing_source=False,
    sparse_history=False,
):
    """
    Human-readable explanation of
    why confidence is high/low.
    """

    reasons = []

    if missing_source:

        reasons.append(
            "a required source is incomplete"
        )

    if sparse_history:

        reasons.append(
            "the historical baseline is too short"
        )

    if score < 0.55 and not reasons:

        reasons.append(
            "evidence is weak or conflicting"
        )

    if not reasons:

        return (
            "multiple independent signals "
            "support the finding"
        )

    return "; ".join(reasons)


def scenario_confidence(scenario):

    return {
        "normal": 0.84,
        "low_confidence": 0.38,
        "sparse_history": 0.42,
    }.get(
        scenario,
        0.70
    )