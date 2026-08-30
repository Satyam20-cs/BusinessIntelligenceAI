import html
import textwrap

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


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="InsightX",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# HTML HELPERS
# IMPORTANT: use st.html instead of st.markdown for HTML
# =========================================================

def render_html(content):
    """Render HTML safely using Streamlit's native HTML renderer."""
    st.html(textwrap.dedent(content).strip())


# =========================================================
# GLOBAL CSS
# =========================================================

render_html(
    """
    <style>

    :root {
        --bg: #070a0f;
        --panel: #0c1118;
        --panel-2: #101720;
        --border: #1d2a38;
        --border-soft: #16212d;
        --text: #edf4fb;
        --muted: #7f91a5;
        --blue: #4da3ff;
        --blue-soft: #13283d;
        --green: #35d39a;
        --red: #ff5c63;
        --yellow: #f2bd55;
    }

    html {
        scroll-behavior: smooth;
    }

    body {
        background: var(--bg);
    }

    .stApp {
        background:
            radial-gradient(
                circle at 80% -10%,
                rgba(44, 122, 255, 0.08),
                transparent 28%
            ),
            var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2.2rem;
        padding-bottom: 6rem;
    }

    section[data-testid="stSidebar"] {
        background: #080c12;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.5rem 1.1rem 2rem 1.1rem;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text);
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }

    .brand-wrap {
        padding: 0.3rem 0.15rem 1.25rem 0.15rem;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 9px;
    }

    .brand-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--blue);
        box-shadow: 0 0 0 4px rgba(77,163,255,0.10);
    }

    .brand {
        font-size: 18px;
        font-weight: 750;
        letter-spacing: -0.5px;
    }

    .brand-subtitle {
        margin-top: 7px;
        color: var(--muted);
        font-size: 11px;
    }

    .sidebar-label {
        margin: 1.25rem 0 0.55rem;
        color: #71869c;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .sidebar-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 13px;
        margin-top: 10px;
    }

    .sidebar-card-title {
        font-size: 12px;
        font-weight: 650;
        color: var(--text);
    }

    .sidebar-card-copy {
        margin-top: 5px;
        color: var(--muted);
        font-size: 10px;
        line-height: 1.5;
    }

    .data-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        margin-right: 6px;
        border-radius: 50%;
        background: var(--green);
    }

    .page-kicker {
        color: #5e86ad;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .page-title {
        color: var(--text);
        font-size: 32px;
        line-height: 1.1;
        font-weight: 760;
        letter-spacing: -1.1px;
        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
        margin-top: 8px;
    }

    .topbar {
        padding-bottom: 1.4rem;
        margin-bottom: 1.7rem;
        border-bottom: 1px solid var(--border);
    }

    .period-pill {
        display: inline-flex;
        align-items: center;
        margin-top: 13px;
        padding: 6px 10px;
        border: 1px solid var(--border);
        border-radius: 7px;
        background: #0b1118;
        color: #87a3bd;
        font-size: 10px;
    }

    .section-label {
        margin-top: 1.7rem;
        margin-bottom: 0.7rem;
        color: #5d85ae;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .section-title {
        color: var(--text);
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .section-description {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background: linear-gradient(
            180deg,
            rgba(14,21,30,0.98),
            rgba(10,15,22,0.98)
        );
        border: 1px solid var(--border);
        border-radius: 11px;
        padding: 17px;
        min-height: 112px;
        box-sizing: border-box;
        transition:
            transform 160ms ease,
            border-color 160ms ease,
            background 160ms ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #29445e;
        background: #0e151e;
    }

    .kpi-name {
        color: #7890a7;
        font-size: 10px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .kpi-value {
        color: #f1f7fd;
        font-size: 24px;
        font-weight: 760;
        letter-spacing: -0.7px;
    }

    .kpi-change-negative,
    .kpi-change-positive,
    .kpi-change-neutral {
        margin-top: 7px;
        font-size: 10px;
        font-weight: 650;
    }

    .kpi-change-negative {
        color: var(--red);
    }

    .kpi-change-positive {
        color: var(--green);
    }

    .kpi-change-neutral {
        color: var(--muted);
    }

    .signal-card {
        background:
            linear-gradient(
                135deg,
                rgba(22, 53, 83, 0.65),
                rgba(10, 16, 24, 0.98) 55%
            );
        border: 1px solid #214564;
        border-radius: 12px;
        padding: 24px;
        min-height: 190px;
        box-sizing: border-box;
    }

    .signal-status {
        color: var(--blue);
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .signal-title {
        color: var(--text);
        font-size: 25px;
        line-height: 1.25;
        font-weight: 740;
        letter-spacing: -0.7px;
    }

    .signal-copy {
        color: #91a4b7;
        font-size: 13px;
        line-height: 1.65;
        margin-top: 11px;
    }

    .signal-copy strong {
        color: #dce8f3;
    }

    .confidence-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        min-height: 190px;
        box-sizing: border-box;
    }

    .confidence-label {
        color: #7890a7;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .confidence-value {
        margin-top: 12px;
        color: var(--text);
        font-size: 35px;
        font-weight: 760;
        letter-spacing: -1px;
    }

    .confidence-status {
        display: inline-block;
        margin-top: 10px;
        padding: 5px 8px;
        border-radius: 6px;
        background: #102336;
        color: #76b8f5;
        font-size: 10px;
        font-weight: 700;
    }

    .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        box-sizing: border-box;
    }

    .driver-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 15px;
        min-height: 125px;
        box-sizing: border-box;
    }

    .driver-label {
        color: #6287a9;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .driver-name {
        color: var(--text);
        font-size: 17px;
        font-weight: 700;
        margin-top: 9px;
    }

    .driver-value {
        color: #c8d7e6;
        font-size: 13px;
        margin-top: 6px;
    }

    .driver-share {
        color: var(--muted);
        font-size: 10px;
        margin-top: 7px;
    }

    .action-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-left: 2px solid var(--blue);
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 9px;
        box-sizing: border-box;
        transition:
            border-color 160ms ease,
            transform 160ms ease;
    }

    .action-card:hover {
        transform: translateX(2px);
        border-color: #31516d;
    }

    .action-priority {
        color: #6192bd;
        font-size: 9px;
        font-weight: 750;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .action-title {
        color: var(--text);
        font-size: 16px;
        font-weight: 700;
        margin-top: 7px;
    }

    .action-meta {
        color: var(--muted);
        font-size: 11px;
        line-height: 1.7;
        margin-top: 8px;
    }

    .notice {
        background: #0d1715;
        border: 1px solid #1c4a3c;
        border-radius: 9px;
        padding: 13px 15px;
        color: #67d6ae;
        font-size: 11px;
        line-height: 1.5;
    }

    .warning {
        background: #19150e;
        border: 1px solid #4a3818;
        border-radius: 9px;
        padding: 13px 15px;
        color: #e5bb66;
        font-size: 11px;
        line-height: 1.5;
    }

    .section-nav {
        display: flex;
        gap: 18px;
        padding: 8px 0 15px;
        margin-bottom: 4px;
        border-bottom: 1px solid var(--border-soft);
    }

    .section-nav a {
        color: #71869a;
        text-decoration: none;
        font-size: 10px;
        font-weight: 600;
    }

    .section-nav a:hover {
        color: var(--blue);
    }

    .stButton > button {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: #0d141c;
        color: #cbd9e7;
        font-size: 11px;
        font-weight: 650;
        min-height: 36px;
        transition: all 150ms ease;
    }

    .stButton > button:hover {
        border-color: #326087;
        background: #101c28;
        color: #ffffff;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }

    .js-plotly-plot {
        border: 1px solid var(--border);
        border-radius: 11px;
        overflow: hidden;
        background: var(--panel);
    }

    div[data-baseweb="select"] > div {
        background: #0d141c;
        border-color: var(--border);
        border-radius: 8px;
    }

    div[data-baseweb="select"] * {
        color: #dce7f1;
    }

    textarea {
        background: #0c131b !important;
        color: #e5eef7 !important;
        border-color: var(--border) !important;
    }

    div[data-testid="stRadio"] label {
        color: #b6c6d5;
    }

    div[data-testid="stRadio"] label:hover {
        color: #ffffff;
    }

    .stCaption {
        color: var(--muted);
    }

    footer {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    </style>
    """
)


# =========================================================
# DATA
# =========================================================

@st.cache_data
def get_data():
    return load_all()


data = get_data()

sales = data["sales"]
inventory = data["inventory"]
customer = data["customer"]
feedback_text = data["feedback_text"]


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    render_html(
        """
        <div class="brand-wrap">
            <div class="brand-row">
                <span class="brand-dot"></span>
                <span class="brand">InsightX</span>
            </div>

            <div class="brand-subtitle">
                Business decision intelligence
            </div>
        </div>
        """
    )

    render_html(
        '<div class="sidebar-label">Workspace</div>'
    )

    page = st.radio(
        "Workspace",
        [
            "Overview",
            "Investigation",
            "Evidence",
            "Actions",
            "Governance",
        ],
        label_visibility="collapsed",
    )

    render_html(
        '<div class="sidebar-label">View</div>'
    )

    persona = st.selectbox(
        "View",
        [
            "Business Head",
            "Business Analyst",
        ],
        label_visibility="collapsed",
    )

    render_html(
        '<div class="sidebar-label">Scenario</div>'
    )

    scenario = st.selectbox(
        "Scenario",
        [
            "normal",
            "low_confidence",
            "sparse_history",
        ],
        format_func=lambda x: {
            "normal": "Normal",
            "low_confidence": "Low confidence",
            "sparse_history": "Sparse history",
        }[x],
        label_visibility="collapsed",
    )

    render_html(
        '<div class="sidebar-label">Analysis window</div>'
    )

    analysis_days = st.slider(
        "Days",
        min_value=7,
        max_value=21,
        value=21,
        step=7,
        label_visibility="collapsed",
    )

    render_html(
        '<div class="sidebar-label">Data</div>'
    )

    render_html(
        """
        <div class="sidebar-card">

            <div class="sidebar-card-title">
                <span class="data-dot"></span>
                Demo dataset
            </div>

            <div class="sidebar-card-copy">
                Sales · Inventory · Customer · Feedback
            </div>

        </div>
        """
    )

    render_html(
        f"""
        <div class="sidebar-card">

            <div class="sidebar-card-title">
                Analysis ready
            </div>

            <div class="sidebar-card-copy">
                {len(sales):,} sales records ·
                {len(inventory):,} inventory records
            </div>

        </div>
        """
    )

    render_html(
        '<div style="height:20px;"></div>'
    )

    st.caption(
        "InsightX prototype · synthetic retail data"
    )


# =========================================================
# ANALYTICS
# =========================================================

kpi_df = calculate_kpis(
    sales,
    customer,
    days=analysis_days,
)

comparison = compare_kpis(kpi_df)

driver_pack = build_revenue_driver_pack(
    sales,
    inventory,
    customer,
    days=analysis_days,
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
    conf = max(
        0.80,
        base_conf,
    )


conf_label = label(conf)

revenue = comparison["Revenue"]

severity = classify_change(
    revenue["change_pct"]
)


# =========================================================
# HELPERS
# =========================================================

def money(value):
    return f"₹{value / 1e7:.2f} Cr"


def change_class(value):

    if value < 0:
        return "negative"

    if value > 0:
        return "positive"

    return "neutral"


def render_header(title, subtitle):

    render_html(
        f"""
        <div class="topbar">

            <div class="page-kicker">
                InsightX
            </div>

            <div class="page-title">
                {html.escape(title)}
            </div>

            <div class="page-subtitle">
                {html.escape(subtitle)}
            </div>

            <div class="period-pill">
                Last {analysis_days} days · Demo dataset
            </div>

        </div>
        """
    )


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

    if change < 0:
        arrow = "↓"

    elif change > 0:
        arrow = "↑"

    else:
        arrow = "—"

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-name">
                {html.escape(str(name))}
            </div>

            <div class="kpi-value">
                {value}
            </div>

            <div class="kpi-change-{css_class}">
                {arrow} {abs(change):.1f}% vs previous period
            </div>

        </div>
        """
    )


def render_action(action):

    priority = html.escape(
        str(action.get("priority", ""))
    )

    title = html.escape(
        str(action.get("action", ""))
    )

    driver = html.escape(
        str(action.get("driver", ""))
    )

    lever = html.escape(
        str(action.get("lever", ""))
    )

    owner = html.escape(
        str(action.get("owner", ""))
    )

    impact = html.escape(
        str(action.get("expected_impact", ""))
    )

    monitoring = html.escape(
        str(action.get("monitoring", ""))
    )

    render_html(
        f"""
        <div class="action-card">

            <div class="action-priority">
                {priority}
            </div>

            <div class="action-title">
                {title}
            </div>

            <div class="action-meta">
                Driver · {driver}<br>
                Lever · {lever}<br>
                Owner · {owner}<br>
                Expected impact · {impact}<br>
                Monitoring · {monitoring}
            </div>

        </div>
        """
    )


def plot_layout(fig, height=320):

    fig.update_layout(
        height=height,
        margin=dict(
            l=12,
            r=12,
            t=15,
            b=15,
        ),
        paper_bgcolor="#0c1118",
        plot_bgcolor="#0c1118",
        font=dict(
            family="Inter, Arial, sans-serif",
            size=11,
            color="#7f91a5",
        ),
        showlegend=False,
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#1d2a38",
        tickfont=dict(
            color="#667b90"
        ),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#18232f",
        zeroline=False,
        tickfont=dict(
            color="#667b90"
        ),
    )

    return fig


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    render_header(
        "Business overview",
        "Current performance and the changes that need attention.",
    )

    render_html(
        '<div class="section-label">Performance</div>'
    )

    cols = st.columns(
        len(comparison)
    )

    for col, (name, item) in zip(
        cols,
        comparison.items(),
    ):

        with col:
            render_kpi(
                name,
                item,
            )

    render_html(
        """
        <div class="section-nav">
            <a href="#trend">Trend</a>
            <a href="#signal">Signal</a>
            <a href="#contributors">Contributors</a>
        </div>
        """
    )

    render_html(
        '<div id="trend"></div>'
    )

    render_html(
        '<div class="section-label">Trend</div>'
    )

    render_html(
        '<div class="section-title">Revenue</div>'
    )

    render_html(
        """
        <div class="section-description">
            Daily revenue over the available period.
        </div>
        """
    )

    daily = (
        sales.groupby(
            "date",
            as_index=False,
        )["revenue"]
        .sum()
        .sort_values("date")
    )

    daily["date"] = pd.to_datetime(
        daily["date"]
    )

    fig = px.line(
        daily,
        x="date",
        y="revenue",
    )

    fig.update_traces(
        line=dict(
            color="#4da3ff",
            width=2.2,
        ),
        hovertemplate="₹%{y:,.0f}<extra></extra>",
    )

    fig = plot_layout(
        fig,
        height=330,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )

    render_html(
        '<div id="signal"></div>'
    )

    render_html(
        '<div class="section-label">Signal</div>'
    )

    left, right = st.columns(
        [2.1, 1],
        gap="large",
    )

    with left:

        direction = (
            "down"
            if revenue["change_pct"] < 0
            else "up"
        )

        render_html(
            f"""
            <div class="signal-card">

                <div class="signal-status">
                    {html.escape(str(severity))}
                </div>

                <div class="signal-title">
                    Revenue is {direction}
                    {abs(revenue["change_pct"]):.1f}%
                </div>

                <div class="signal-copy">
                    {money(revenue["previous"])}
                    →
                    {money(revenue["current"])}
                    across equal {analysis_days}-day periods.
                </div>

            </div>
            """
        )

    with right:

        render_html(
            f"""
            <div class="confidence-card">

                <div class="confidence-label">
                    Confidence
                </div>

                <div class="confidence-value">
                    {conf:.0%}
                </div>

                <div class="confidence-status">
                    {html.escape(str(conf_label).upper())}
                </div>

            </div>
            """
        )

    render_html(
        '<div id="contributors"></div>'
    )

    render_html(
        '<div class="section-label">Contributors</div>'
    )

    region_df = driver_pack["regions"].copy()

    if not region_df.empty:

        region_cards = region_df.head(4)

        columns = st.columns(
            min(4, len(region_cards))
        )

        for col, (_, row) in zip(
            columns,
            region_cards.iterrows(),
        ):

            with col:

                render_html(
                    f"""
                    <div class="driver-card">

                        <div class="driver-label">
                            Region
                        </div>

                        <div class="driver-name">
                            {html.escape(str(row["region"]))}
                        </div>

                        <div class="driver-value">
                            {money(row["delta"])}
                        </div>

                        <div class="driver-share">
                            {row["contribution_pct"]:.1f}%
                            of negative movement
                        </div>

                    </div>
                    """
                )


# =========================================================
# INVESTIGATION
# =========================================================

elif page == "Investigation":

    render_header(
        "Revenue investigation",
        "Trace the movement from signal to contributing evidence and action.",
    )

    render_html(
        """
        <div class="section-nav">
            <a href="#signal">01 Signal</a>
            <a href="#drivers">02 Drivers</a>
            <a href="#connections">03 Connections</a>
            <a href="#recommendation">04 Action</a>
        </div>
        """
    )

    # -----------------------------------------------------
    # SIGNAL
    # -----------------------------------------------------

    render_html(
        '<div id="signal"></div>'
    )

    render_html(
        '<div class="section-label">01 · Signal</div>'
    )

    direction = (
        "down"
        if revenue["change_pct"] < 0
        else "up"
    )

    render_html(
        f"""
        <div class="signal-card">

            <div class="signal-status">
                Revenue movement ·
                {html.escape(str(severity))}
            </div>

            <div class="signal-title">
                Revenue is {direction}
                {abs(revenue["change_pct"]):.1f}%
            </div>

            <div class="signal-copy">
                Current period:
                <strong>{money(revenue["current"])}</strong>
                &nbsp;·&nbsp;
                Previous period:
                <strong>{money(revenue["previous"])}</strong>
            </div>

        </div>
        """
    )

    # -----------------------------------------------------
    # DRIVERS
    # -----------------------------------------------------

    render_html(
        '<div id="drivers"></div>'
    )

    render_html(
        '<div class="section-label">02 · Drivers</div>'
    )

    top_region = driver_pack["regions"].head(3)
    top_product = driver_pack["products"].head(3)

    d1, d2 = st.columns(
        2,
        gap="large",
    )

    with d1:

        render_html(
            '<div class="section-title">Regional contribution</div>'
        )

        if not top_region.empty:

            for _, row in top_region.iterrows():

                render_html(
                    f"""
                    <div class="driver-card"
                         style="margin-bottom:8px;">

                        <div class="driver-label">
                            Region
                        </div>

                        <div class="driver-name">
                            {html.escape(str(row["region"]))}
                        </div>

                        <div class="driver-value">
                            {money(row["delta"])}
                        </div>

                        <div class="driver-share">
                            {row["contribution_pct"]:.1f}%
                            of negative movement
                        </div>

                    </div>
                    """
                )

        else:

            st.caption(
                "No regional driver data available."
            )

    with d2:

        render_html(
            '<div class="section-title">Product contribution</div>'
        )

        if not top_product.empty:

            for _, row in top_product.iterrows():

                render_html(
                    f"""
                    <div class="driver-card"
                         style="margin-bottom:8px;">

                        <div class="driver-label">
                            Product
                        </div>

                        <div class="driver-name">
                            {html.escape(str(row["product"]))}
                        </div>

                        <div class="driver-value">
                            {money(row["delta"])}
                        </div>

                        <div class="driver-share">
                            {row["contribution_pct"]:.1f}%
                            of negative movement
                        </div>

                    </div>
                    """
                )

        else:

            st.caption(
                "No product driver data available."
            )

    # -----------------------------------------------------
    # CONNECTIONS
    # -----------------------------------------------------

    render_html(
        '<div id="connections"></div>'
    )

    render_html(
        '<div class="section-label">03 · Connections</div>'
    )

    c1, c2 = st.columns(
        2,
        gap="large",
    )

    with c1:

        inv = driver_pack["inventory"]

        inventory_change = inv.get(
            "change_pct",
            0,
        )

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Inventory stockouts
                </div>

                <div class="kpi-value">
                    {inv.get("current", 0):,.0f}
                </div>

                <div class="kpi-change-negative">
                    ↑ {abs(inventory_change):.1f}%
                </div>

            </div>
            """
        )

    with c2:

        comp = driver_pack["complaints"]

        complaints_current = comp.get(
            "current",
            0,
        )

        complaints_change = comp.get(
            "change_pct",
            0,
        )

        complaint_css = change_class(
            complaints_change
        )

        if complaints_change < 0:
            complaint_arrow = "↓"

        elif complaints_change > 0:
            complaint_arrow = "↑"

        else:
            complaint_arrow = "—"

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Customer complaints
                </div>

                <div class="kpi-value">
                    {complaints_current:,.0f}
                </div>

                <div class="kpi-change-{complaint_css}">
                    {complaint_arrow}
                    {abs(complaints_change):.1f}%
                    vs previous period
                </div>

            </div>
            """
        )

    # -----------------------------------------------------
    # CUSTOMER SIGNALS
    # -----------------------------------------------------

    if not theme_summary.empty:

        render_html(
            """
            <div class="section-title"
                 style="margin-top:22px;">
                Customer signals
            </div>
            """
        )

        st.dataframe(
            theme_summary.head(6),
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------
    # STATISTICAL SIGNALS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SCENARIO WARNINGS
    # -----------------------------------------------------

    if scenario == "low_confidence":

        render_html(
            """
            <div class="warning">
                Evidence is incomplete. InsightX will not make a
                definitive inventory attribution.
            </div>
            """
        )

    elif scenario == "sparse_history":

        render_html(
            """
            <div class="warning">
                Historical evidence is limited. InsightX will not
                make a strong trend claim for the selected scenario.
            </div>
            """
        )

    # -----------------------------------------------------
    # AI NARRATIVE
    # -----------------------------------------------------

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

    safe_narrative = (
        html.escape(str(narrative))
        .replace("\n", "<br>")
    )

    render_html(
        '<div class="section-label">Interpretation</div>'
    )

    render_html(
        f"""
        <div class="card">

            <div class="signal-copy"
                 style="margin-top:0;color:#b9c8d7;">

                {safe_narrative}

            </div>

        </div>
        """
    )

    # -----------------------------------------------------
    # RECOMMENDED ACTION
    # -----------------------------------------------------

    render_html(
        '<div id="recommendation"></div>'
    )

    render_html(
        '<div class="section-label">04 · Recommended action</div>'
    )

    actions = recommend_actions(
        driver_pack,
        conf,
    )

    for action in actions[:3]:
        render_action(action)

    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    render_html(
        '<div class="section-label">Feedback</div>'
    )

    f1, f2 = st.columns(2)

    with f1:

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

    with f2:

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


# =========================================================
# EVIDENCE
# =========================================================

elif page == "Evidence":

    render_header(
        "Evidence",
        "Trace the insight back to the sources used by the analysis.",
    )

    render_html(
        '<div class="section-label">Source coverage</div>'
    )

    st.dataframe(
        recon["sources"],
        use_container_width=True,
        hide_index=True,
    )

    overlap = recon["dimension_overlap"]

    c1, c2 = st.columns(2)

    with c1:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Sales ↔ Inventory overlap
                </div>

                <div class="kpi-value">
                    {overlap["sales_inventory_pct"]:.1f}%
                </div>

            </div>
            """
        )

    with c2:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-name">
                    Sales ↔ Customer overlap
                </div>

                <div class="kpi-value">
                    {overlap["sales_customer_pct"]:.1f}%
                </div>

            </div>
            """
        )

    render_html(
        '<div class="section-label">Lineage</div>'
    )

    lineage = pd.DataFrame(
        lineage_rows()
    )

    st.dataframe(
        lineage,
        use_container_width=True,
        hide_index=True,
    )

    render_html(
        '<div class="section-label">System boundary</div>'
    )

    render_html(
        """
        <div class="card">

            <div class="section-title">
                Analytics first. Language second.
            </div>

            <div class="signal-copy">

                KPI calculations, comparisons, materiality,
                driver analysis, reconciliation and confidence
                are handled by deterministic analytics.

                <br><br>

                The language layer turns verified results into
                a concise business explanation.

                <br><br>

                <strong>
                    The language model is not the source of truth.
                </strong>

            </div>

        </div>
        """
    )


# =========================================================
# ACTIONS
# =========================================================

elif page == "Actions":

    render_header(
        "Recommended actions",
        "Prioritized next steps based on the available evidence.",
    )

    actions = recommend_actions(
        driver_pack,
        conf,
    )

    if conf < 0.55:

        render_html(
            """
            <div class="warning">

                Confidence is low. The recommended action is
                validation rather than an aggressive intervention.

            </div>
            """
        )

    for action in actions:
        render_action(action)


# =========================================================
# GOVERNANCE
# =========================================================

elif page == "Governance":

    render_header(
        "Governance",
        "Confidence, feedback and the boundary between analytics and generation.",
    )

    render_html(
        '<div class="section-label">Current view</div>'
    )

    if persona == "Business Head":

        render_html(
            """
            <div class="card">

                <div class="section-title">
                    Executive view
                </div>

                <div class="signal-copy">

                    Focuses on business impact, key contributors,
                    recommended decisions and ownership.

                </div>

            </div>
            """
        )

    else:

        render_html(
            """
            <div class="card">

                <div class="section-title">
                    Analyst view
                </div>

                <div class="signal-copy">

                    Focuses on evidence, analytical method,
                    uncertainty and source lineage.

                </div>

            </div>
            """
        )

    render_html(
        '<div class="section-label">Confidence</div>'
    )

    render_html(
        f"""
        <div class="confidence-card">

            <div class="confidence-label">
                Current confidence
            </div>

            <div class="confidence-value">
                {conf:.0%}
            </div>

            <div class="confidence-status">
                {html.escape(str(conf_label).upper())}
            </div>

        </div>
        """
    )

    render_html(
        '<div class="section-label">Guardrails</div>'
    )

    render_html(
        """
        <div class="notice">

            InsightX supports decisions; it does not make decisions.

            When evidence is incomplete, contradictory or sparse,
            confidence should decrease and strong attribution should
            be avoided.

        </div>
        """
    )

    render_html(
        '<div class="section-label">Feedback history</div>'
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

    render_html(
        '<div class="section-label">Runtime</div>'
    )

    st.caption(
        "InsightX prototype runtime · deterministic analytics + optional narrative generation."
    )