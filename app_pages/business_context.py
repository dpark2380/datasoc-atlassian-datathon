"""
Business context page: why account-level risk detection is worth building,
argued entirely from figures Atlassian filed with the SEC.

Separate from the Dashboard (our analysis of the datathon dataset) and the
Risk Scorer (the per-customer tool) on purpose. Nothing on this page comes
from the datathon dataset; it is external, citable context for the problem.

Run: .venv/bin/streamlit run streamlit_app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

ATLASSIAN_COLORS = ["#0052CC", "#4C9AFF", "#00B8D9", "#6554C0", "#FF991F", "#DE350B"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ATLASSIAN_COLORS

st.title("Business context")
st.caption(
    "The case for per-account risk detection, in Atlassian's own filed numbers. "
    "Nothing on this page comes from the datathon dataset."
)

st.subheader("Revenue concentration")
st.caption(
    "Every figure on this page comes from a document Atlassian filed with the SEC. Nothing here is "
    "estimated, assumed, or taken from a third-party tracker."
)

c1, c2, c3 = st.columns(3)
c1.metric("Customers with >$10,000 Cloud ARR", "57,334", "Q4 FY26")
c2.metric("Share of total Cloud ARR they hold", "over 85%")
c3.metric("Share of the customer base they are", "about 16%", "57,334 of >350,000")

st.markdown(
    "Atlassian's Q4 FY26 shareholder letter, filed as an exhibit to a Form 8-K on 6 August 2026, states:\n\n"
    "> We ended Q4'26 with 57,334 customers with greater than $10,000 in Cloud ARR. This cohort accounts "
    "for over 85% of total Cloud ARR.\n\n"
    "The same filings report more than 350,000 customers in total. Dividing one by the other gives "
    "roughly one account in six holding over 85% of Cloud ARR. That is a division of two published "
    "numbers and nothing else.\n\n"
    "This is why a per-account risk flag is worth building. In a book of business shaped like that, the "
    "cost of missing one disengaging account is not evenly spread."
)

st.markdown("#### The cohort is growing, which is the metric Atlassian says it manages to")
cohort = pd.DataFrame({
    "As at 30 June": ["2024", "2025", "2026"],
    "Customers with >$10,000 Cloud ARR": [45842, 51978, 57334],
})
fig = px.bar(cohort, x="As at 30 June", y="Customers with >$10,000 Cloud ARR")
st.plotly_chart(fig, width="stretch")
st.caption(
    "FY26 Form 10-K, filed 14 August 2026, customer metrics table. The same filing says Atlassian is "
    "\"focused on continuing to grow ... the number of customers with more than $10,000 in annualized "
    "recurring revenue from our Cloud offerings\", because it measures expansion within the existing base."
)

st.divider()
st.markdown("#### Three quotes worth having ready")
st.markdown(
    "On the problem this work addresses, from the 10-K risk factors:\n\n"
    "> Additionally, we may be unable to timely address any retention issues with specific customers, "
    "which could harm our results of operations.\n\n"
    "The load-bearing word is \"specific\". Atlassian's own filing frames the risk as not knowing which "
    "accounts need attention.\n\n"
    "On why support tickets are a thin signal, from Item 1 of the 10-K:\n\n"
    "> Our model focuses on a land-and-expand strategy, with automated and low-touch customer service, "
    "superior product quality, and transparent pricing.\n\n"
    "Backed by the spending in the same filing: $3,269M on research and development against $1,541M on "
    "marketing and sales in FY26. Support being automated and low-touch is a deliberate design choice, "
    "so ticket data is a late and thin signal about account health by design rather than by accident. "
    "Usage telemetry has to carry that load.\n\n"
    "On integration depth, from the Q4 FY26 shareholder letter:\n\n"
    "> MCP adopters are significantly stickier, expand their paid seats faster, and grow their ARR at "
    "rates 2x faster than non-adopters.\n\n"
    "Atlassian measuring stickiness by how many tools a customer connects is the same logic behind the "
    "embeddedness score here, which is built on Integrations Used."
)

st.divider()
st.info(
    "Two limits we state rather than gloss over. First, Cloud ARR and Cloud revenue are different "
    "measures, and Atlassian says so explicitly: \"Cloud ARR and Cloud MRR should be viewed "
    "independently of revenue and do not represent our revenue under GAAP.\" So the 85% is presented as "
    "the published ratio it is, and is never multiplied by a revenue figure to manufacture a dollar "
    "amount. Second, the 8,320 customers in this dataset are not Atlassian's real customers. The "
    "concentration figures describe the business this method would run in, not this sample.",
    icon=":material/info:",
)
st.caption(
    "Sources: Atlassian Q4 FY26 shareholder letter, Form 8-K exhibit filed 6 August 2026. "
    "Atlassian Form 10-K for fiscal year 2026, filed 14 August 2026. Both at sec.gov, CIK 0001650372. "
    "Full citations and the figures we checked and rejected are in the Documentation tab."
)
