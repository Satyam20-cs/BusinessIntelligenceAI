import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.io import load_all
from engine.kpi_engine import monthly_kpis, compare_periods
from engine.driver_engine import revenue_drivers
from engine.materiality import classify_change
from engine.confidence_engine import scenario_confidence, label_confidence
from engine.action_engine import recommend_action
from evidence.lineage import get_lineage, evidence_summary
from ai.narrative import generate_narrative
from feedback.feedback import save_feedback, load_feedback
from telemetry.metrics import make_telemetry

load_dotenv()

st.set_page_config(
    page_title="InsightX AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-title {font-size: 38px; font-weight: 800; margin-bottom: 0;}
.subtitle {color: #6b7280; font-size: 16px;}
.kpi-card {padding: 18px; border-radius: 14px; background: #f7f7fb; border: 1px solid #e5e7eb;}
.badge {padding: 5px 10px; border-radius: 12px; background: #eee; font-weight: 700;}
.small {font-size: 12px; color: #6b7280;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_all()

data = get_data()
sales, inventory, customer = data["sales"], data["inventory"], data["customer_metrics"]

monthly = monthly_kpis(sales, customer)
comparison = compare_periods(monthly)
drivers = revenue_drivers(sales, inventory, customer)

# Sidebar
st.sidebar.markdown("## InsightX AI")
st.sidebar.caption("BusinessIntelligence.ai — KPI intelligence-to-action")

persona = st.sidebar.selectbox(
    "Persona",
    ["Business Head", "Business Analyst"]
)

scenario = st.sidebar.selectbox(
    "Demo scenario",
    ["normal", "low_confidence", "sparse_history"],
    format_func=lambda x: {
        "normal": "Normal — material revenue decline",
        "low_confidence": "Low confidence — missing inventory",
        "sparse_history": "Sparse history — new product"
    }[x]
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Dashboard",
        "InsightX Investigation",
        "Evidence & Lineage",
        "Recommended Actions",
        "Governance & Feedback"
    ]
)

# Header
st.markdown('<div class="main-title">BusinessIntelligence.ai</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">InsightX AI — Detect → Explain → Connect → Recommend → Learn</div>', unsafe_allow_html=True)
st.divider()

# KPI helper
def fmt(name, value):
    if name in ["Revenue", "Profit"]:
        return f"₹{value/1e7:.2f} Cr"
    if name == "Conversion Rate" or name == "Return Rate":
        return f"{value:.2f}%"
    return f"{value:,.0f}"

# Scenario adjustment
conf = scenario_confidence(scenario)

if page == "Executive Dashboard":
    st.subheader("Business Health")
    cols = st.columns(5)
    for i, (name, info) in enumerate(comparison.items()):
        with cols[i]:
            st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.markdown(f"### {fmt(name, info['current'])}")
            arrow = "↓" if info["change_pct"] < 0 else "↑"
            st.write(f"{arrow} {abs(info['change_pct']):.1f}% vs previous period")
            st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Material KPI Movements")
    revenue_info = comparison["Revenue"]
    severity = classify_change(revenue_info["change_pct"])

    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="Revenue trend")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.error(f"Revenue {revenue_info['change_pct']:.1f}%")
        st.write(f"Severity: **{severity}**")
        st.write(f"Confidence: **{conf:.0%}**")
        if st.button("Investigate Revenue", type="primary"):
            st.session_state["goto_investigation"] = True
            st.info("Use the sidebar to open InsightX Investigation.")

    st.subheader("Top signals")
    top = drivers["region_drivers"][:3]
    if top:
        df = pd.DataFrame(top)
        fig2 = px.bar(df, x="contribution_pct", y="driver", orientation="h",
                      title="Regional contribution to revenue decline")
        st.plotly_chart(fig2, use_container_width=True)

elif page == "InsightX Investigation":
    st.subheader("InsightX Investigation")
    st.caption("Quantitative calculations are performed by the analytics engine; the LLM is only used for narrative synthesis.")

    info = comparison["Revenue"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", fmt("Revenue", info["current"]), f"{info['change_pct']:.1f}%")
    c2.metric("Severity", classify_change(info["change_pct"]))
    c3.metric("Confidence", f"{conf:.0%}", label_confidence(conf))

    st.markdown("### 1. DETECT")
    st.write(f"Revenue moved by **{info['change_pct']:.1f}%** compared with the previous period.")

    st.markdown("### 2. EXPLAIN")
    top_drivers = []
    for d in drivers["region_drivers"][:2]:
        top_drivers.append(d)
    for d in drivers["product_drivers"][:2]:
        top_drivers.append(d)

    if scenario == "low_confidence":
        st.warning("Inventory evidence is intentionally incomplete in this demo scenario. InsightX should not make a definitive inventory attribution.")
    elif scenario == "sparse_history":
        st.warning("This scenario is intended to demonstrate abstention for a newly launched product with limited historical evidence.")

    payload = {
        "kpi": "Revenue",
        "current": info["current"],
        "previous": info["previous"],
        "change_pct": info["change_pct"],
        "top_drivers": top_drivers,
        "confidence": conf,
        "scenario": scenario
    }

    narrative, meta = generate_narrative(payload, persona)
    st.markdown("### InsightX narrative")
    st.info(narrative)

    st.markdown("### 3. CONNECT")
    st.write("Driver chain: **Region/Product performance → Orders → Inventory/Customer signals → Revenue**")

    if top_drivers:
        tree_df = pd.DataFrame({
            "Driver": [d["driver"] for d in top_drivers],
            "Contribution (%)": [d["contribution_pct"] for d in top_drivers]
        })
        st.dataframe(tree_df, use_container_width=True, hide_index=True)

    if drivers["inventory_signal"]:
        st.write(
            f"Inventory stockouts changed from **{drivers['inventory_signal']['previous']:.0f}** "
            f"to **{drivers['inventory_signal']['current']:.0f}** "
            f"({drivers['inventory_signal']['change_pct']:.1f}%)."
        )

    st.markdown("### 4. RECOMMEND")
    action = recommend_action(drivers, conf)
    st.success(action["action"])
    st.write(f"**Owner:** {action['owner']}  |  **Expected impact:** {action['expected_impact']}")
    st.write(f"**Monitoring:** {action['monitoring']}")

    st.markdown("### 5. LEARN")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👍 Insight is correct"):
            save_feedback("correct", f"{persona} accepted the revenue insight.")
            st.success("Feedback recorded.")
    with col_b:
        if st.button("👎 Insight needs correction"):
            st.session_state["show_feedback_form"] = True

    if st.session_state.get("show_feedback_form"):
        note = st.text_area("What should be corrected?")
        if st.button("Save correction"):
            save_feedback("correction", note)
            st.success("Correction stored for the learning loop.")

    telemetry = make_telemetry(meta)
    st.caption(
        f"Telemetry — provider: {telemetry.provider} | latency: {telemetry.latency_ms} ms | "
        f"model calls: {telemetry.model_calls} | tokens: {telemetry.tokens_estimate} | "
        f"estimated cost: ${telemetry.estimated_cost_usd:.4f}"
    )

elif page == "Evidence & Lineage":
    st.subheader("Evidence & Lineage")
    st.write("Every important statement should be traceable to a source and analytical method.")

    summary = evidence_summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Data completeness", f"{summary['data_completeness']:.0%}")
    c2.metric("Evidence strength", f"{summary['evidence_strength']:.0%}")
    c3.metric("History strength", f"{summary['history_strength']:.0%}")
    c4.metric("Consistency", f"{summary['consistency']:.0%}")

    st.markdown("### Source lineage")
    st.dataframe(pd.DataFrame(get_lineage()), use_container_width=True, hide_index=True)

    st.markdown("### LLM vs non-LLM")
    st.code("""
Revenue calculation        -> Python/Pandas
KPI comparison             -> deterministic analytics
Driver contribution        -> contribution analysis
Confidence score           -> weighted evidence rules
Evidence/lineage           -> deterministic metadata
Narrative                   -> LLM (optional)
Persona adaptation          -> LLM (optional)
Action structure            -> business rules + LLM wording
""")

    st.markdown("### Data freshness")
    freshness = pd.DataFrame([
        ["sales.csv", "10 min ago", "Fresh"],
        ["inventory.csv", "2 hours ago", "Usable; slower refresh"],
        ["customer_metrics.csv", "35 min ago", "Fresh"]
    ], columns=["Source", "Last refresh", "Status"])
    st.dataframe(freshness, use_container_width=True, hide_index=True)

elif page == "Recommended Actions":
    st.subheader("Recommended Actions")
    action = recommend_action(drivers, conf)

    st.markdown("## Driver → Lever → Action → Impact → Owner → Confidence → Monitoring")

    rows = [
        ("Driver", action["driver"]),
        ("Controllable lever", action["lever"]),
        ("Recommended action", action["action"]),
        ("Expected impact", action["expected_impact"]),
        ("Owner", action["owner"]),
        ("Confidence", f"{action['confidence']:.0%}"),
        ("Monitoring plan", action["monitoring"])
    ]
    st.table(pd.DataFrame(rows, columns=["Component", "InsightX recommendation"]))

    if conf < 0.55:
        st.warning("Because confidence is low, InsightX recommends validation rather than a major corrective action.")

elif page == "Governance & Feedback":
    st.subheader("Governance, Security & Learning")

    st.markdown("### Role-based access demo")
    if persona == "Business Head":
        st.success("Business Head view: executive KPIs, top drivers, business impact and actions.")
    else:
        st.success("Business Analyst view: evidence, methods, lineage, confidence and analytical detail.")

    st.markdown("### Feedback loop")
    feedback = load_feedback()
    if feedback:
        st.dataframe(pd.DataFrame(feedback).tail(10), use_container_width=True, hide_index=True)
    else:
        st.info("No feedback yet. Use the Investigation page to accept or correct an insight.")

    st.markdown("### Runtime telemetry")
    st.metric("Tracked insights", max(1, len(feedback)))
    st.metric("LLM calls in this session", "0–1 per generated narrative")
    st.metric("Architecture", "Analytics-first, LLM-assisted")

    st.markdown("### Safety rule")
    st.warning(
        "InsightX is decision support, not an autonomous decision-maker. "
        "It should abstain when evidence is incomplete, contradictory or too sparse."
    )

st.sidebar.divider()
st.sidebar.caption("Prototype data is synthetic and intentionally engineered for the competition demo.")
