import os
import time

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def fallback(payload, persona):
    kpi = payload["kpi"]
    change = payload["change_pct"]
    conf = payload["confidence"]
    top = payload["top_drivers"]

    direction = "decreased" if change < 0 else "increased"
    drivers = ", ".join(top) if top else "multiple factors"

    if conf < 0.55:
        return (
            f"InsightX cannot confidently explain the {kpi} movement. "
            f"{kpi} {direction} by {abs(change):.1f}%, but the evidence is insufficient. "
            f"Potential signals include {drivers}. Confidence is {conf:.0%}. "
            "Validate the missing evidence before making a major decision."
        )

    if persona == "Business Head":
        return (
            f"{kpi} {direction} by {abs(change):.1f}% versus the previous equal-length period. "
            f"The strongest supported signals are {drivers}. "
            f"Confidence is {conf:.0%}. "
            "Prioritize the highest-impact controllable driver and monitor the KPI response."
        )

    return (
        f"{kpi} {direction} by {abs(change):.1f}%. "
        f"Top supported signals: {drivers}. "
        f"Confidence: {conf:.0%}. "
        "These signals indicate association, not guaranteed causation; see Evidence & Lineage for methods and source traceability."
    )

def generate(payload, persona):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.6")

    if not api_key or OpenAI is None:
        return fallback(payload, persona), {
            "latency_ms": 0, "model_calls": 0, "tokens": 0, "provider": "deterministic fallback"
        }

    prompt = f"""
You are InsightX AI, a business decision-support system.

Rules:
- Quantitative truth comes only from the verified payload.
- Never invent numbers.
- Do not claim causality from correlation.
- If confidence < 0.55, abstain from a definitive explanation.
- Persona: {persona}

Verified payload:
{payload}

Write a concise narrative:
1. What changed
2. Top supported contributors
3. Confidence and uncertainty
4. One next action

Do not recalculate metrics.
"""
    start = time.perf_counter()
    client = OpenAI(api_key=api_key)
    response = client.responses.create(model=model, input=prompt)
    latency = int((time.perf_counter() - start) * 1000)
    text = response.output_text
    usage = getattr(response, "usage", None)
    tokens = int(getattr(usage, "total_tokens", 0) or 0) if usage else 0

    return text, {
        "latency_ms": latency,
        "model_calls": 1,
        "tokens": tokens,
        "provider": "OpenAI Responses API"
    }
