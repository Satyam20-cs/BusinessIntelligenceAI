from dataclasses import dataclass


@dataclass
class Telemetry:

    latency_ms: int

    model_calls: int

    tokens: int

    estimated_cost_usd: float

    provider: str


def make(
    latency_ms,
    model_calls,
    tokens,
    provider,
):
    """
    Convert narrative metadata into
    a telemetry object.
    """

    latency_ms = int(
        latency_ms or 0
    )

    model_calls = int(
        model_calls or 0
    )

    tokens = int(
        tokens or 0
    )

    estimated_cost = round(
        tokens / 1000 * 0.002,
        4
    )

    return Telemetry(
        latency_ms=latency_ms,
        model_calls=model_calls,
        tokens=tokens,
        estimated_cost_usd=estimated_cost,
        provider=provider or "unknown",
    )