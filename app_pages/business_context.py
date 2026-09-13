"""
Business context page: why account-level risk detection is worth building,
argued from Atlassian's own published sources.

Separate from the Dashboard (our analysis of the datathon dataset) and the
Risk Scorer (the per-customer tool) on purpose. Nothing on this page comes
from the datathon dataset; it is external, citable context for the problem.

Sources are labelled by weight, because a figure Atlassian filed with the SEC
and a figure an Atlassian employee published on the Community hold up
differently under questioning. Full citations, plus the widely repeated
statistics we checked and rejected, are in
docs/research-business-context-figures.md.

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
    "The case for per-account risk detection, in Atlassian's own numbers. Nothing on this page comes "
    "from the datathon dataset. Each item is labelled filed (submitted to the SEC) or published "
    "(first-party, but not a regulatory filing)."
)

# --- 1. Concentration -----------------------------------------------------
st.header("1. Missing one account is expensive")

c1, c2, c3 = st.columns(3)
c1.metric("Customers with >$10,000 Cloud ARR", "57,334", "Q4 FY26")
c2.metric("Share of total Cloud ARR they hold", "over 85%")
c3.metric("Share of the customer base they are", "about 16%", "57,334 of >350,000")

st.markdown(
    "**Filed.** Atlassian's Q4 FY26 shareholder letter, an exhibit to a Form 8-K filed 6 August 2026:\n\n"
    "> We ended Q4'26 with 57,334 customers with greater than $10,000 in Cloud ARR. This cohort accounts "
    "for over 85% of total Cloud ARR.\n\n"
    "The same filings report more than 350,000 customers in total, so that cohort is roughly one account "
    "in six. That is a division of two published numbers and nothing else."
)

st.markdown(
    "**Filed.** The obvious reply is that this must really be a handful of giant accounts a salesperson "
    "already knows by name. The FY26 10-K closes that off:\n\n"
    "> No single customer contributed more than 5% of our total revenues during fiscal year 2026.\n\n"
    "So the concentration is spread across tens of thousands of accounts. That is precisely the range "
    "where no individual can watch every account and a model can."
)

st.markdown("##### The cohort Atlassian says it manages to is growing")
cohort = pd.DataFrame({
    "As at 30 June": ["2024", "2025", "2026"],
    "Customers with >$10,000 Cloud ARR": [45842, 51978, 57334],
})
fig = px.bar(cohort, x="As at 30 June", y="Customers with >$10,000 Cloud ARR")
st.plotly_chart(fig, width="stretch", key="biz_chart_1")
st.caption(
    "FY26 Form 10-K, filed 14 August 2026, customer metrics table. The same filing says Atlassian is "
    "\"focused on continuing to grow ... the number of customers with more than $10,000 in annualized "
    "recurring revenue from our Cloud offerings\", because it measures expansion within the existing base. "
    "Separately, and on total ARR rather than Cloud ARR, the Q4 FY26 letter reports that customers above "
    "$3M ARR grew more than 50% year on year and those above $5M grew more than 70%, so the largest "
    "accounts are also the fastest growing. Keep the two measures apart when presenting: the 85% figure "
    "above is Cloud ARR, these two are total ARR."
)

st.divider()

# --- 2. Atlassian's own CS team ------------------------------------------
st.header("2. Atlassian's own Customer Success team already prioritises this way")

st.markdown(
    "**Published, first-party, attributable.** Jaclyn Ruby, an Enterprise Customer Success Manager at "
    "Atlassian, published how her team decides which account to work next. The weighted score is:"
)
weights = pd.DataFrame({
    "Field": ["Monthly Active Usage", "Potential CSM Impact", "Months Until Renewal", "Customer Readiness"],
    "Weight": [40, 20, 20, 20],
})
fig = px.bar(weights, x="Weight", y="Field", orientation="h")
fig.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig, width="stretch", key="biz_chart_2")

st.markdown(
    "On how the usage term is signed:\n\n"
    "> Atlassian CSMs are focused on increasing adoption so I wanted customers with lower MAU to have a "
    "higher impact on the Impact Score. To do this, put a negative in front of the MAU number, which "
    "helps prioritize customers with low adoption\n\n"
    "Two things matter here. Usage is the heaviest input at 40%, and it is inverted, so low adoption "
    "pulls an account up the queue. That is the rule this project built, described by the company it was "
    "built for.\n\n"
    "Also worth noting: no support ticket count and no satisfaction score appears anywhere in those four "
    "fields. Our decision to leave ticket data out of the model has an independent justification beyond "
    "this dataset's ticket columns being random."
)
st.caption(
    "Source: \"How Atlassian's Customer Success team uses Jira Product Discovery for account "
    "prioritization\", Atlassian Community, 12 June 2025. This is one CSM describing her own team's "
    "setup, so it is fair to call it an Atlassian CSM's published prioritisation method, and overclaiming "
    "to call it Atlassian's official customer health score."
)

st.divider()

# --- 3. Support is thin by design ----------------------------------------
st.header("3. Support is a thin signal by design, not by accident")

st.markdown(
    "**Filed.** From Item 1 of the FY26 10-K:\n\n"
    "> Our model focuses on a land-and-expand strategy, with automated and low-touch customer service, "
    "superior product quality, and transparent pricing.\n\n"
    "Where the money goes backs that up: $3,269M on research and development against $1,541M on marketing "
    "and sales in FY26."
)

st.markdown(
    "**Filed.** That is the stated intention. The reported numbers show the direction of travel inside "
    "the support function itself. From the Q4 FY26 shareholder letter:\n\n"
    "> GAAP gross margin of 87% and non-GAAP gross margin of 89% increased by more than three ppts from "
    "the prior year, driven by continued optimization of our infrastructure and greater efficiency in our "
    "customer support operations.\n\n"
    "The FY26 10-K points the same way across the full year. Cost of revenues rose 11% against revenue "
    "growth of 26%, and inside that line employee compensation fell $56.2M.\n\n"
    "Customer numbers grew while the people cost of serving them fell. A support organisation being "
    "deliberately made cheaper per customer produces thinner and later signal per customer. That is the "
    "argument for not building a risk model on tickets, in Atlassian's own reported figures rather than "
    "as our opinion."
)
st.caption(
    "The 87% gross margin is the quarter and the 85% full-year figure is in the 10-K. Quote one, say "
    "which period it covers, and do not mix them."
)

st.divider()

# --- 4. Nobody is watching most of these accounts -------------------------
st.header("4. Below a certain size, nobody is assigned to the account at all")

st.markdown(
    "**Filed.** This is the part that decides what the solution has to look like. From the FY26 10-K:\n\n"
    "> Historically, a majority of users do not convert from free trials or limited free versions to paid "
    "apps or products, and our strategy also relies on these users influencing broader adoption within "
    "their organizations.\n\n"
    "> ... we do not have to solely rely on a traditional, commissioned direct sales force until a "
    "customer reaches a specific size, thanks to the automation and efficiency built into our sales "
    "model.\n\n"
    "Read those together. Below the enterprise threshold there is no assigned human watching the account. "
    "Nobody is having a quarterly conversation with a mid-sized Standard-plan customer, so there is no "
    "relationship through which quiet disengagement would surface. If the signal is not in the telemetry, "
    "it does not exist anywhere."
)

st.markdown("##### What that means the solution has to do")
st.markdown(
    "1. **Run with no human in the loop to detect.** Detection cannot depend on a CSM noticing something, "
    "because for most accounts there is no CSM. The flag has to be computed from usage data on a "
    "schedule.\n"
    "2. **Work at tens of thousands of accounts, not hundreds.** The concentration in section 1 sits "
    "across 57,334 accounts. A process that only scales to the named-account list misses the range where "
    "this matters most.\n"
    "3. **Automate the intervention as well as the detection.** Flagging an account nobody is "
    "assigned to achieves nothing on its own. This is exactly why the Established & Low Engagement play "
    "is a feature-specific email, then an in-app nudge, then a training offer, with no CSM time spent "
    "unless the automated sequence fails to move usage. The intervention has to be as automatic as the "
    "detection for the tier that has no owner.\n"
    "4. **Reserve human effort for where it is justified.** The High-Value Disengaged play is an "
    "executive business review precisely because that tier is above the threshold where Atlassian does "
    "assign people."
)
st.caption(
    "This is the clearest filed justification for an automated, usage-driven detector, and it is also the "
    "reason the playbook is tiered rather than uniform. The tiering is not a nicety; it follows from "
    "Atlassian's own stated sales and support model."
)

st.divider()

# --- 5. Integration depth -------------------------------------------------
st.header("5. Integration depth is a stickiness signal, which is what the embeddedness score uses")

st.markdown(
    "**Filed.** The clause that most directly licenses a count-of-integrations score, from the Q4 FY26 "
    "shareholder letter on the Teamwork Graph:\n\n"
    "> It's baked into our platform and those advantages compound the more applications and contexts a "
    "customer connects.\n\n"
    "Monotonic in the number of connected applications is the shape of the embeddedness score itself.\n\n"
    "The same letter puts numbers on it:\n\n"
    "> MCP adopters are significantly stickier, expand their paid seats faster, and grow their ARR at "
    "rates 2x faster than non-adopters.\n\n"
    "> Rovo adopters continue to grow their ARR more than 2x faster than non-adopters\n\n"
    "Atlassian also measures account value in units of product activity, which is what "
    "`product_usage.csv` contains: Rovo adopters complete 20% more Jira work items and create or edit "
    "25% more Confluence pages than non-adopters. Those are associations rather than proven causation, "
    "and the slide should say so."
)

st.info(
    "Held in reserve for the obvious objection, which is that integration traffic might be machines "
    "rather than people. The same letter reports that 98% of MCP users are also active in the Jira UI in "
    "the same month. Integration depth and human engagement move together rather than substituting for "
    "each other.",
    icon=":material/shield:",
)

st.divider()

# --- 6. The hardest question ---------------------------------------------
st.header("6. The hardest question, and the answer")

st.markdown(
    "**Peer-reviewed.** The strongest challenge to any risk model is that targeting the highest-risk "
    "customers is not automatically the right rule. Eva Ascarza (Journal of Marketing Research, 2018) "
    "ran two field experiments and found that firms should target on how much a customer's behaviour "
    "will change in response to the intervention, not on how likely they are to leave. The customers "
    "most likely to churn are often the ones least movable.\n\n"
    "Our model already answers this, and it is better raised by us than by a judge. The four categories "
    "split on how movable an account is alongside how at risk it is. A recently-acquired account with low adoption gets "
    "onboarding help because that is a fixable situation. A long-tenured, heavily-integrated account "
    "gets a different and more senior intervention because the stakes and the levers are different. "
    "The Atlassian CSM's \"Potential CSM Impact\" field in section 2 is the same idea, weighted "
    "separately from usage."
)

st.divider()

# --- 7. What Atlassian's own product already captures ---------------------
st.header("7. What Atlassian's own product already captures")
st.caption(
    "This grounds the closing recommendation in Atlassian's own published API and schema, not a "
    "generic wishlist. Sources: the JSM Cloud REST API reference and the published Atlassian "
    "Analytics warehouse schema for Jira Service Management."
)

st.metric("Support-relevant columns in this dataset that map to a JSM concept", "11 of 13", "all flattened")

jsm_gap = pd.DataFrame({
    "Dataset column": [
        "Customer Satisfaction Rating", "First Response Time / Time to Resolution",
        "Ticket Status", "Customer Email", "Ticket Channel", "Ticket Type",
    ],
    "What JSM actually models": [
        "CSATFeedbackFullDTO: rating (1-5) plus a comment field",
        "SlaInformationOngoingCycleDTO: goal, elapsed time, breach flag, pause flag, working-hours flag",
        "Full changelog: every transition, its author, and its timestamp",
        "jsm_issue_organization_mapping: request mapped to an organization",
        "Fixed vocabulary: jira, portal, anonymousportal, email, API, deployment (no Phone or Social media)",
        "RequestTypeDTO: id, name, practice, and a configured field schema",
    ],
})
st.dataframe(jsm_gap, width="stretch", hide_index=True)

st.markdown(
    "- **The gap that matters most:** the rating half of CSAT is exactly what this dataset gives us. "
    "The `comment` field is exactly the sentiment data the challenge asks for and this dataset lacks.\n"
    "- **Also absent from the file entirely:** comment threads (with a public/internal flag), SLA "
    "breach state, organization mapping, work logs, approvals, issue links, incident severity.\n"
    "- **One thing this rules out:** `Ticket Channel` and `Ticket Type` use vocabularies JSM doesn't, "
    "so this file was not exported from a real JSM instance. It's a simulation shaped like one."
)
st.caption(
    "Say \"your public API models this,\" not \"your systems contain this\": the API reference shows "
    "what JSM exposes, not how Atlassian provisions data internally."
)

st.divider()

st.warning(
    "Statistics we checked and deliberately left out. The Reichheld retention figures (\"a 5% increase "
    "in retention raises profits 25% to 95%\") do not appear in that form in the original 1990 article, "
    "which reports 85%, 50% and 30% for three consumer businesses, and later work in the same journal "
    "published direct pushback. The \"5x cheaper to retain than acquire\" claim traces to unavailable "
    "1980s research with no recoverable primary source. Net revenue retention is not disclosed in "
    "Atlassian's filings at all, so the widely quoted figure stays off the deck. Vendor-blog churn "
    "statistics carried no methodology and were treated as unusable. Full reasoning is in the research "
    "doc in the Dashboard's Documentation tab.",
    icon=":material/report:",
)

st.caption(
    "Sources: Atlassian Q4 FY26 shareholder letter, Form 8-K exhibit filed 6 August 2026. Atlassian "
    "Form 10-K for fiscal year 2026, filed 14 August 2026. Both at sec.gov, CIK 0001650372. Atlassian "
    "Community, 12 June 2025. Ascarza, Journal of Marketing Research 55(1), 2018. "
    "Two limits we state rather than gloss over: Cloud ARR is not GAAP revenue and Atlassian says so "
    "explicitly, so the 85% is never multiplied into a dollar figure; and the 8,320 customers in this "
    "dataset are not Atlassian's real customers, so these figures describe the business this method "
    "would run in, not this sample."
)
