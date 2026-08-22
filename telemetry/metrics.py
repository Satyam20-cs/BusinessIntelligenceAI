from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Telemetry:
    timestamp: str
    latency_ms: int
    model_calls: int
    tokens_estimate: int
    estimated_cost_usd: float
    provider: str

def estimate_cost(tokens, cost_per_1k=0.002):
    return round((tokens / 1000) * cost_per_1k, 4)

def make_telemetry(meta):
    tokens = int(meta.get("tokens_estimate", 0))
    return Telemetry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        latency_ms=int(meta.get("latency_ms", 0)),
        model_calls=int(meta.get("model_calls", 0)),
        tokens_estimate=tokens,
        estimated_cost_usd=estimate_cost(tokens),
        provider=meta.get("provider", "fallback")
    )
