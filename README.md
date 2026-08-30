# InsightX

**Business Decision Intelligence for Retail Performance**

InsightX is a Streamlit-based business decision intelligence prototype that helps business teams understand *what changed, why it changed, what evidence supports the finding, and what action should be taken next.*

It combines deterministic analytics with optional AI-generated business narratives. The analytical layer is the source of truth — the language layer only converts verified results into concise explanations.

> **Core principle:** Analytics first. Language second.
> AI explains verified analytical outputs; it does not replace the analytical calculations.

---

## 1. Problem Statement

Business teams often work across multiple sources — sales, inventory, customer data, and qualitative feedback. The challenge isn't calculating KPIs; it's connecting signals across these sources and turning them into reliable decisions.

Typical questions InsightX answers:

- Why did revenue increase or decrease?
- Which regions or products contributed most to the movement?
- Are inventory issues connected to the revenue change?
- Do customer complaints or feedback support the same signal?
- How complete and reliable is the available evidence?
- What should the business team do next?
- Can the insight be traced back to its underlying sources?

## 2. Key Capabilities

- **Business Overview** — Revenue, profit, orders, conversion rate, return rate, period-over-period comparison, revenue trend, top regional contributors, and a confidence score.
- **Revenue Investigation** — Detects the movement, identifies regional/product contributors, connects it to inventory and customer complaint signals, surfaces feedback themes, shows statistical relationships, and generates a concise interpretation with recommended actions.
- **Evidence** — Source coverage, cross-source dimension overlap, analytical lineage, system boundaries, and the separation between deterministic analytics and AI-generated language.
- **Recommended Actions** — Priority, action, driver, business lever, owner, expected impact, and monitoring metric.
- **Governance** — Confidence, evidence quality, feedback history, Business Head vs. Business Analyst views, analytical guardrails, and AI system boundaries.

## 3. Architecture

```
Data Sources (Sales, Inventory, Customer, Feedback)
            │
            ▼
   Deterministic Analytics
   (KPI, Drivers, Reconciliation, Confidence)
            │
            ▼
      Evidence Layer
            │
            ▼
   Optional AI Narrative
            │
            ▼
   Recommended Actions
            │
            ▼
      Business User
```

## 4. Project Structure

```
InsightX/
├── app.py
├── requirements.txt
├── .env
├── README.md
│
├── data/
│   ├── sales.csv
│   ├── inventory.csv
│   ├── customer.csv
│   └── feedback.csv
│
├── utils/
│   └── io.py
│
├── engine/
│   ├── kpi_engine.py
│   ├── materiality.py
│   ├── driver_engine.py
│   ├── reconciliation.py
│   ├── unstructured_engine.py
│   ├── confidence_engine.py
│   └── action_engine.py
│
├── evidence/
│   └── lineage.py
│
├── feedback/
│   └── feedback.py
│
└── ai/
    └── narrative.py
```

| File / Module | Responsibility |
|---|---|
| `app.py` | Streamlit interface and application orchestration |
| `utils/io.py` | Loading and preparing source data |
| `engine/kpi_engine.py` | KPI calculation and period comparison |
| `engine/materiality.py` | Classification of KPI changes |
| `engine/driver_engine.py` | Revenue driver and cross-source analysis |
| `engine/reconciliation.py` | Source completeness and reconciliation |
| `engine/unstructured_engine.py` | Customer feedback theme extraction |
| `engine/confidence_engine.py` | Confidence scoring and labels |
| `engine/action_engine.py` | Recommended business actions |
| `evidence/lineage.py` | Analytical lineage and evidence traceability |
| `feedback/feedback.py` | Saving and loading user feedback |
| `ai/narrative.py` | Optional AI-generated business narrative |

## 5. Main User Flow

**Detect → Prioritize → Investigate → Validate → Act → Learn**

1. **Detect** — The Overview page presents current performance and highlights material movements.
2. **Investigate** — The Investigation page breaks the movement into regional and product contributors.
3. **Connect** — Revenue movement is examined alongside inventory signals, customer complaints, and qualitative feedback.
4. **Validate** — Evidence, source coverage, confidence, and lineage are shown before a strong conclusion is made.
5. **Act** — The system recommends prioritized actions based on available evidence.
6. **Learn** — Users can mark an insight as useful or submit a correction.

## 6. Personas

- **Business Head** — optimized for business impact, key contributors, recommended decisions, ownership, expected impact.
- **Business Analyst** — optimized for evidence, analytical methodology, uncertainty, source coverage, statistical signals, lineage.

## 7. Confidence & Governance

InsightX does not treat every analytical result as equally reliable. Confidence is based on:

- Data completeness
- Driver strength
- Historical evidence
- Agreement between sources
- Unstructured customer feedback support

Three demo scenarios illustrate this:

- **Normal** — strong evidence supports a higher-confidence interpretation.
- **Low Confidence** — confidence is reduced and definitive attribution is avoided when evidence is incomplete.
- **Sparse History** — the system warns against strong trend claims when historical evidence is limited.

**Governance principle:** When evidence is incomplete, contradictory, or sparse, confidence should decrease and strong attribution should be avoided.

## 8. AI Boundary

The AI layer is intentionally separated from the analytical layer.

**Deterministic components calculate:**
- KPIs
- Period comparisons
- Materiality
- Revenue drivers
- Reconciliation

**The AI layer (optional) only narrates** verified analytical output into a concise, readable explanation — it never performs the underlying calculations.

## 9. Installation

```bash
git clone <your-repo-url>
cd InsightX
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-5.6
```

> The AI narrative feature is optional — the app runs on deterministic analytics alone even without a configured API key.

## 10. Running the App

```bash
streamlit run app.py
```

To regenerate sample data:

```bash
python generate_data.py
```

## 11. Testing

```bash
pytest tests/
```

## 12. Tech Stack

- **Streamlit** — application interface
- **Pandas / NumPy** — data processing
- **Plotly** — visualization
- **SciPy / scikit-learn** — statistical analysis
- **OpenAI API** — optional narrative generation

