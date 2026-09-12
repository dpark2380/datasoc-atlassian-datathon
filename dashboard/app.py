"""
EDA dashboard (workstream B). Run: .venv/bin/streamlit run dashboard/app.py

Reads analysis/cleaned_tickets.csv (placeholder dataset). Swap the CSV_PATH
constant once the official dataset lands -- everything below is written
against column names, not the specific dataset, so it should mostly survive
a swap as long as columns are renamed to match.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CSV_PATH = Path(__file__).parent.parent / "analysis" / "cleaned_tickets.csv"

st.set_page_config(page_title="Support Ticket EDA", layout="wide")


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Ticket Priority"] = pd.Categorical(
        df["Ticket Priority"], categories=["Low", "Medium", "High", "Critical"], ordered=True
    )
    return df


df = load_data(CSV_PATH)

st.title("Support Ticket EDA")
st.caption(
    "PLACEHOLDER DATASET pending tomorrow's official prompt/data. "
    "Layout and cuts below are dataset-agnostic; numbers will change."
)

# --- Filters -----------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    priorities = st.multiselect(
        "Priority", options=df["Ticket Priority"].cat.categories.tolist(),
        default=df["Ticket Priority"].cat.categories.tolist(),
    )
    channels = st.multiselect(
        "Channel", options=sorted(df["Ticket Channel"].unique()),
        default=sorted(df["Ticket Channel"].unique()),
    )

filtered = df[df["Ticket Priority"].isin(priorities) & df["Ticket Channel"].isin(channels)]

# --- KPI row -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tickets", f"{len(filtered):,}")
col2.metric("At-risk tickets", f"{filtered['At Risk'].sum():,}", f"{filtered['At Risk'].mean():.1%}")
col3.metric("Avg resolution (hrs)", f"{filtered['Resolution Hours'].mean():.1f}")
avg_csat = filtered["Customer Satisfaction Rating"].mean()
col4.metric("Avg CSAT (closed only)", f"{avg_csat:.2f}" if pd.notna(avg_csat) else "n/a")

st.divider()

# --- Volume & priority ---------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    st.subheader("Ticket volume by type")
    fig = px.bar(filtered["Ticket Type"].value_counts().reset_index(), x="Ticket Type", y="count")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Ticket volume by priority")
    fig = px.bar(
        filtered["Ticket Priority"].value_counts().reindex(df["Ticket Priority"].cat.categories).reset_index(),
        x="Ticket Priority", y="count",
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Resolution time -------------------------------------------------------
st.subheader("Resolution time by priority")
fig = px.box(filtered.dropna(subset=["Resolution Hours"]), x="Ticket Priority", y="Resolution Hours")
st.plotly_chart(fig, use_container_width=True)

# --- Sentiment -------------------------------------------------------------
c3, c4 = st.columns(2)
with c3:
    st.subheader("Sentiment distribution")
    fig = px.pie(filtered, names="Sentiment Label")
    st.plotly_chart(fig, use_container_width=True)
with c4:
    st.subheader("CSAT distribution (closed tickets)")
    csat = filtered.dropna(subset=["Customer Satisfaction Rating"])
    fig = px.histogram(csat, x="Customer Satisfaction Rating", nbins=5)
    st.plotly_chart(fig, use_container_width=True)

# --- The honesty check, front and center ------------------------------
st.divider()
st.subheader("Does anything correlate with CSAT?")
st.caption(
    "This is the sanity check every claim in the deck needs to pass. "
    "In the placeholder dataset, CSAT is statistically random -- roughly "
    "uniform across every field we tested. Rerun analysis/sanity_check.py "
    "on the real dataset before building any 'X predicts satisfaction' slide."
)
group_col = st.selectbox(
    "Group CSAT by", ["Ticket Priority", "Ticket Channel", "Ticket Type", "Sentiment Label"]
)
means = filtered.groupby(group_col, observed=True)["Customer Satisfaction Rating"].mean().reset_index()
fig = px.bar(means, x=group_col, y="Customer Satisfaction Rating", range_y=[0, 5])
st.plotly_chart(fig, use_container_width=True)

# --- At-risk table -----------------------------------------------------
st.divider()
st.subheader("At-risk tickets (sample)")
st.caption("Flag = High/Critical priority + slow-or-unresolved + (negative sentiment or CSAT <= 2)")
st.dataframe(
    filtered[filtered["At Risk"]][
        ["Ticket ID", "Ticket Type", "Ticket Priority", "Ticket Channel",
         "Resolution Hours", "Sentiment Label", "Customer Satisfaction Rating"]
    ].head(50),
    use_container_width=True,
)
