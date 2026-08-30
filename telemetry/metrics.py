import time
from dataclasses import dataclass

@dataclass
class Telemetry:
    latency_ms: int
    model_calls: int
    tokens: int
    estimated_cost_usd: float
    provider: str

def make(latency_ms, model_calls, tokens, provider):
    return Telemetry(
        latency_ms=int(latency_ms),
        model_calls=int(model_calls),
        tokens=int(tokens),
        estimated_cost_usd=round(tokens / 1000 * 0.002, 4),
        provider=provider
    )
