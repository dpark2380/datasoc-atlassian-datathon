"""
Risk scorer page: single-customer lookup, the live-demo tool (workstream C).

Not part of the graded submission (the brief is deck/PDF only), but ready
to demo live in the 8-minute slot if this reaches heats. Unlike the
Dashboard page (internal exploration, exports charts, never shown live),
this is built to be presentable: pick a customer, see the risk score,
category, and recommended action on one screen.

Run: .venv/bin/streamlit run streamlit_app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RISK_CSV = Path(__file__).parent.parent / "analysis" / "customer_risk.csv"

CATEGORY_COLOR = {
    "Monitor Only": "#6b7280",
    "New & Struggling": "#f59e0b",
    "Established & Low Engagement": "#f97316",
    "High-Value Disengaged": "#dc2626",
}
PEER_METRICS = ["Active Days", "Sessions", "Product Actions", "Collaborators", "Integrations Used"]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(RISK_CSV)
    return df


risk = load_data()

st.title("Risk Scorer")
st.caption(
    "Pick a customer to see their risk score, category, and recommended action. "
    "Built on real usage data; ticket fields play no part in this score (see the data audit)."
)

with st.sidebar:
    st.header("Find a customer")
    only_at_risk = st.checkbox("At-risk customers only", value=True)
    category_filter = st.multiselect(
        "Risk category", options=risk["Risk Category"].unique().tolist(),
        default=["High-Value Disengaged"] if only_at_risk else None,
    )
    pool = risk[risk["At Risk"]] if only_at_risk else risk
    if category_filter:
        pool = pool[pool["Risk Category"].isin(category_filter)]
    pool = pool.sort_values("Risk Score", ascending=False)

    options = pool["Customer ID"].tolist()

    if options and st.button("Pick a random one"):
        st.session_state["customer_id"] = pool.sample(1)["Customer ID"].iloc[0]

    if not options:
        st.warning("No customers match this filter.")
        st.stop()

    default_index = options.index(st.session_state["customer_id"]) if st.session_state.get("customer_id") in options else 0
    customer_id = st.selectbox("Customer ID", options=options, index=default_index)

row = risk[risk["Customer ID"] == customer_id].iloc[0]

# --- Header: who this is and the headline verdict --------------------------
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.subheader(f"Customer {row['Customer ID']}")
    st.caption(
        f"{row['Plan Type']} plan · {row['Primary Product']} · {row['Industry']} · {row['Region']} · "
        f"{row['Company Size']} employees"
    )
with col2:
    st.metric("Risk score", f"{row['Risk Score']:.0f} / 100")
with col3:
    color = CATEGORY_COLOR.get(row["Risk Category"], "#6b7280")
    st.markdown(
        f"<div style='background:{color};color:white;padding:0.6rem;border-radius:0.4rem;"
        f"text-align:center;font-weight:600'>{row['Risk Category']}</div>",
        unsafe_allow_html=True,
    )

st.divider()

# --- Why: this customer vs their real peer group ----------------------------
st.subheader("Peer comparison")
st.caption(
    "What this chart shows: this customer's five usage metrics against the median for customers on the "
    "same Plan Type and Primary Product, i.e. their actual peer group, not the whole customer base. This "
    "is the reasoning behind why they were flagged."
)
peers = risk[(risk["Plan Type"] == row["Plan Type"]) & (risk["Primary Product"] == row["Primary Product"])]
peer_median = peers[PEER_METRICS].median()

fig = go.Figure()
fig.add_trace(go.Bar(name="This customer", x=PEER_METRICS, y=[row[m] for m in PEER_METRICS], marker_color="#0052CC"))
fig.add_trace(go.Bar(
    name=f"Peer median ({row['Plan Type']} / {row['Primary Product']})",
    x=PEER_METRICS, y=peer_median.tolist(), marker_color="#B3D4FF",
))
fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.15), template="plotly_white")
st.plotly_chart(fig, width="stretch", key="scorer_peer_chart")

st.caption(
    f"Engagement percentile within peer group: {row['Engagement Percentile']:.0f} "
    f"(bottom 25% = At Risk). Embeddedness percentile: {row['Embeddedness Percentile']:.0f}. "
    f"Tenure: {'recently acquired' if row['Recently Acquired (relative)'] else 'established'} relative to our customer base. "
    f"Usage segment: {row['Usage Cluster']}."
    + (" Flagged as a usage anomaly, meaning the shape of their usage is unusual, which is a different signal from low volume." if row["Usage Anomaly"] else "")
)

st.divider()

# --- What: the recommended action -------------------------------------------
st.subheader("Recommended action")
st.markdown(f"**{row['Recommended Action']}**")

st.divider()
st.caption(
    f"For context only, not part of the score: this customer has filed {int(row['Ticket Count'])} support "
    "ticket(s). Ticket fields are confirmed statistically random in this dataset and play no role in the "
    "risk calculation (see docs/findings-data-quality.md)."
)
