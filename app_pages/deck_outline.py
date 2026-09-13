"""
Deck outline page: the presentation plan, kept in the app so it's one click
away instead of a markdown file nobody opens.

Keep this in sync with docs/deck-outline.md whenever the deck plan changes.
This page is a tighter, dotpoint version of that file for fast scanning; the
source doc has the same content in full prose if that's ever needed.

Run: .venv/bin/streamlit run streamlit_app.py
"""
import pandas as pd
import streamlit as st

st.title("Deck outline")
st.caption(
    "Submission: PowerPoint or PDF, due 3pm Monday 14 September. If selected: 8 min presentation + "
    "4 min Q&A. 8 minutes is roughly 10 slides; the timings below total about 7:30, leaving buffer."
)

weights = pd.DataFrame({
    "Criterion": ["Solution & Recommendation", "Analysis & Insights", "Presentation & Q&A", "Story & Problem Statement"],
    "Weight": ["35%", "30%", "20%", "15%"],
})
st.dataframe(weights, width="stretch", hide_index=True)

st.info(
    "The one-sentence story: the support ticket data cannot answer the question asked, we can prove "
    "it, and the usage data can answer it instead. Here is who is at risk, why, and what Atlassian "
    "should do about each one.",
    icon=":material/lightbulb:",
)

SLIDES = [
    {
        "title": "1. The problem",
        "time": "30 sec", "serves": "Story",
        "points": [
            "The challenge statement, then the stakes. Do not open with methodology.",
        ],
        "line": "Atlassian has more than 350,000 customers and cannot call all of them, so the question is which account to work next.",
    },
    {
        "title": "2. Why getting this right is worth money",
        "time": "45 sec", "serves": "Story",
        "points": [
            "57,334 customers hold over 85% of Cloud ARR (Q4 FY26 shareholder letter, filed 6 August 2026).",
            "Against >350,000 customers total, that's about one account in six.",
            "No single customer is >5% of total revenue (FY26 10-K): tens of thousands of accounts, not a handful of whales someone already watches.",
            "Keep Cloud ARR and total ARR apart. The 85% is Cloud ARR only.",
        ],
        "line": "The concentration is real, but spread across tens of thousands of accounts, exactly the range where a person can't watch each one and a model can.",
    },
    {
        "title": "3. The data cannot answer the question as asked",
        "time": "60 sec", "serves": "Analysis (credibility foundation, don't soften it)",
        "points": [
            "Every ticket field tested against every other, all flat: satisfaction, type, priority, channel, subject, resolution time, age, gender, ticket count.",
            "A Critical ticket scores the same average satisfaction as a Low one.",
            "No customer-written text anywhere in the dataset, so sentiment analysis is not possible.",
        ],
        "line": "We could have shown you a sentiment chart. It would have been noise with a trend line on it.",
        "source": "findings-data-quality.md, findings-additional-signals.md",
    },
    {
        "title": "4. We ran the same audit on our own data",
        "time": "45 sec", "serves": "Analysis (most teams won't have this)",
        "points": [
            "Reliability per metric: 0.98 (Sessions) down to 0.63 (Collaborators). Every composite weight is measured, not chosen by hand.",
            "Trend permutation test: shuffled months produce slopes with the same spread as real ones (ratio 0.997). First/second-half slopes correlate at -0.49, i.e. mean reversion.",
        ],
        "line": "There's no trend to analyse in this panel, and we can show that rather than assert it. That's also why a category once called \"Declining\" is now \"Low Engagement.\"",
        "source": "findings-reliability.md",
    },
    {
        "title": "5. What is real",
        "time": "45 sec", "serves": "Analysis",
        "points": [
            "Usage is stable per customer (0.82 correlation Jan-May).",
            "Scales cleanly with plan tier (Free 5.3 active days/month, Enterprise 11.5) and product (Loom ~6.7, Jira ~10.0).",
            "Two charts, no more.",
        ],
    },
    {
        "title": "6. The risk model",
        "time": "60 sec", "serves": "Analysis into Solution",
        "points": [
            "At risk = bottom quartile of engagement within the same plan tier and product (a Free/Loom user isn't judged against an Enterprise/Jira baseline).",
            "Each at-risk account gets a 0-100 score, weighted by account value and embeddedness, plus one of four categories.",
        ],
        "table": pd.DataFrame({
            "Category": ["Monitor Only", "New & Struggling", "Established & Low Engagement", "High-Value Disengaged"],
            "Count": [6248, 518, 893, 661],
        }),
    },
    {
        "title": "7. Why you can trust the split",
        "time": "45 sec", "serves": "Analysis (condense hard, one line each)",
        "points": [
            "Unsupervised clustering, with no knowledge of the risk rules, independently reproduced the same volume-vs-depth split. High-Value Disengaged draws 62% from the integration-heavy cluster.",
            "Anomaly detection flags a different 5% of accounts, only 18% overlapping: the rule isn't just re-deriving what any outlier detector finds.",
            "Every judgment-call parameter was varied and the population barely moves. Bootstrap resampling agrees 99.1% of the time.",
        ],
        "source": "findings-ml-segments.md, findings-sensitivity.md",
    },
    {
        "title": "8. What Atlassian does about it",
        "time": "90 sec, the most important slide", "serves": "Solution, 35% of the marks",
        "points": [
            "New & Struggling: milestone-tracked onboarding review (30/60/90-day checklist), using Atlassian's own Jira Adoption Guide as session material.",
            "High-Value Disengaged: quarterly executive business review, jointly owned by CSM + account leadership, logged via Jira Product Discovery (which Atlassian's CS team already uses).",
            "Established & Low Engagement: automated play naming the specific unused feature, then an in-app nudge, then a short training offer. No CSM time unless it fails.",
            "Monitor Only: nothing. Say this out loud: a model that flags everyone is useless.",
        ],
        "source": "research-cs-playbook-actions.md",
    },
    {
        "title": "9. Atlassian's own Customer Success team already works this way",
        "time": "45 sec", "serves": "Solution (the strongest single slide, don't bury it in an appendix)",
        "points": [
            "An Atlassian Enterprise CSM published her team's prioritisation weighting: Monthly Active Usage 40%, Potential CSM Impact 20%, Months Until Renewal 20%, Customer Readiness 20%.",
            "She inverts the usage term so low adoption ranks an account higher.",
            "No ticket count and no satisfaction score anywhere in those four fields.",
        ],
        "line": "That's the model we built, described by the team we built it for.",
        "warn": "Call it an Atlassian CSM's published method, not Atlassian's official health score. The second version is overclaiming and would be corrected.",
    },
    {
        "title": "10. What to capture next, and close",
        "time": "30 sec", "serves": "Solution",
        "points": [
            "Industry health scores (Gainsight, ChurnZero) combine usage with support sentiment and survey data. Ours has usage only, because this dataset's ticket data can't support the rest.",
            "Closing recommendation, what to start capturing: ordered/real response timestamps, actual customer-written text, tickets linked to account context.",
        ],
        "line": "Close on the specific thing, not a summary of the talk.",
    },
]

st.divider()
st.subheader("Slide by slide")

for i, slide in enumerate(SLIDES):
    with st.expander(f"{slide['title']}  ·  {slide['time']}", expanded=False):
        st.caption(f"Serves: {slide['serves']}")
        st.markdown("\n".join(f"- {p}" for p in slide["points"]))
        if "table" in slide:
            st.dataframe(slide["table"], width="stretch", hide_index=True)
        if "line" in slide:
            st.markdown(f"**Line to say:** {slide['line']}")
        if "warn" in slide:
            st.warning(slide["warn"], icon=":material/warning:")
        if "source" in slide:
            st.caption(f"Source: {slide['source']}")

st.divider()

with st.expander("Backup slides, for Q&A only", expanded=False):
    st.caption("Have these built but not in the main flow.")
    st.markdown(
        "1. **Targeting responsiveness, not just risk.** Ascarza (JMR 2018): targeting the "
        "highest-risk customers is often wrong, they're the least movable. Our four categories "
        "already split on responsiveness. Best raised by us if the conversation goes there.\n"
        "2. Full reliability and permutation detail, including the ICC table.\n"
        "3. Sensitivity tables: cutoff, embeddedness weight, urgency coefficient.\n"
        "4. Support is thin by design: gross margin up partly on \"greater efficiency in customer "
        "support operations,\" cost of revenues up 11% against 26% revenue growth, employee "
        "compensation down $56.2M inside that.\n"
        "5. Integration depth: \"those advantages compound the more applications and contexts a "
        "customer connects,\" and 98% of MCP users are also active in the Jira UI the same month "
        "(answers the \"integration traffic might be bots\" objection).\n"
        "6. The live risk scorer: pick a customer, show the score, the reason, and the recommended "
        "action on one screen."
    )

with st.expander("Do not put these on a slide", expanded=False):
    st.caption("Checked and rejected. If someone else cites one at us, this is the answer.")
    st.markdown(
        "- Reichheld retention figures (\"a 5% retention increase raises profits 25-95%\"). Not in "
        "the original 1990 article in that form; consumer settings only; later work in the same "
        "journal pushed back directly.\n"
        "- \"5x cheaper to retain than acquire.\" Traces to unavailable 1980s research, no recoverable source.\n"
        "- Net revenue retention. Not disclosed in Atlassian's filings; the widely quoted figure comes "
        "from call commentary and third-party trackers.\n"
        "- Churn statistics from vendor blogs. No sample size or method.\n"
        "- The at-a-glance market opportunity / user-diversity splits. Definition changed between Q3 "
        "and Q4 FY26; an Atlassian judge would know.\n"
        "- Any dollar figure from multiplying 85% by Cloud revenue. Atlassian states Cloud ARR is not "
        "GAAP revenue."
    )

st.divider()
st.caption(
    "Standing caveat, state once early: the 8,320 customers in this dataset are not Atlassian's real "
    "customers. The Atlassian figures describe the business this method would run in, not this sample. "
    "Say it once, then stop apologising for it."
)
st.caption(
    "Style rule for every slide: say the specific, checkable thing, not \"sentiment analysis reveals "
    "hidden customer pain points\" but \"the ticket data is statistically random, here's what we built "
    "instead.\" Every number must be one we computed or can point to in a filed document."
)
