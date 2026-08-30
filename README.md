InsightX

Business Decision Intelligence for Retail Performance

InsightX is a Streamlit-based business decision intelligence prototype
designed to help business teams understand what changed, why it
changed, what evidence supports the finding, and what action should be
taken next.

The application combines deterministic analytics with optional
AI-generated business narratives. The analytical layer remains the
source of truth, while the language layer converts verified results into
concise explanations.

1. Problem Statement

Business teams often work with multiple sources such as sales,
inventory, customer data, and qualitative feedback. The challenge is not
simply calculating KPIs; it is connecting signals across these sources
and turning them into reliable decisions.

Typical questions include:

Why did revenue increase or decrease?

Which regions or products contributed most to the movement?

Are inventory issues connected to the revenue change?

Are customer complaints or feedback supporting the same signal?

How complete and reliable is the available evidence?

What should the business team do next?

Can the insight be traced back to its underlying sources?

InsightX addresses these questions through a single decision-oriented
workflow.

2. Key Capabilities

Business Overview

Provides a high-level view of business performance through:

Revenue

Profit

Orders

Conversion Rate

Return Rate

Period-over-period comparison

Revenue trend visualization

Major regional contributors

Confidence score

Revenue Investigation

Moves from the headline signal to the underlying drivers:

Detect the revenue movement.

Identify regional contributors.

Identify product contributors.

Connect revenue movement with inventory signals.

Connect revenue movement with customer complaints.

Surface customer feedback themes.

Display statistical relationships.

Generate a concise interpretation.

Recommend prioritized actions.

Evidence

Provides transparency into the analytical process:

Source coverage

Cross-source dimension overlap

Analytical lineage

System boundaries

Separation between deterministic analytics and AI-generated language

Recommended Actions

Converts analytical findings into practical next steps, including:

Priority

Action

Driver

Business lever

Owner

Expected impact

Monitoring metric

Governance

Provides visibility around:

Confidence

Evidence quality

Feedback history

Business Head vs Business Analyst views

Analytical guardrails

AI system boundaries

3. Architecture

InsightX follows an analytics-first architecture:

                         InsightX
                            |
             +--------------+--------------+
             |                             |
        Data Sources                 User Interface
             |                             |
   +---------+---------+             Streamlit App
   |         |         |
 Sales   Inventory  Customer
   |         |         |
   +---------+---------+
             |
       Feedback Data
             |
             v
    Deterministic Analytics
             |
   +---------+---------+----------------+
   |         |         |                |
  KPI     Drivers   Reconciliation   Confidence
   |         |         |                |
   +---------+---------+----------------+
             |
             v
       Evidence Layer
             |
             v
      Optional AI Narrative
             |
             v
       Recommended Actions
             |
             v
        Business User

Core principle:

Analytics first. Language second.

AI explains verified analytical outputs; it does not replace the
analytical calculations.

4. Project Structure

InsightX/
|
├── app.py
├── requirements.txt
├── .env
├── README.md
|
├── data/
│   ├── sales.csv
│   ├── inventory.csv
│   ├── customer.csv
│   └── feedback.csv
|
├── utils/
│   └── io.py
|
├── engine/
│   ├── kpi_engine.py
│   ├── materiality.py
│   ├── driver_engine.py
│   ├── reconciliation.py
│   ├── unstructured_engine.py
│   ├── confidence_engine.py
│   └── action_engine.py
|
├── evidence/
│   └── lineage.py
|
├── feedback/
│   └── feedback.py
|
└── ai/
    └── narrative.py

File / Module                     Responsibility

app.py                          Streamlit interface and application orchestration
utils/io.py                     Loading and preparing source data
engine/kpi_engine.py            KPI calculation and period comparison
engine/materiality.py           Classification of KPI changes
engine/driver_engine.py         Revenue driver and cross-source analysis
engine/reconciliation.py        Source completeness and reconciliation
engine/unstructured_engine.py   Customer feedback theme extraction
engine/confidence_engine.py     Confidence scoring and labels
engine/action_engine.py         Recommended business actions
evidence/lineage.py             Analytical lineage and evidence traceability
feedback/feedback.py            Saving and loading user feedback
ai/narrative.py                 Optional AI-generated business narrative

5. Main User Flow

Detect → Prioritize → Investigate → Validate → Act → Learn

Detect

The Overview page presents current business performance and highlights
material movements.

Investigate

The Investigation page breaks the movement into regional and product
contributors.

Connect

Revenue movement is examined alongside inventory signals, customer
complaints, and qualitative feedback.

Validate

Evidence, source coverage, confidence, and lineage are displayed before
a strong conclusion is made.

Act

The system recommends prioritized actions based on available evidence.

Learn

Users can mark an insight as useful or submit a correction.

6. Personas

Business Head

Optimized for:

Business impact

Key contributors

Recommended decisions

Ownership

Expected impact

Business Analyst

Optimized for:

Evidence

Analytical methodology

Uncertainty

Source coverage

Statistical signals

Lineage

7. Confidence and Governance

InsightX does not treat every analytical result as equally reliable.

Confidence considers factors such as:

Data completeness

Driver strength

Historical evidence

Agreement between sources

Unstructured customer feedback support

The prototype demonstrates three scenarios:

Normal

Strong evidence supports a higher-confidence interpretation.

Low Confidence

The system reduces confidence and avoids definitive attribution when
evidence is incomplete.

Sparse History

The system warns against strong trend claims when historical evidence is
limited.

Governance principle:

When evidence is incomplete, contradictory, or sparse, confidence
should decrease and strong attribution should be avoided.

8. AI Boundary

The AI layer is intentionally separated from the analytical layer.

Deterministic components calculate:

KPIs

Period comparisons

Materiality

Revenue drivers

Reconciliation

Confidence

Evidence lineage

Recommended actions

The AI layer receives verified analytical results and generates a
concise business narrative.

This keeps quantitative truth grounded in deterministic analytics.

9. Technology Stack

Python

Streamlit

Pandas

Plotly

HTML/CSS

python-dotenv

Optional LLM integration for narrative generation

10. Installation

Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies

pip install -r requirements.txt

If a requirements file is not available:

pip install streamlit pandas plotly python-dotenv

Install the AI provider package required by ai/narrative.py if AI
narrative generation is enabled.

11. Environment Configuration

Create a .env file in the project root when the AI narrative module
requires an API key.

Example:

OPENAI_API_KEY=your_api_key_here

Never commit real API keys to the repository.

Recommended .gitignore entries:

.env
.venv/
__pycache__/

12. Running the Application

From the project root:

streamlit run app.py

Open the local Streamlit URL shown in the terminal, typically:

http://localhost:8501

13. Application Controls

The sidebar provides:

Workspace

Overview

Investigation

Evidence

Actions

Governance

View

Business Head

Business Analyst

Scenario

Normal

Low confidence

Sparse history

Analysis Window

The analysis period can be adjusted to evaluate different time windows.

14. Data Sources

The prototype works with four source categories.

Sales

Used for revenue, orders, product performance, regional performance, and
revenue trends.

Inventory

Used for stockout signals and inventory-related driver analysis.

Customer

Used for customer metrics, complaint signals, and cross-source analysis.

Feedback

Used for qualitative customer signals and theme extraction.

The prototype can operate with synthetic/demo retail data.

15. Evidence and Lineage

The Evidence workspace helps users understand how an insight was
produced.

It exposes:

Source completeness

Dimension overlap

Analytical lineage

System boundaries

The objective is to make insights traceable rather than presenting
unexplained AI output.

16. Feedback Loop

Users can evaluate an insight using:

Insight is useful

Needs correction

Corrections can include a written explanation of the issue.

Feedback is stored through the feedback module and displayed in
Governance.

17. Design Principles

Analytics First

Numerical conclusions should come from deterministic calculations.

Evidence Before Attribution

Strong causal claims should not be made without sufficient supporting
evidence.

Confidence Is Explicit

Users should be able to see how reliable an insight is.

Explainability

Important insights should be connected to underlying evidence.

Decision Orientation

The goal is not only to report what happened, but to help users decide
what to do next.

Human-in-the-Loop

InsightX supports business decisions; it does not autonomously make
decisions.

18. Example Decision Journey

Revenue movement detected
          |
          v
Identify major contributors
          |
          +--> Regional contribution
          |
          +--> Product contribution
          |
          v
Check inventory signals
          |
          v
Check customer complaints
          |
          v
Review customer feedback
          |
          v
Evaluate confidence
          |
          v
Generate business explanation
          |
          v
Recommend action
          |
          v
Monitor outcome

19. Limitations

InsightX is a decision-support prototype, not an autonomous
decision-making system.

Current limitations may include:

Synthetic or demo data

Limited historical depth

Dependence on source-data quality

Correlation does not prove causation

AI-generated narratives require human review

Recommendations depend on available evidence and analytical rules

These limitations are surfaced through confidence and governance
features.

20. Future Enhancements

Potential extensions include:

Live database connectors

Automated data-quality monitoring

More advanced causal analysis

Forecasting

Anomaly detection

Production-grade role-based access

Real-time alerts

Action tracking and outcome measurement

Feedback-driven model improvement

Additional business functions beyond revenue analysis

Production-grade audit logging

21. Demo Checklist

Before presenting:

Start the Streamlit application.

Open Overview.

Show the KPI cards and revenue trend.

Open Investigation.

Show regional and product drivers.

Show inventory and customer connections.

Show customer signals and statistical evidence.

Show the confidence score.

Demonstrate a low-confidence or sparse-history scenario.

Open Actions.

Open Evidence and show source coverage and lineage.

Finish with Governance and the analytics-first AI boundary.

22. Summary

InsightX transforms fragmented retail data into a structured business
decision workflow:

Detect → Investigate → Validate → Explain → Act → Learn

The central principle is:

The numbers come from analytics. The language explains the numbers.
The business user makes the decision.
