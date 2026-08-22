import os
import time

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def _fallback(payload, persona):
    kpi = payload["kpi"]
    change = payload["change_pct"]
    conf = payload["confidence"]
    drivers = payload["top_drivers"]
    direction = "decreased" if change < 0 else "increased"
    top = ", ".join([d["driver"] for d in drivers[:3]]) if drivers else "multiple factors"

    if conf < 0.55:
        return (
            f"InsightX cannot confidently explain the {kpi} movement. "
            f"{kpi} {direction} by {abs(change):.1f}%, but the available evidence is incomplete or sparse. "
            f"Potential signals include {top}. Confidence is {conf:.0%}. "
            "Validate the missing evidence before making a major business decision."
        )

    if persona == "Business Head":
        return (
            f"{kpi} {direction} by {abs(change):.1f}% versus the previous period. "
            f"The strongest signals are {top}. "
            f"InsightX estimates {conf:.0%} confidence in this explanation. "
            "The recommended next step is to address the most controllable driver first and monitor the KPI response."
        )

    return (
        f"{kpi} {direction} by {abs(change):.1f}%. "
        f"Top analytical signals: {top}. "
        f"Confidence: {conf:.0%}. "
        "The quantitative calculations come from the analytics engine; the narrative is a synthesis of those verified results."
    )

def generate_narrative(payload, persona):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.6")

    if not api_key or OpenAI is None:
        return _fallback(payload, persona), {"provider": "fallback", "latency_ms": 0, "model_calls": 0, "tokens_estimate": 0}

    client = OpenAI(api_key=api_key)
    prompt = f"""
You are InsightX AI, a business decision-support layer.
Never invent quantitative facts. Use only the verified analytics payload below.
Do not claim causality when the evidence only supports an association.
If confidence is below 0.55, explicitly abstain from a definitive explanation.
Persona: {persona}

Verified payload:
{payload}

Write a concise business narrative with:
1. What changed
2. Top supported contributors
3. Confidence/uncertainty
4. One practical next step

Do not recalculate numbers.
"""
    start = time.perf_counter()
    response = client.responses.create(model=model, input=prompt)
    latency = int((time.perf_counter() - start) * 1000)
    text = response.output_text
    usage = getattr(response, "usage", None)
    tokens = 0
    if usage:
        tokens = getattr(usage, "total_tokens", 0) or 0
    return text, {
        "provider": "OpenAI Responses API",
        "latency_ms": latency,
        "model_calls": 1,
        "tokens_estimate": tokens,
        "model": model
    }
