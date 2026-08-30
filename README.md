# InsightX

BusinessIntelligence.ai — AI-powered KPI storytelling
and decision-support prototype.

## Core workflow

Detect → Explain → Connect → Recommend → Learn

## What InsightX does

InsightX goes beyond a traditional dashboard.

Instead of only showing that a KPI changed, it attempts to explain:

1. What changed?
2. What are the strongest supported contributors?
3. What other business signals connect to the movement?
4. How confident is the explanation?
5. What should the business investigate or do next?

## Architecture

Data Sources
    ↓
Source Reconciliation
    ↓
KPI Engine
    ↓
Materiality
    ↓
Driver Analysis
    ↓
Unstructured Feedback
    ↓
Confidence Engine
    ↓
Evidence / Lineage
    ↓
Recommendation Engine
    ↓
Narrative Layer
    ↓
Persona
    ↓
Feedback

## Analytics-first principle

The LLM does not calculate KPIs.

Quantitative results are produced by deterministic
Python/Pandas analytics.

The language model only converts the verified analytics
payload into concise business language.

## Data

The prototype uses synthetic retail data.

Files:

- sales.csv
- inventory.csv
- customer_metrics.csv
- customer_feedback.csv

## Installation

Create a virtual environment:

python -m venv .venv

Activate:

.venv\Scripts\Activate.ps1

Install:

pip install -r requirements.txt

Generate data:

python generate_data.py

Run:

streamlit run app.py

## Optional OpenAI

Copy:

.env.example

to:

.env

Then add:

OPENAI_API_KEY=your_key

OPENAI_MODEL=gpt-5.6

The application still works without the API key.

## Demo scenarios

### Normal

Shows:

- KPI movement
- regional contribution
- product contribution
- inventory signals
- customer signals
- correlation
- confidence
- recommendations

### Low confidence

Demonstrates that InsightX does not make a
strong conclusion when evidence is insufficient.

### Sparse history

Demonstrates that InsightX avoids strong conclusions
when historical evidence is insufficient.

## Important principle

Correlation is treated as association,
not proof of causality.

InsightX supports human decision-making;
it does not replace human judgment.