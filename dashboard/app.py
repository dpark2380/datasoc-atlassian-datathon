"""
Risk & playbook dashboard (workstream B) -- internal exploration tool. Export
charts from here into the deck; this app itself is never demoed live
(submission is deck/PDF only). The single-customer risk-scorer tool (live
demo, workstream C) is a separate app.

Run: .venv/bin/streamlit run dashboard/app.py

Reads analysis/customer_risk.csv and analysis/cleaned_tickets.csv, both
produced by analysis/eda.py. See docs/findings-data-quality.md and
docs/findings-additional-signals.md for why the two files are treated so
differently: usage/risk is real signal, tickets are descriptive-only.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RISK_CSV = Path(__file__).parent.parent / "analysis" / "customer_risk.csv"
TICKETS_CSV = Path(__file__).parent.parent / "analysis" / "cleaned_tickets.csv"
USAGE_CSV = Path(__file__).parent.parent / "references" / "Dataset" / "product_usage.csv"

PLAN_ORDER = ["Free", "Standard", "Premium", "Enterprise"]
CATEGORY_ORDER = ["Monitor Only", "New & Struggling", "Established & Declining", "High-Value Disengaged"]

st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")


@st.cache_data
def load_data():
    risk = pd.read_csv(RISK_CSV)
    risk["Plan Type"] = pd.Categorical(risk["Plan Type"], categories=PLAN_ORDER, ordered=True)
    risk["Risk Category"] = pd.Categorical(risk["Risk Category"], categories=CATEGORY_ORDER, ordered=True)
    tickets = pd.read_csv(TICKETS_CSV)
    usage = pd.read_csv(USAGE_CSV)
    return risk, tickets, usage


risk, tickets, usage = load_data()

st.title("Customer Risk & Playbook")
st.caption(
    "Internal analysis tool -- exports charts for the deck, not demoed live. "
    "See docs/findings-data-quality.md and docs/findings-additional-signals.md for the full data audit."
)

with st.sidebar:
    st.header("Filters")
    plans = st.multiselect("Plan Type", options=PLAN_ORDER, default=PLAN_ORDER)

filtered = risk[risk["Plan Type"].isin(plans)]
at_risk = filtered[filtered["At Risk"]]

# --- KPI row -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{len(filtered):,}")
col2.metric("At Risk", f"{filtered['At Risk'].sum():,}", f"{filtered['At Risk'].mean():.1%}")
col3.metric("Avg risk score (at-risk only)", f"{at_risk['Risk Score'].mean():.1f}" if len(at_risk) else "n/a")
col4.metric("Avg active days/month", f"{filtered['Active Days'].mean():.1f}")

st.divider()

# --- The headline finding --------------------------------------------------
st.subheader("Usage scales with plan tier (the real signal)")
st.caption("Active Days by Plan Type -- this is genuine, not a data artifact (see findings doc).")
means = risk.groupby("Plan Type", observed=True)["Active Days"].mean().reindex(PLAN_ORDER).reset_index()
fig = px.bar(means, x="Plan Type", y="Active Days")
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Risk category breakdown")
    st.caption("Monitor Only / New & Struggling / Established & Declining / High-Value Disengaged.")
    counts = filtered["Risk Category"].value_counts().reindex(CATEGORY_ORDER).reset_index()
    fig = px.bar(counts, x="Risk Category", y="count")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Usage by product")
    st.caption("Secondary real cut -- Jira/daily-use tools show higher engagement than Loom.")
    by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
    fig = px.bar(by_product, x="Product", y="Active Days")
    st.plotly_chart(fig, use_container_width=True)

# --- At-risk customer table with recommended action -----------------------
st.divider()
st.subheader("At-risk customers and recommended action (sample)")
st.dataframe(
    at_risk[
        ["Customer ID", "Plan Type", "Primary Product", "Risk Category", "Risk Score",
         "Active Days", "Embeddedness Percentile", "Recommended Action"]
    ].sort_values("Risk Score", ascending=False).head(50),
    use_container_width=True,
)

# --- Ticket data: descriptive only, clearly labeled ------------------------
st.divider()
st.subheader("Support ticket data (descriptive only -- not predictive)")
st.caption(
    "Ticket Type/Priority/Channel/Satisfaction are confirmed random in this dataset "
    "(near-zero spread across every field we tested -- see docs/findings-data-quality.md). "
    "These charts show raw operational volume, not a driver of risk."
)
c3, c4 = st.columns(2)
with c3:
    fig = px.bar(tickets["Ticket Type"].value_counts().reset_index(), x="Ticket Type", y="count")
    st.plotly_chart(fig, use_container_width=True)
with c4:
    fig = px.bar(tickets["Ticket Channel"].value_counts().reset_index(), x="Ticket Channel", y="count")
    st.plotly_chart(fig, use_container_width=True)
