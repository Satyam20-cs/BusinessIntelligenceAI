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
from engine.confidence_engine import confidence_score, label
from engine.action_engine import recommend_actions
from evidence.lineage import lineage_rows
from feedback.feedback import save_feedback, load_feedback
from ai.narrative import generate
from telemetry.metrics import make


load_dotenv()

st.set_page_config(
    page_title="InsightX",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>


    html {
        scroll-behavior: smooth;
    }

    .stApp {
        background: #fafafa;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Remove excessive Streamlit spacing */

    div[data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }


    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8e8e8;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }


    .brand {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.4px;
        color: #111111;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #8a8a8a;
        margin-top: 2px;
    }


    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e9e9e9;
    }

    .page-title {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #111111;
        margin: 0;
    }

    .page-subtitle {
        color: #777777;
        font-size: 14px;
        margin-top: 5px;
    }


    .section-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8a8a8a;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
    }

    .section-title {
        font-size: 21px;
        font-weight: 650;
        letter-spacing: -0.4px;
        color: #171717;
        margin-bottom: 0.15rem;
    }

    .section-description {
        font-size: 13px;
        color: #777777;
        margin-bottom: 1rem;
    }


    .kpi-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 18px;
        min-height: 112px;
    }

    .kpi-name {
        font-size: 12px;
        color: #777777;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -0.6px;
        color: #161616;
    }

    .kpi-change-negative {
        color: #b42318;
        font-size: 12px;
        font-weight: 600;
        margin-top: 5px;
    }

    .kpi-change-positive {
        color: #18794e;
        font-size: 12px;
        font-weight: 600;
        margin-top: 5px;
    }

    .kpi-change-neutral {
        color: #777777;
        font-size: 12px;
        margin-top: 5px;
    }


    .insight-card {
        background: #ffffff;
        border: 1px solid #dedede;
        border-radius: 14px;
        padding: 24px;
        margin-top: 8px;
    }

    .insight-status {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #b42318;
        margin-bottom: 10px;
    }

    .insight-title {
        font-size: 24px;
        line-height: 1.25;
        font-weight: 650;
        letter-spacing: -0.6px;
        color: #161616;
    }

    .insight-copy {
        color: #666666;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 8px;
    }

    .confidence-box {
        background: #f6f6f6;
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 15px;
    }

    .confidence-label {
        font-size: 11px;
        color: #777777;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .confidence-value {
        font-size: 22px;
        font-weight: 700;
        color: #161616;
    }

    .driver-row {
        padding: 13px 0;
        border-bottom: 1px solid #eeeeee;
    }

    .driver-name {
        font-size: 13px;
        font-weight: 600;
        color: #222222;
    }

    .driver-meta {
        font-size: 11px;
        color: #888888;
        margin-top: 3px;
    }


    .action-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .action-priority {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #777777;
    }

    .action-title {
        font-size: 16px;
        font-weight: 650;
        margin-top: 6px;
        color: #191919;
    }

    .action-meta {
        font-size: 12px;
        color: #777777;
        margin-top: 8px;
    }


    .status-ok {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        background: #edf8f2;
        color: #18794e;
        font-size: 11px;
        font-weight: 600;
    }

    .status-warning {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        background: #fff6e5;
        color: #9a6700;
        font-size: 11px;
        font-weight: 600;
    }

    .status-danger {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        background: #fff0ef;
        color: #b42318;
        font-size: 11px;
        font-weight: 600;
    }


    .section-nav {
        display: flex;
        gap: 18px;
        padding: 10px 0 18px 0;
        border-bottom: 1px solid #eeeeee;
        margin-bottom: 20px;
    }

    .section-nav a {
        color: #777777;
        text-decoration: none;
        font-size: 12px;
        font-weight: 500;
    }

    .section-nav a:hover {
        color: #111111;
    }


    .stButton > button {
        border-radius: 8px;
        border: 1px solid #dddddd;
        background: #ffffff;
        color: #222222;
        font-weight: 600;
        font-size: 13px;
        min-height: 38px;
    }

    .stButton > button:hover {
        border-color: #aaaaaa;
        color: #111111;
        background: #f8f8f8;
    }


    div[data-testid="stDataFrame"] {
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        overflow: hidden;
    }


    .js-plotly-plot {
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        background: #ffffff;
    }


    .streamlit-expanderHeader {
        font-size: 13px;
        font-weight: 600;
    }


    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    return load_all()


data = get_data()

sales = data["sales"]
inventory = data["inventory"]
customer = data["customer"]
feedback_text = data["feedback_text"]



with st.sidebar:

    st.markdown(
        """
        <div class="brand">InsightX</div>
        <div class="brand-subtitle">
            Business decision intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    persona = st.selectbox(
        "View",
        ["Business Head", "Business Analyst"],
    )

    scenario = st.selectbox(
        "Scenario",
        ["normal", "low_confidence", "sparse_history"],
        format_func=lambda x: {
            "normal": "Normal",
            "low_confidence": "Low confidence",
            "sparse_history": "Sparse history",
        }[x],
    )

    st.divider()

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Investigation",
            "Evidence",
            "Actions",
            "Governance",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "Prototype environment · Synthetic retail data"
    )



kpi_df = calculate_kpis(
    sales,
    customer,
    days=21,
)

comparison = compare_kpis(kpi_df)

driver_pack = build_revenue_driver_pack(
    sales,
    inventory,
    customer,
    days=21,
)

recon = reconcile_sources(
    sales,
    inventory,
    customer,
    feedback_text,
)

_, theme_summary = extract_themes(
    feedback_text
)



base_conf = confidence_score(
    data_completeness=min(
        source_completeness(sales),
        source_completeness(inventory),
        source_completeness(customer),
    ),
    driver_strength=0.88,
    history_strength=0.90,
    source_agreement=0.87,
    unstructured_support=0.80,
)

if scenario == "low_confidence":
    conf = 0.38

elif scenario == "sparse_history":
    conf = 0.42

else:
    conf = max(0.80, base_conf)


conf_label = label(conf)

revenue = comparison["Revenue"]

severity = classify_change(
    revenue["change_pct"]
)



def money(value):
    return f"₹{value / 1e7:.2f} Cr"


def change_class(value):

    if value < 0:
        return "negative"

    if value > 0:
        return "positive"

    return "neutral"


def render_kpi(name, item):

    current = item["current"]
    change = item["change_pct"]

    if name in ["Revenue", "Profit"]:
        value = money(current)

    elif "Rate" in name:
        value = f"{current:.2f}%"

    else:
        value = f"{current:,.0f}"

    css_class = change_class(change)

    arrow = "↓" if change < 0 else "↑"

    if change == 0:
        arrow = "—"

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-name">{name}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-change-{css_class}">
                {arrow} {abs(change):.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plot_layout(fig, height=320):

    fig.update_layout(
        height=height,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            size=12,
            color="#555555",
        ),
        showlegend=False,
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#eeeeee",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#f0f0f0",
        zeroline=False,
    )

    return fig



if page == "Overview":

    st.markdown(
        """
        <div class="topbar">
            <div>
                <div class="page-title">Business overview</div>
                <div class="page-subtitle">
                    A concise view of current business performance and material changes.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-label">Performance</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(comparison))

    for col, (name, item) in zip(
        cols,
        comparison.items(),
    ):

        with col:
            render_kpi(name, item)


    st.markdown(
        """
        <div class="section-nav">
            <a href="#performance">Performance</a>
            <a href="#key-signal">Key signal</a>
            <a href="#contributors">Contributors</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div id="performance"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Revenue performance</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Current revenue compared with the previous equal-length period.'
        '</div>',
        unsafe_allow_html=True,
    )

    daily = (
        sales.groupby(
            "date",
            as_index=False
        )["revenue"]
        .sum()
    )

    fig = px.line(
        daily,
        x="date",
        y="revenue",
    )

    fig.update_traces(
        line_width=2.2,
        hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>",
    )

    fig = plot_layout(
        fig,
        height=330,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )


    st.markdown(
        '<div id="key-signal"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">Key signal</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [2.2, 1],
        gap="large",
    )

    with left:

        st.markdown(
            f"""
            <div class="insight-card">

                <div class="insight-status">
                    Material movement
                </div>

                <div class="insight-title">
                    Revenue declined {abs(revenue["change_pct"]):.1f}%
                </div>

                <div class="insight-copy">
                    Revenue moved from
                    <strong>{money(revenue["previous"])}</strong>
                    to
                    <strong>{money(revenue["current"])}</strong>
                    across equal 21-day periods.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            f"""
            <div class="confidence-box">

                <div class="confidence-label">
                    Confidence
                </div>

                <div class="confidence-value">
                    {conf:.0%}
                </div>

                <div style="font-size:12px;color:#777;margin-top:3px;">
                    {conf_label}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown(
        '<div id="contributors"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">Contributors</div>',
        unsafe_allow_html=True,
    )

    region_df = driver_pack["regions"].copy()

    if not region_df.empty:

        fig2 = px.bar(
            region_df.head(4),
            x="contribution_pct",
            y="region",
            orientation="h",
        )

        fig2.update_traces(
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
        )

        fig2.update_layout(
            xaxis_title="Share of negative movement",
            yaxis_title="",
        )

        fig2 = plot_layout(
            fig2,
            height=260,
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )



elif page == "Investigation":

    st.markdown(
        """
        <div class="topbar">
            <div>
                <div class="page-title">Revenue investigation</div>
                <div class="page-subtitle">
                    Understand what changed, what may be contributing, and what to do next.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-nav">
            <a href="#signal">Signal</a>
            <a href="#drivers">Drivers</a>
            <a href="#connections">Connections</a>
            <a href="#recommendation">Recommendation</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div id="signal"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">01 · Signal</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-card">

            <div class="insight-status">
                Revenue movement · {severity}
            </div>

            <div class="insight-title">
                Revenue is down {abs(revenue["change_pct"]):.1f}%
            </div>

            <div class="insight-copy">
                The current 21-day period generated
                <strong>{money(revenue["current"])}</strong>,
                compared with
                <strong>{money(revenue["previous"])}</strong>
                in the previous period.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div id="drivers"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">02 · Drivers</div>',
        unsafe_allow_html=True,
    )

    top_region = driver_pack["regions"].head(3)
    top_product = driver_pack["products"].head(3)

    driver_col1, driver_col2 = st.columns(
        2,
        gap="large",
    )

    with driver_col1:

        st.markdown(
            '<div class="section-title">Regional contribution</div>',
            unsafe_allow_html=True,
        )

        if not top_region.empty:

            display = top_region[
                [
                    "region",
                    "previous",
                    "current",
                    "delta",
                    "contribution_pct",
                ]
            ].copy()

            display.columns = [
                "Region",
                "Previous",
                "Current",
                "Change",
                "Share",
            ]

            display["Previous"] = display["Previous"].map(money)
            display["Current"] = display["Current"].map(money)

            display["Change"] = display["Change"].map(
                lambda x: money(x)
            )

            display["Share"] = display["Share"].map(
                lambda x: f"{x:.1f}%"
            )

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

    with driver_col2:

        st.markdown(
            '<div class="section-title">Product contribution</div>',
            unsafe_allow_html=True,
        )

        if not top_product.empty:

            display2 = top_product[
                [
                    "product",
                    "previous",
                    "current",
                    "delta",
                    "contribution_pct",
                ]
            ].copy()

            display2.columns = [
                "Product",
                "Previous",
                "Current",
                "Change",
                "Share",
            ]

            display2["Previous"] = display2["Previous"].map(money)
            display2["Current"] = display2["Current"].map(money)

            display2["Change"] = display2["Change"].map(
                lambda x: money(x)
            )

            display2["Share"] = display2["Share"].map(
                lambda x: f"{x:.1f}%"
            )

            st.dataframe(
                display2,
                use_container_width=True,
                hide_index=True,
            )


    st.markdown(
        '<div id="connections"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">03 · Connections</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(
        2,
        gap="large",
    )

    with c1:

        inv = driver_pack["inventory"]

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Inventory stockouts
                </div>

                <div class="kpi-value">
                    {inv["current"]:,.0f}
                </div>

                <div class="kpi-change-negative">
                    ↑ {abs(inv["change_pct"]):.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        comp = driver_pack["complaints"]

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Customer complaints
                </div>

                <div class="kpi-value">
                    {comp["current"]:,.0f}
                </div>

                <div class="kpi-change-negative">
                    ↑ {abs(comp["change_pct"]):.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    if not theme_summary.empty:

        st.markdown(
            '<div class="section-title">Customer signals</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            theme_summary.head(6),
            use_container_width=True,
            hide_index=True,
        )


    corr = driver_pack["correlations"]

    if not corr.empty:

        with st.expander(
            "Statistical signals",
            expanded=False,
        ):

            st.dataframe(
                corr,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Correlation indicates association, not causation."
            )


    if scenario == "low_confidence":

        st.warning(
            "Evidence is incomplete. InsightX will not make a "
            "definitive inventory attribution."
        )

    elif scenario == "sparse_history":

        st.warning(
            "Historical evidence is limited. InsightX will not "
            "make a strong trend claim for the selected scenario."
        )


    payload = {
        "kpi": "Revenue",
        "change_pct": revenue["change_pct"],
        "confidence": conf,
        "top_drivers": [
            f"{row['region']} region"
            for _, row in top_region.iterrows()
        ]
        + [
            str(row["product"])
            for _, row in top_product.iterrows()
        ],
        "scenario": scenario,
    }

    narrative, meta = generate(
        payload,
        persona,
    )

    st.markdown(
        '<div class="section-label">Interpretation</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-card">

            <div class="insight-copy"
                 style="margin-top:0;font-size:15px;color:#333;">
                {narrative}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div id="recommendation"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">04 · Recommendation</div>',
        unsafe_allow_html=True,
    )

    actions = recommend_actions(
        driver_pack,
        conf,
    )

    for action in actions[:3]:

        st.markdown(
            f"""
            <div class="action-card">

                <div class="action-priority">
                    {action["priority"]}
                </div>

                <div class="action-title">
                    {action["action"]}
                </div>

                <div class="action-meta">
                    Driver: {action["driver"]}
                    &nbsp; · &nbsp;
                    Owner: {action["owner"]}
                    &nbsp; · &nbsp;
                    Monitoring: {action["monitoring"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown(
        '<div class="section-label">Feedback</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:

        if st.button(
            "Insight is useful",
            use_container_width=True,
        ):

            save_feedback(
                "accepted",
                "Revenue investigation accepted.",
                persona,
            )

            st.success(
                "Feedback recorded."
            )

    with col_b:

        if st.button(
            "Needs correction",
            use_container_width=True,
        ):

            st.session_state[
                "feedback_open"
            ] = True

    if st.session_state.get(
        "feedback_open",
        False,
    ):

        note = st.text_area(
            "What should be corrected?",
            placeholder="Describe the issue...",
        )

        if st.button(
            "Save correction",
            use_container_width=True,
        ):

            save_feedback(
                "correction",
                note,
                persona,
            )

            st.success(
                "Correction stored."
            )

            st.session_state[
                "feedback_open"
            ] = False



elif page == "Evidence":

    st.markdown(
        """
        <div class="topbar">
            <div>
                <div class="page-title">Evidence</div>
                <div class="page-subtitle">
                    See where each insight comes from and how the system validates it.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">Source coverage</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        recon["sources"],
        use_container_width=True,
        hide_index=True,
    )

    overlap = recon["dimension_overlap"]

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Sales ↔ Inventory overlap
                </div>

                <div class="kpi-value">
                    {overlap["sales_inventory_pct"]:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Sales ↔ Customer overlap
                </div>

                <div class="kpi-value">
                    {overlap["sales_customer_pct"]:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-label">Lineage</div>',
        unsafe_allow_html=True,
    )

    lineage = pd.DataFrame(
        lineage_rows()
    )

    st.dataframe(
        lineage,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        '<div class="section-label">System boundary</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="insight-card">

            <div class="section-title">
                Analytics first. Language second.
            </div>

            <div class="insight-copy">
                KPI calculations, comparisons, materiality,
                driver analysis, reconciliation and confidence
                are handled by deterministic analytics.
                <br><br>
                The language layer only turns verified results
                into a concise business explanation.
                <br><br>
                <strong>The language model is not the source of truth.</strong>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )



elif page == "Actions":

    st.markdown(
        """
        <div class="topbar">
            <div>
                <div class="page-title">Recommended actions</div>
                <div class="page-subtitle">
                    Prioritized next steps based on the available evidence.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    actions = recommend_actions(
        driver_pack,
        conf,
    )

    if conf < 0.55:

        st.warning(
            "Confidence is low. Recommended action is validation "
            "rather than an aggressive business intervention."
        )

    for action in actions:

        st.markdown(
            f"""
            <div class="action-card">

                <div class="action-priority">
                    {action["priority"]}
                </div>

                <div class="action-title">
                    {action["action"]}
                </div>

                <div class="action-meta">
                    Driver · {action["driver"]}
                    <br>
                    Lever · {action["lever"]}
                    <br>
                    Owner · {action["owner"]}
                    <br>
                    Expected impact · {action["expected_impact"]}
                    <br>
                    Monitoring · {action["monitoring"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )



elif page == "Governance":

    st.markdown(
        """
        <div class="topbar">
            <div>
                <div class="page-title">Governance</div>
                <div class="page-subtitle">
                    Transparency, feedback and decision-support guardrails.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-label">Current view</div>',
        unsafe_allow_html=True,
    )

    if persona == "Business Head":

        st.markdown(
            """
            <div class="insight-card">

                <div class="section-title">
                    Executive view
                </div>

                <div class="insight-copy">
                    Focuses on business impact, key drivers,
                    recommended decisions and ownership.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="insight-card">

                <div class="section-title">
                    Analyst view
                </div>

                <div class="insight-copy">
                    Focuses on evidence, analytical methods,
                    uncertainty and source lineage.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown(
        '<div class="section-label">Guardrails</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="insight-card">

            <div class="insight-copy"
                 style="margin-top:0;">

                InsightX is a decision-support system.
                It should avoid strong conclusions when:

                <br><br>

                • evidence is incomplete<br>
                • sources disagree<br>
                • historical data is insufficient<br>
                • relationships only show correlation

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="section-label">Feedback history</div>',
        unsafe_allow_html=True,
    )

    feedback = load_feedback()

    if feedback:

        st.dataframe(
            pd.DataFrame(feedback).tail(20),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.caption(
            "No feedback has been recorded yet."
        )


    st.markdown(
        '<div class="section-label">Runtime</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Runtime telemetry is retained for prototype monitoring."
    )