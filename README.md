# BusinessIntelligence.ai — InsightX AI

A competition prototype for the Round 2 BusinessIntelligence.ai problem statement.

## Core workflow

DETECT -> EXPLAIN -> CONNECT -> RECOMMEND -> LEARN

## What this prototype demonstrates

- 5 connected KPIs
- 3 simulated data sources
- KPI semantic contract
- Material KPI movement detection
- Multi-factor driver/contribution analysis
- Evidence and lineage
- Confidence scoring
- Persona-specific narratives
- Low-confidence scenario
- Sparse-history/new-product scenario
- Role-based access demo
- Feedback loop
- Runtime telemetry
- Optional OpenAI-powered narrative generation

## Data strategy

The challenge explicitly allows simulated/illustrative data. This project therefore generates a controlled synthetic retail dataset instead of depending on proprietary company data.

## Run locally on Windows

1. Install Python 3.10–3.14.
2. Open PowerShell in this folder.
3. Create a virtual environment:

   `python -m venv .venv`

4. Activate it:

   `.venv\Scripts\Activate.ps1`

5. Install packages:

   `pip install -r requirements.txt`

6. Generate/refresh the demo data:

   `python generate_data.py`

7. Start the app:

   `streamlit run app.py`

8. Open the localhost address shown by Streamlit, normally http://localhost:8501.

## Optional LLM setup

Copy `.env.example` to `.env` and add:

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6

Without an API key, InsightX uses a deterministic fallback narrative so the prototype still works.

## Demo flow

1. Open Executive Dashboard.
2. Select the "Business Head" persona.
3. Click the Revenue investigation.
4. Show the driver contribution and driver tree.
5. Open Evidence & Lineage.
6. Open Recommended Actions.
7. Switch persona to Business Analyst.
8. Open Governance & Feedback.
9. Select the low-confidence scenario and show abstention.
10. Select the sparse-history scenario and show that InsightX avoids a strong conclusion.
# BusinessIntelligenceAI
