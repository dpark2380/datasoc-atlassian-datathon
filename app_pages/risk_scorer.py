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

from app_pages.chart_styling import render_plotly_chart

RISK_CSV = Path(__file__).parent.parent / "analysis" / "customer_risk.csv"
PRED_CSV = Path(__file__).parent.parent / "analysis" / "customer_disengagement_predictions.csv"

CATEGORY_COLOR = {
    "Monitor Only": "#6b7280",
    "New & Struggling": "#f59e0b",
    "Established & Low Engagement": "#f97316",
    "High-Value Disengaged": "#dc2626",
}
PEER_METRICS = ["Active Days", "Sessions", "Product Actions", "Collaborators", "Integrations Used"]


@st.cache_data
def load_data(risk_mtime: float) -> pd.DataFrame:
    """risk_mtime busts the cache when customer_risk.csv is regenerated --
    see the matching fix and comment in app_pages/dashboard.py's load_data."""
    df = pd.read_csv(RISK_CSV)
    if PRED_CSV.exists():
        preds = pd.read_csv(PRED_CSV)
        df = df.merge(preds[["Customer ID", "Predicted Disengagement Prob"]], on="Customer ID", how="left")
    return df


risk = load_data(RISK_CSV.stat().st_mtime)

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
# --- Header: who this is and the headline verdict --------------------------
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.subheader(f"Customer {row['Customer ID']}")
    st.caption(
        f"{row['Plan Type']} plan · {row['Primary Product']} · {row['Industry']} · {row['Region']} · "
        f"{row['Company Size']} employees"
    )
with col2:
    st.metric("Risk score", f"{row['Risk Score']:.0f} / 100")
with col3:
    if "Predicted Disengagement Prob" in row and pd.notna(row["Predicted Disengagement Prob"]):
        st.metric("30-Day Risk Forecast", f"{row['Predicted Disengagement Prob']:.0%}")
    else:
        st.metric("Status", "At Risk" if row["At Risk"] else "Healthy")
with col4:
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
render_plotly_chart(fig, width="stretch", key="scorer_peer_chart")

anomaly_desc = ""
if row["Usage Anomaly"]:
    driver = row.get("Anomaly Driver", "Unusual usage shape")
    anomaly_desc = f" Flagged as a usage anomaly (Driver: {driver})."

st.caption(
    f"Engagement percentile within peer group: {row['Engagement Percentile']:.0f} "
    f"(bottom 25% = At Risk). Embeddedness percentile: {row['Embeddedness Percentile']:.0f}. "
    f"Tenure: {'recently acquired' if row['Recently Acquired (relative)'] else 'established'} relative to our customer base. "
    f"Usage segment: {row['Usage Cluster']}.{anomaly_desc}"
)

st.divider()

# --- Longitudinal Telemetry: 5-Month Trajectory ------------------------------
st.subheader("Longitudinal Telemetry: 5-Month Engagement Trajectory")
st.caption(
    "How this customer's engagement progressed from Month 1 (Jan) to Month 5 (May) "
    "compared to the healthy and disengaged peer cohort benchmarks."
)
try:
    from analysis.trajectory_utils import build_trajectory_plot
    scorer_traj_metric = st.selectbox(
        "Trajectory Metric:",
        ["Active Days", "Sessions", "Product Actions"],
        index=0,
        key="scorer_traj_metric_select",
    )
    fig_scorer_traj = build_trajectory_plot(metric=scorer_traj_metric, selected_customers=[customer_id])
    render_plotly_chart(fig_scorer_traj, width="stretch", key=f"scorer_traj_{customer_id}_{scorer_traj_metric}")
except Exception as e:
    st.info(f"Longitudinal trajectory plot temporarily unavailable: {e}")

st.divider()

# --- SHAP Risk Attribution: Explainable AI ----------------------------------
st.subheader("Why this customer? (SHAP Positive vs. Negative Risk Attribution)")
st.caption(
    "SHAP (Shapley Additive exPlanations) breaks down the exact marginal contribution of each telemetry "
    "metric to this customer's forecasted disengagement risk. Red bars (Right / +) escalate churn risk; "
    "blue bars (Left / -) act as protective retention factors."
)

shap_choice_col, _ = st.columns([2, 2])
with shap_choice_col:
    shap_plot_type = st.radio(
        "Attribution plot style:",
        ["Double-Sided Impact Plot (+/-)", "Sequential Waterfall"],
        horizontal=True,
        key="scorer_shap_plot_type",
    )

try:
    from analysis.shap_utils import build_shap_diverging_bar, build_shap_waterfall
    if shap_plot_type == "Double-Sided Impact Plot (+/-)":
        fig_shap = build_shap_diverging_bar(customer_id)
    else:
        fig_shap = build_shap_waterfall(customer_id)
    render_plotly_chart(fig_shap, width="stretch", key=f"scorer_shap_{customer_id}_{shap_plot_type}")
except Exception as e:
    st.info(f"SHAP attribution temporarily unavailable: {e}")

st.divider()

# --- What: the recommended action -------------------------------------------
st.subheader(f"Recommended action for {row['Primary Product']}")
st.markdown(f"**{row['Recommended Action']}**")
st.caption(
    "The risk category sets the intervention intensity; Primary Product sets the workflow focus. "
    "Confirm the specific feature gap with product-level event telemetry or the customer before acting."
)

st.divider()
st.caption(
    f"For context only, not part of the score: this customer has filed {int(row['Ticket Count'])} support "
    "ticket(s). Ticket fields are confirmed statistically random in this dataset and play no role in the "
    "risk calculation (see docs/findings-data-quality.md)."
)
