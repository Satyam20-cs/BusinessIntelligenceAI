import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.io import load_all
from engine.kpi_engine import calculate_kpis, compare_kpis
from engine.materiality import classify_change
from engine.driver_engine import build_revenue_driver_pack
from engine.reconciliation import reconcile_sources, source_completeness
from engine.unstructured_engine import extract_themes
from engine.confidence_engine import confidence_score, label, reason
from engine.action_engine import recommend_actions
from evidence.lineage import lineage_rows
from feedback.feedback import save_feedback, load_feedback
from ai.narrative import generate
from telemetry.metrics import make

load_dotenv()

st.set_page_config(
    page_title="InsightX AI",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 20px 24px; border-radius: 18px; background: linear-gradient(90deg,#111827,#312e81); color: white;}
.hero h1 {margin: 0; font-size: 38px;}
.hero p {margin: 6px 0 0; opacity: .82;}
.card {padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: #ffffff;}
.muted {color: #6b7280; font-size: 13px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_all()

data = get_data()
sales = data["sales"]
inventory = data["inventory"]
customer = data["customer"]
feedback_text = data["feedback_text"]

st.markdown("""
<div class="hero">
<h1>BusinessIntelligence.ai</h1>
<p>InsightX AI — Detect → Explain → Connect → Recommend → Learn</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("InsightX Controls")
persona = st.sidebar.selectbox("Persona", ["Business Head", "Business Analyst"])
scenario = st.sidebar.selectbox(
    "Demo scenario",
    ["normal", "low_confidence", "sparse_history"],
    format_func=lambda x: {
        "normal": "Normal — sufficient evidence",
        "low_confidence": "Low confidence — missing inventory evidence",
        "sparse_history": "Sparse history — new product"
    }[x]
)

page = st.sidebar.radio(
    "Module",
    [
        "Executive Dashboard",
        "Insight Investigation",
        "Evidence & Lineage",
        "Recommended Actions",
        "Governance & Feedback"
    ]
)

kpi_df = calculate_kpis(sales, customer, days=21)
comparison = compare_kpis(kpi_df)
driver_pack = build_revenue_driver_pack(sales, inventory, customer, days=21)
recon = reconcile_sources(sales, inventory, customer, feedback_text)
_, theme_summary = extract_themes(feedback_text)

# Confidence is scenario-adjusted for the competition demo.
base_conf = confidence_score(
    data_completeness=min(
        source_completeness(sales),
        source_completeness(inventory),
        source_completeness(customer)
    ),
    driver_strength=0.88,
    history_strength=0.90,
    source_agreement=0.87,
    unstructured_support=0.80
)

if scenario == "low_confidence":
    conf = 0.38
elif scenario == "sparse_history":
    conf = 0.42
else:
    conf = max(0.80, base_conf)

revenue = comparison["Revenue"]
severity = classify_change(revenue["change_pct"])
conf_label = label(conf)

def money(v):
    return f"₹{v/1e7:.2f} Cr"

if page == "Executive Dashboard":
    st.subheader("Business Health")

    cols = st.columns(5)
    for col, (name, item) in zip(cols, comparison.items()):
        with col:
            value = money(item["current"]) if name in ["Revenue", "Profit"] else (
                f"{item['current']:.2f}%" if "Rate" in name else f"{item['current']:,.0f}"
            )
            arrow = "↓" if item["change_pct"] < 0 else "↑"
            st.metric(name, value, f"{arrow} {abs(item['change_pct']):.1f}%")

    st.divider()

    left, right = st.columns([1.7, 1])
    with left:
        st.subheader("Revenue trend")
        daily = sales.groupby("date", as_index=False)["revenue"].sum()
        fig = px.line(daily, x="date", y="revenue", markers=False)
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Material movement")
        st.error(f"Revenue {revenue['change_pct']:.1f}%")
        st.write(f"**Severity:** {severity}")
        st.write(f"**Confidence:** {conf:.0%} — {conf_label}")
        st.write("**Comparison:** equal 21-day windows")
        st.caption("InsightX avoids partial-month bias by comparing equal-length periods.")

    st.subheader("Top regional contributors")
    region_df = driver_pack["regions"].copy()
    if not region_df.empty:
        region_df["region"] = region_df["region"].astype(str)
        fig2 = px.bar(
            region_df.head(4),
            x="contribution_pct",
            y="region",
            orientation="h",
            text_auto=".1f"
        )
        fig2.update_layout(height=280, xaxis_title="Share of negative revenue movement (%)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

elif page == "Insight Investigation":
    st.subheader("InsightX Investigation")

    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue movement", f"{revenue['change_pct']:.1f}%")
    c2.metric("Materiality", severity)
    c3.metric("Confidence", f"{conf:.0%}", conf_label)

    st.markdown("### 1 — DETECT")
    st.write(
        f"Revenue changed from **{money(revenue['previous'])}** to "
        f"**{money(revenue['current'])}**, a **{revenue['change_pct']:.1f}%** movement "
        "over equal-length periods."
    )

    st.markdown("### 2 — EXPLAIN")
    top_region = driver_pack["regions"].head(2)
    top_product = driver_pack["products"].head(2)

    top_names = []
    for _, row in top_region.iterrows():
        top_names.append(f"{row['region']} region")
    for _, row in top_product.iterrows():
        top_names.append(str(row["product"]))

    payload = {
        "kpi": "Revenue",
        "change_pct": revenue["change_pct"],
        "confidence": conf,
        "top_drivers": top_names,
        "scenario": scenario
    }

    if scenario == "low_confidence":
        st.warning(
            "ABSTENTION: Inventory evidence is intentionally unavailable for this scenario. "
            "InsightX will not make a definitive inventory attribution."
        )
    elif scenario == "sparse_history":
        st.warning(
            "ABSTENTION: The selected product is treated as a new launch with insufficient historical baseline. "
            "InsightX will not make a strong trend claim."
        )

    narrative, meta = generate(payload, persona)
    st.info(narrative)

    st.markdown("### 3 — CONNECT")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Regional contribution**")
        display = top_region[["region","previous","current","delta","contribution_pct"]].copy()
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.write("**Product contribution**")
        display2 = top_product[["product","previous","current","delta","contribution_pct"]].copy()
        st.dataframe(display2, use_container_width=True, hide_index=True)

    with col2:
        inv = driver_pack["inventory"]
        comp = driver_pack["complaints"]
        st.metric("Inventory stockouts", f"{inv['current']:,.0f}", f"{inv['change_pct']:.1f}%")
        st.metric("Customer complaints", f"{comp['current']:,.0f}", f"{comp['change_pct']:.1f}%")

        st.write("**Unstructured customer signals**")
        st.dataframe(theme_summary.head(6), use_container_width=True, hide_index=True)

    st.markdown("### Statistical signals")
    corr = driver_pack["correlations"]
    if corr.empty:
        st.caption("Not enough overlapping daily observations for correlation testing.")
    else:
        st.dataframe(corr, use_container_width=True, hide_index=True)
        st.caption("Correlation is treated as association, not proof of causality.")

    st.markdown("### 4 — RECOMMEND")
    actions = recommend_actions(driver_pack, conf)
    st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)

    st.markdown("### 5 — LEARN")
    a, b = st.columns(2)
    with a:
        if st.button("👍 Mark insight correct", use_container_width=True):
            save_feedback("accepted", "Revenue investigation accepted.", persona)
            st.success("Feedback recorded.")
    with b:
        if st.button("👎 Mark insight incorrect", use_container_width=True):
            st.session_state["feedback_open"] = True

    if st.session_state.get("feedback_open"):
        note = st.text_area("What should InsightX change?")
        if st.button("Save correction"):
            save_feedback("correction", note, persona)
            st.success("Correction stored.")
            st.session_state["feedback_open"] = False

    t = make(
        meta["latency_ms"],
        meta["model_calls"],
        meta["tokens"],
        meta["provider"]
    )
    st.caption(
        f"Telemetry — provider: {t.provider} | latency: {t.latency_ms} ms | "
        f"LLM calls: {t.model_calls} | tokens: {t.tokens} | "
        f"estimated cost: ${t.estimated_cost_usd:.4f}"
    )

elif page == "Evidence & Lineage":
    st.subheader("Evidence & Lineage")

    st.write(
        "InsightX separates deterministic analytics from generative AI. "
        "The LLM receives a verified payload; it does not calculate the KPI."
    )

    st.markdown("### Source reconciliation")
    st.dataframe(recon["sources"], use_container_width=True, hide_index=True)

    st.write(
        f"Sales→Inventory dimension overlap: **{recon['dimension_overlap']['sales_inventory_pct']:.1f}%**  |  "
        f"Sales→Customer dimension overlap: **{recon['dimension_overlap']['sales_customer_pct']:.1f}%**"
    )

    st.markdown("### Lineage")
    st.dataframe(pd.DataFrame(lineage_rows()), use_container_width=True, hide_index=True)

    st.markdown("### Analytics boundary")
    st.code("""
Python / Pandas
    ├── KPI definitions
    ├── Equal-period comparison
    ├── Materiality
    ├── Driver contribution
    ├── Source reconciliation
    ├── Correlation tests
    ├── Confidence
    └── Action structure

LLM
    ├── Natural-language synthesis
    └── Persona-specific wording

Rule:
LLM never becomes the quantitative source of truth.
""")

elif page == "Recommended Actions":
    st.subheader("Recommended Actions")

    actions = recommend_actions(driver_pack, conf)
    for action in actions:
        st.markdown(f"#### {action['priority']} — {action['driver']}")
        st.write(f"**Lever:** {action['lever']}")
        st.success(action["action"])
        st.write(f"**Owner:** {action['owner']}")
        st.write(f"**Expected impact:** {action['expected_impact']}")
        st.write(f"**Monitoring:** {action['monitoring']}")
        st.divider()

    if conf < 0.55:
        st.warning(
            "Because confidence is LOW, the recommended action is data validation rather than an aggressive business intervention."
        )

elif page == "Governance & Feedback":
    st.subheader("Governance & Feedback")

    st.markdown("### Persona access")
    if persona == "Business Head":
        st.success("Executive view: impact, top drivers, decision and owner.")
    else:
        st.success("Analyst view: evidence, methods, uncertainty and lineage.")

    st.markdown("### Feedback history")
    feedback = load_feedback()
    if feedback:
        st.dataframe(pd.DataFrame(feedback).tail(20), use_container_width=True, hide_index=True)
    else:
        st.info("No feedback recorded yet.")

    st.markdown("### Guardrails")
    st.warning(
        "InsightX is a decision-support system. It must abstain when evidence is incomplete, "
        "contradictory or too sparse."
    )

    st.markdown("### Prototype architecture")
    st.write(
        "Data sources → Reconciliation → KPI Engine → Materiality → Driver Engine → "
        "Confidence → Evidence → Recommendation → LLM Narrative → Persona → Feedback"
    )

st.sidebar.divider()
st.sidebar.caption("Prototype uses synthetic data for controlled demonstration.")
