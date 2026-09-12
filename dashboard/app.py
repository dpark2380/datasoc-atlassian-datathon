"""
EDA dashboard (workstream B) -- internal exploration tool. Export charts
from here into the deck; this app itself is never demoed live (submission
is deck/PDF only).

Run: .venv/bin/streamlit run dashboard/app.py

Reads analysis/customer_engagement.csv and analysis/cleaned_tickets.csv,
both produced by analysis/eda.py. See docs/findings-data-quality.md for why
the two files are treated so differently: engagement is real signal,
tickets are descriptive-only.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ENGAGEMENT_CSV = Path(__file__).parent.parent / "analysis" / "customer_engagement.csv"
TICKETS_CSV = Path(__file__).parent.parent / "analysis" / "cleaned_tickets.csv"
USAGE_CSV = Path(__file__).parent.parent / "references" / "Dataset" / "product_usage.csv"

PLAN_ORDER = ["Free", "Standard", "Premium", "Enterprise"]

st.set_page_config(page_title="Customer Engagement & Risk", layout="wide")


@st.cache_data
def load_data():
    engagement = pd.read_csv(ENGAGEMENT_CSV)
    engagement["Plan Type"] = pd.Categorical(engagement["Plan Type"], categories=PLAN_ORDER, ordered=True)
    tickets = pd.read_csv(TICKETS_CSV)
    usage = pd.read_csv(USAGE_CSV)
    return engagement, tickets, usage


engagement, tickets, usage = load_data()

st.title("Customer Engagement & Risk")
st.caption(
    "Internal analysis tool -- exports charts for the deck, not demoed live. "
    "See docs/findings-data-quality.md for the full data audit."
)

with st.sidebar:
    st.header("Filters")
    plans = st.multiselect("Plan Type", options=PLAN_ORDER, default=PLAN_ORDER)

filtered = engagement[engagement["Plan Type"].isin(plans)]

# --- KPI row -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{len(filtered):,}")
col2.metric("Underengaged", f"{filtered['Underengaged'].sum():,}", f"{filtered['Underengaged'].mean():.1%}")
col3.metric("Avg active days/month", f"{filtered['Active Days'].mean():.1f}")
col4.metric("Avg sessions/month", f"{filtered['Sessions'].mean():.1f}")

st.divider()

# --- The headline finding --------------------------------------------------
st.subheader("Usage scales with plan tier (the real signal)")
st.caption("Active Days by Plan Type -- this is genuine, not a data artifact (see findings doc).")
means = engagement.groupby("Plan Type", observed=True)["Active Days"].mean().reindex(PLAN_ORDER).reset_index()
fig = px.bar(means, x="Plan Type", y="Active Days")
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Underengaged customers by plan")
    st.caption("Bottom 25% of Active Days within each customer's own plan tier.")
    under = filtered.groupby("Plan Type", observed=True)["Underengaged"].agg(["sum", "mean"]).reindex(PLAN_ORDER).reset_index()
    fig = px.bar(under, x="Plan Type", y="sum", labels={"sum": "Underengaged customers"})
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Usage by product")
    st.caption("Secondary real cut -- Jira/daily-use tools show higher engagement than Loom.")
    by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
    fig = px.bar(by_product, x="Product", y="Active Days")
    st.plotly_chart(fig, use_container_width=True)

# --- Underengaged customer table -----------------------------------------
st.divider()
st.subheader("Underengaged customers (sample)")
st.dataframe(
    filtered[filtered["Underengaged"]][
        ["Customer ID", "Plan Type", "Industry", "Region", "Company Size", "Active Days", "Sessions", "Ticket Count"]
    ].head(50),
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
