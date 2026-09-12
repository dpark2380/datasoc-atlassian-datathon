"""
Results dashboard: everything from the analysis in one place. Export
charts from here into the deck; this app itself is never demoed live
(submission is deck/PDF only). The single-customer risk-scorer tool (live
demo, workstream C) is a separate app.

Run: .venv/bin/streamlit run dashboard/app.py

Reads analysis/customer_risk.csv and analysis/cleaned_tickets.csv, both
produced by analysis/eda.py, plus the docs/ findings for the Documentation
tab. Run analysis/eda.py and analysis/sensitivity_checks.py first if these
don't exist yet.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import sensitivity_checks  # noqa: E402

RISK_CSV = ROOT / "analysis" / "customer_risk.csv"
TICKETS_CSV = ROOT / "analysis" / "cleaned_tickets.csv"
USAGE_CSV = ROOT / "references" / "Dataset" / "product_usage.csv"
DOCS_DIR = ROOT / "docs"

PLAN_ORDER = ["Free", "Standard", "Premium", "Enterprise"]
CATEGORY_ORDER = ["Monitor Only", "New & Struggling", "Established & Declining", "High-Value Disengaged"]

DOC_FILES = {
    "Findings summary (start here)": "findings-summary.md",
    "Build plan: what and why": "build-plan.md",
    "Data quality audit": "findings-data-quality.md",
    "Additional signal check": "findings-additional-signals.md",
    "ML segments (clustering + anomaly detection)": "findings-ml-segments.md",
    "Sensitivity and robustness checks": "findings-sensitivity.md",
    "Customer success playbook research": "research-cs-playbook-actions.md",
    "Deck outline": "deck-outline.md",
}

st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")


@st.cache_data
def load_data():
    risk = pd.read_csv(RISK_CSV)
    risk["Plan Type"] = pd.Categorical(risk["Plan Type"], categories=PLAN_ORDER, ordered=True)
    risk["Risk Category"] = pd.Categorical(risk["Risk Category"], categories=CATEGORY_ORDER, ordered=True)
    tickets = pd.read_csv(TICKETS_CSV)
    usage = pd.read_csv(USAGE_CSV)
    return risk, tickets, usage


@st.cache_data
def load_sensitivity_results(_risk: pd.DataFrame):
    return {
        "cutoff": sensitivity_checks.cutoff_sensitivity(_risk),
        "embeddedness": sensitivity_checks.embeddedness_weight_sensitivity(_risk),
        "urgency": sensitivity_checks.urgency_coefficient_sensitivity(_risk),
        "bootstrap": sensitivity_checks.bootstrap_flag_stability(_risk),
    }


risk, tickets, usage = load_data()

st.title("Customer Risk & Playbook")
st.caption(
    "Internal analysis tool: exports charts for the deck, not demoed live. "
    "Everything here, including prior analyses, is one click away in the Documentation tab."
)

with st.sidebar:
    st.header("Filters")
    st.caption("Applies to the Risk Model and Usage Segments tabs.")
    plans = st.multiselect("Plan Type", options=PLAN_ORDER, default=PLAN_ORDER)

filtered = risk[risk["Plan Type"].isin(plans)]
at_risk = filtered[filtered["At Risk"]]

tab_overview, tab_risk, tab_segments, tab_robustness, tab_tickets, tab_docs = st.tabs(
    ["Overview", "Risk model", "Usage segments (ML)", "Robustness checks", "Ticket data audit", "Documentation"]
)

# --- Overview --------------------------------------------------------------
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customers", f"{len(filtered):,}")
    col2.metric("At Risk", f"{filtered['At Risk'].sum():,}", f"{filtered['At Risk'].mean():.1%}")
    col3.metric("Avg risk score (at-risk only)", f"{at_risk['Risk Score'].mean():.1f}" if len(at_risk) else "n/a")
    col4.metric("Avg active days/month", f"{filtered['Active Days'].mean():.1f}")

    st.subheader("The story in one paragraph")
    st.markdown(
        "Support ticket fields in this dataset are statistically random; there's no free text to score "
        "sentiment from either. Usage data is real: it's stable per customer over time and scales cleanly "
        "with plan tier and product. The risk model flags a customer as at risk when their usage sits in the "
        "bottom quarter compared to peers on the same plan and product, scores them 0-100, and assigns one of "
        "four playbook categories. See the Documentation tab for the full findings and sources."
    )

# --- Risk model --------------------------------------------------------------
with tab_risk:
    st.subheader("Usage scales with plan tier (the real signal)")
    st.caption("Active Days by Plan Type. This is genuine, not a data artifact (see Documentation tab).")
    means = risk.groupby("Plan Type", observed=True)["Active Days"].mean().reindex(PLAN_ORDER).reset_index()
    fig = px.bar(means, x="Plan Type", y="Active Days")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Risk category breakdown")
        counts = filtered["Risk Category"].value_counts().reindex(CATEGORY_ORDER).reset_index()
        fig = px.bar(counts, x="Risk Category", y="count")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Usage by product")
        st.caption("Secondary real cut: Jira and other daily-use tools show higher engagement than Loom.")
        by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
        fig = px.bar(by_product, x="Product", y="Active Days")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("At-risk customers and recommended action (sample)")
    st.dataframe(
        at_risk[
            ["Customer ID", "Plan Type", "Primary Product", "Risk Category", "Risk Score",
             "Active Days", "Embeddedness Percentile", "Recommended Action"]
        ].sort_values("Risk Score", ascending=False).head(50),
        use_container_width=True,
    )

# --- Usage segments (ML) -----------------------------------------------------
with tab_segments:
    st.subheader("Usage segments (unsupervised, independent of the Risk Score)")
    st.caption(
        "KMeans on standardised usage metrics, discovered from the data rather than hand-picked. "
        "See the ML segments doc for why k=4 was chosen over the higher-silhouette k=2."
    )
    c5, c6 = st.columns(2)
    with c5:
        cluster_counts = filtered["Usage Cluster"].value_counts().reset_index()
        fig = px.bar(cluster_counts, x="Usage Cluster", y="count")
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        st.caption("Usage anomalies (Isolation Forest, 5% contamination) vs. the At Risk flag:")
        anomaly_overlap = filtered.groupby("Usage Anomaly")["At Risk"].mean().reset_index()
        anomaly_overlap["Usage Anomaly"] = anomaly_overlap["Usage Anomaly"].map({True: "Anomaly", False: "Not anomaly"})
        fig = px.bar(anomaly_overlap, x="Usage Anomaly", y="At Risk", labels={"At Risk": "Share also At Risk"})
        st.plotly_chart(fig, use_container_width=True)

# --- Robustness checks -------------------------------------------------------
with tab_robustness:
    st.subheader("Does the exact parameter choice matter?")
    st.caption(
        "The Risk Score's parameters (25% cutoff, 2x Integrations weight, 0.3 urgency coefficient) were chosen "
        "by judgment, since there's no churn label to fit them against. These checks show whether a reasonable "
        "alternative choice would flag a very different set of customers, or just fine-tune the result."
    )
    results = load_sensitivity_results(risk)

    st.markdown("**At Risk cutoff.** Tier mix of who's flagged, across cutoffs from 15% to 35%:")
    st.dataframe(results["cutoff"], use_container_width=True)

    st.markdown("**Embeddedness weight.** Rank correlation and category-flip rate, across Integrations Used weights from 1x to 5x:")
    st.dataframe(results["embeddedness"], use_container_width=True)

    st.markdown("**Urgency coefficient.** Risk Score rank correlation across coefficients from 0.2 to 0.5 (Risk Category doesn't depend on this at all):")
    st.dataframe(results["urgency"], use_container_width=True)

    st.metric("Bootstrap At-Risk flag stability", f"{results['bootstrap']:.1%}", "average agreement across 20 resamples")

# --- Ticket data audit --------------------------------------------------------
with tab_tickets:
    st.subheader("Support ticket data (descriptive only, not predictive)")
    st.caption(
        "Ticket Type, Priority, Channel, and Satisfaction are confirmed random in this dataset "
        "(near-zero spread across every field we tested; see the data quality audit doc). "
        "These charts show raw operational volume, not a driver of risk."
    )
    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(tickets["Ticket Type"].value_counts().reset_index(), x="Ticket Type", y="count")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.bar(tickets["Ticket Channel"].value_counts().reset_index(), x="Ticket Channel", y="count")
        st.plotly_chart(fig, use_container_width=True)

# --- Documentation -----------------------------------------------------------
with tab_docs:
    st.caption("Every finding behind this dashboard, in one place.")
    choice = st.selectbox("Choose a document", list(DOC_FILES))
    doc_path = DOCS_DIR / DOC_FILES[choice]
    if doc_path.exists():
        st.markdown(doc_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"{doc_path} not found yet.")
