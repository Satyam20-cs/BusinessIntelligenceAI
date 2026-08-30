# InsightX AI V2

This version is the next prototype step for the BusinessIntelligence.ai Round 2 problem.

## Improvements over the earlier skeleton

1. Equal-length 21-day KPI comparison instead of comparing a partial month with a full month.
2. Explicit source reconciliation.
3. Structured + unstructured data.
4. Customer feedback theme extraction.
5. Correlation analysis with an explicit non-causal interpretation.
6. Evidence lineage showing which component produced each claim.
7. Confidence is based on multiple evidence dimensions.
8. Low-confidence and sparse-history abstention.
9. Persona-specific narratives.
10. Recommendation objects with driver, lever, action, owner and monitoring.
11. Feedback persistence.
12. Runtime LLM telemetry.
13. Analytics-first architecture: the LLM never calculates KPI values.

## Windows setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

## Optional OpenAI setup

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5.6
```

The application still works without the key using a deterministic fallback narrative.

## Main demo

Normal:
- Executive Dashboard
- Revenue investigation
- Show region/product contributions
- Show stockout and customer-feedback signals
- Show correlation table
- Show recommendation
- Open Evidence & Lineage

Low confidence:
- Switch scenario to Low confidence
- Show abstention

Sparse history:
- Switch scenario to Sparse history
- Show abstention

Persona:
- Business Head → concise business impact
- Business Analyst → evidence and uncertainty

## Important

The data is synthetic. That is intentional for the competition prototype.
