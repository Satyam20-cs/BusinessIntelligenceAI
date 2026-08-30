import os
import time


try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def fallback(payload, persona):

    kpi = payload["kpi"]

    change = float(
        payload["change_pct"]
    )

    confidence = float(
        payload["confidence"]
    )

    drivers = payload.get(
        "top_drivers",
        []
    )

    direction = (
        "declined"
        if change < 0
        else "increased"
    )

    driver_text = (
        ", ".join(
            drivers[:3]
        )
        if drivers
        else "multiple signals"
    )

    if confidence < 0.55:

        return (
            f"{kpi} {direction} by "
            f"{abs(change):.1f}%, but the "
            f"available evidence is not strong "
            f"enough for a definitive explanation. "
            f"Potential signals include "
            f"{driver_text}. "
            f"Validate the underlying evidence "
            f"before taking major action."
        )

    if persona == "Business Head":

        return (
            f"{kpi} {direction} by "
            f"{abs(change):.1f}% versus the "
            f"previous equal-length period. "
            f"The strongest supported signals are "
            f"{driver_text}. "
            f"Prioritize the highest-impact "
            f"controllable driver and monitor "
            f"the response."
        )

    return (
        f"{kpi} {direction} by "
        f"{abs(change):.1f}%. "
        f"Top supported signals: "
        f"{driver_text}. "
        f"Confidence is "
        f"{confidence:.0%}. "
        f"These signals indicate association, "
        f"not guaranteed causation."
    )


def generate(payload, persona):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6"
    )

    if (
        not api_key
        or OpenAI is None
    ):

        return (
            fallback(
                payload,
                persona
            ),

            {
                "latency_ms": 0,
                "model_calls": 0,
                "tokens": 0,
                "provider":
                    "deterministic fallback",
            }
        )

    prompt = f"""
You are the narrative layer of InsightX,
a business decision-support system.

Your job is NOT to perform analysis.

The verified analytics payload below is the
only source of quantitative truth.

Rules:

- Never invent numbers.
- Never calculate or modify KPI values.
- Never claim causality from correlation.
- If confidence is below 0.55, explicitly
  state that the evidence is insufficient.
- Keep the answer concise.
- Maximum 4 sentences.
- Avoid buzzwords.
- Write like an experienced business analyst.
- Do not say "As an AI".
- Do not use emojis.
- Do not repeat the entire dataset.

Persona:
{persona}

Verified analytics payload:
{payload}

Write:

1. What changed.
2. Strongest supported contributors.
3. Confidence / uncertainty.
4. One practical next step.
"""

    start = time.perf_counter()

    try:

        client = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model=model,
            input=prompt
        )

        latency = int(
            (
                time.perf_counter()
                - start
            )
            * 1000
        )

        text = response.output_text.strip()

        usage = getattr(
            response,
            "usage",
            None
        )

        tokens = 0

        if usage is not None:

            tokens = int(
                getattr(
                    usage,
                    "total_tokens",
                    0
                )
                or 0
            )

        return (
            text,

            {
                "latency_ms": latency,
                "model_calls": 1,
                "tokens": tokens,
                "provider":
                    "OpenAI Responses API",
            }
        )

    except Exception:

        return (
            fallback(
                payload,
                persona
            ),

            {
                "latency_ms": 0,
                "model_calls": 0,
                "tokens": 0,
                "provider":
                    "deterministic fallback",
            }
        )