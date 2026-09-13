"""Slide-by-slide pitch plan, mirrored in docs/deck-outline.md."""

import pandas as pd
import streamlit as st


st.title("Deck outline")
st.caption(
    "An 18-slide, 8:35 story arc modelled on last year's sample deck: title → problem → stakes → "
    "headline finding → evidence → method → results → action → product reveal. Each slide has one "
    "job and one specified figure."
)

weights = pd.DataFrame(
    {
        "Criterion": [
            "Solution & Recommendation",
            "Analysis & Insights",
            "Presentation & Q&A",
            "Story & Problem Statement",
        ],
        "Weight": ["35%", "30%", "20%", "15%"],
    }
)
st.dataframe(weights, width="stretch", hide_index=True)

st.info(
    "The one-sentence story: the support-ticket file cannot reliably reveal customer sentiment, "
    "but product usage can identify who needs attention, why, and what action to take next.",
    icon=":material/lightbulb:",
)

SLIDES = [
    {
        "title": "1. From Noise to Next Best Action",
        "time": "10 sec",
        "serves": "Opening",
        "headline": "Turn product signals into timely customer action.",
        "figure": (
            "A clean hero graphic: three connected blocks labelled **Signals → Priority → Action**. "
            "Use the Atlassian blue palette; keep the rest of the slide empty apart from title, team, "
            "and a small product screenshot crop."
        ),
        "points": [
            "Subtitle: A usage-led customer risk and action playbook.",
            "Team name and member names only—no methodology on the title slide.",
        ],
        "line": "We built a practical way to turn noisy account data into the next best customer action.",
    },
    {
        "title": "2. Problem Statement",
        "time": "25 sec",
        "serves": "Story & Problem Statement",
        "headline": "Customer risk is useful only if it is detected before value is lost.",
        "figure": (
            "A left-to-right problem chain: **Low adoption → Unseen risk → Late intervention → Lost "
            "customer value**. Put a warning icon over the gap between unseen risk and late intervention."
        ),
        "points": [
            "Business question: which customer needs attention now, and what should the team do?",
            "The brief points to support tickets; first we test whether those tickets contain a defensible signal.",
        ],
        "line": "The goal is not to describe churn after it happens; it is to find the accounts where action can still change the outcome.",
    },
    {
        "title": "3. Why Should Atlassian Care?",
        "time": "30 sec",
        "serves": "Story & Problem Statement",
        "headline": "Protect revenue, increase customer value, and focus limited human attention.",
        "figure": (
            "Three equal columns with simple icons and one outcome each: **Protect recurring revenue**, "
            "**Increase realised customer value**, and **Scale Customer Success**. Under the third column, "
            "add a small funnel labelled **8,320 accounts → 2,072 prioritised for action**. Do not use a "
            "financial filing chart or product-specific adoption statistics here."
        ),
        "points": [
            "Protect recurring revenue: disengagement can become renewal or downsell risk if nobody sees it early.",
            "Increase realised customer value: customers benefit when they adopt the products and integrations they already have.",
            "Scale Customer Success: in this dataset, prioritisation narrows 8,320 accounts to 2,072 that need action.",
        ],
        "line": "This matters to any subscription business: keep customers, help them realise more value, and spend human attention where it can make a difference.",
        "warn": "The 8,320 and 2,072 figures describe the datathon dataset, not Atlassian's real customer base.",
    },
    {
        "title": "4. The Finding That Changed Our Approach",
        "time": "25 sec",
        "serves": "Analysis & Insights",
        "headline": "The ticket file cannot support the sentiment analysis in the brief.",
        "figure": (
            "One oversized **49.3%** with the label **resolved tickets with impossible event order**. "
            "Beside it, a second card reading **0 customer-written text fields**. This is the sample "
            "deck's large-headline-number moment."
        ),
        "points": [
            "2,769 tickets are marked resolved, but almost half have resolution before first response.",
            "Without customer-written text, there is nothing genuine to score for sentiment.",
        ],
        "line": "We could have produced a sentiment chart, but it would have been noise with a trend line on it.",
        "source": "findings-data-quality.md",
    },
    {
        "title": "5. What Each Dataset Can Tell Us",
        "time": "35 sec",
        "serves": "Analysis & Insights",
        "headline": "Three datasets, three different levels of decision value.",
        "figure": (
            "A three-column EDA panel. **customers.csv:** 8,320 rows, 10 fields, four plan tiers. "
            "**customer_support_tickets.csv:** 8,469 rows, zero usable text fields, 49.3% impossible "
            "resolved-event order. **product_usage.csv:** 42,210 observations, five months, 0.82 "
            "January–May usage persistence. Export the three EDA cards from the Dashboard."
        ),
        "points": [
            "Customer data provides account context and peer groups.",
            "Ticket data is suitable for a data-quality audit, not a customer sentiment score.",
            "Usage data provides repeated behavioural observations and becomes the model input.",
        ],
        "line": "We did not combine every column simply because it was available; we assigned each dataset only the role it could support.",
    },
    {
        "title": "6. Why the Ticket File Cannot Measure Sentiment",
        "time": "30 sec",
        "serves": "Analysis & Insights",
        "headline": "Ticket labels are present, but meaningful relationships are not.",
        "figure": (
            "Use the Dashboard's **average satisfaction by ticket priority** bar chart, with all bars "
            "visibly near 3.0. Add a small callout: **Critical ≈ Low satisfaction**. Pair it with a "
            "compact 49.3% invalid-timestamp donut or badge."
        ),
        "points": [
            "Priority, type, channel, resolution time, and satisfaction all come back effectively flat.",
            "Nearly every customer has exactly one ticket, so ticket-volume comparisons have almost no variation.",
            "Conclusion: exclude ticket fields from the score rather than manufacture confidence.",
        ],
        "line": "The responsible analytical decision was to reject the ticket file as a risk signal.",
        "source": "findings-data-quality.md and findings-additional-signals.md",
    },
    {
        "title": "7. The Real Signal: Product Usage",
        "time": "35 sec",
        "serves": "Analysis & Insights",
        "headline": "Usage is repeatable enough to compare customers fairly.",
        "figure": (
            "Primary figure: the Dashboard's **January active days vs May active days** scatter with "
            "**r = 0.82** called out. Add two small KPI cards: **5.3 Free vs 11.5 Enterprise active "
            "days** and **1.1 vs 6.0 integrations (5.3×)**."
        ),
        "points": [
            "The same customers tend to remain relatively high- or low-usage across the five-month window.",
            "Usage also separates coherently by plan and product, unlike the ticket fields.",
        ],
        "line": "Repeated behaviour—not a random ticket label—is the strongest available signal of customer engagement.",
    },
    {
        "title": "8. How We Define Risk",
        "time": "40 sec",
        "serves": "Analysis into Solution",
        "headline": "Forecast next-month disengagement, then explain it against fair peers.",
        "figure": (
            "A two-lane model diagram. **Early warning:** Months 1–4 usage → predict bottom-quartile "
            "engagement in Month 5. **Action layer:** Five-month usage → plan × product peer group → "
            "bottom 25% engagement → value and embeddedness weighting. End both lanes at one "
            "customer card with forecast probability, risk category, and next action."
        ),
        "points": [
            "The forecast provides a one-month warning using an observed future usage outcome.",
            "A Free Loom account is never judged against an Enterprise Jira account.",
            "Neither layer claims to predict contract churn because no churn label exists.",
            "The final 0–100 score ranks urgency after the at-risk rule is applied.",
        ],
        "line": "One layer tells us who may disengage next month; the other explains who they are and what to do.",
    },
    {
        "title": "9. Results: Who Needs Action?",
        "time": "30 sec",
        "serves": "Solution & Recommendation",
        "headline": "2,072 accounts need action; 6,248 should be left alone.",
        "figure": (
            "A horizontal 100% stacked bar or account funnel: **6,248 Monitor Only**, **518 New & "
            "Struggling**, **893 Established & Low Engagement**, **661 High-Value Disengaged**. Use "
            "grey for Monitor and progressively warmer colours for the three action groups."
        ),
        "points": [
            "25% of accounts are prioritised because the threshold is defined within each peer group.",
            "The category split converts a score into distinct operating queues.",
        ],
        "line": "The model's first useful decision is who not to contact; only one account in four enters an action queue.",
        "table": pd.DataFrame(
            {
                "Category": [
                    "Monitor Only",
                    "New & Struggling",
                    "Established & Low Engagement",
                    "High-Value Disengaged",
                ],
                "Accounts": [6248, 518, 893, 661],
            }
        ),
    },
    {
        "title": "10. Usage Segments and Anomaly Detection",
        "time": "30 sec",
        "serves": "Analysis & Insights",
        "headline": "Unsupervised clustering and anomaly detection corroborate the risk categories, independently.",
        "figure": (
            "The Dashboard's k=4 usage-cluster scatter (Usage Volume vs. Integration Depth), with the four "
            "segment counts labelled: **Low engagement (3,154)**, **Active, shallow integration (2,318)**, "
            "**Integration-heavy, moderate usage (1,807)**, **Power users (1,041)**. Beside it, one card: "
            "**416 of 8,320 customers (5.0%) flagged as usage anomalies**, **only 18.3% overlap with At Risk**."
        ),
        "points": [
            "KMeans on the five usage metrics, standardised within each customer's Primary Product so a Loom "
            "account isn't penalised for a lower category baseline than Jira.",
            "k=2 is the cleanest split (silhouette 0.40) but mostly restates the plan-tier finding; k=4 "
            "(silhouette 0.30) trades some separation to split usage volume from integration depth instead.",
            "Isolation Forest (5% contamination) flags a mostly different population from the At Risk rule: "
            "unusual usage shape, not just low usage level.",
            "Both are unsupervised, since there is no churn label to train or validate a supervised model "
            "against; each is evaluated on internal statistical properties, not prediction accuracy.",
        ],
        "line": "This is independent evidence, not decoration: the categories we built by hand and the segments KMeans found on its own point at the same customers.",
        "source": "findings-ml-segments.md",
    },
    {
        "title": "11. Validation: Can We Trust the Result?",
        "time": "35 sec",
        "serves": "Analysis & Insights",
        "headline": "The forecast separates next-month disengagement, and the action queue stays stable.",
        "figure": (
            "A two-panel validation slide. **Forecast panel:** held-out ROC curve with **0.921 AUC**, "
            "**74.1% precision**, **70.4% recall**, and **n = 1,664**. **Prioritisation panel:** "
            "**99.1% bootstrap agreement**, **0.63–0.98 metric reliability**, and **0.997 "
            "real-vs-shuffled trend spread**. Use the trend result as evidence for rejecting trend claims."
        ),
        "points": [
            "The supervised outcome is Month-5 bottom-quartile engagement, not churn or renewal.",
            "The forecast is tested out of sample; the descriptive risk queue is tested for stability.",
            "Sensitivity tests leave rankings and population sizes largely unchanged.",
            "The model deliberately says low engagement, not declining usage, because apparent slopes do not persist.",
        ],
        "line": "We kept the part the data can reproduce and removed the part it cannot.",
        "source": "findings-reliability.md and findings-sensitivity.md",
    },
    {
        "title": "12. Customer Scenarios: Score to Action",
        "time": "35 sec",
        "serves": "Solution & Recommendation",
        "headline": "The same low-usage signal requires different action in different contexts.",
        "figure": (
            "A 2×2 scenario matrix with one anonymised customer card per category. Axes: **new ↔ "
            "established** and **lower value ↔ higher value**. Each card shows plan, product, peer "
            "percentile, score, and a one-line next action."
        ),
        "points": [
            "New & Struggling → onboarding recovery.",
            "Established & Low Engagement → targeted feature reactivation.",
            "High-Value Disengaged → human-led value review.",
            "Monitor Only → no intervention.",
        ],
        "line": "Segmentation matters because urgency, likely cause, and appropriate cost of response are not the same for every account.",
    },
    {
        "title": "13. Method Selection",
        "time": "30 sec",
        "serves": "Analysis & Insights",
        "headline": "Choose the method the available evidence can actually support.",
        "figure": (
            "A four-row decision table: **Sentiment model—rejected: no text**; **Supervised churn "
            "model—rejected: no churn outcome label**; **Month-5 usage forecaster—selected: an "
            "observed next-month engagement label and 0.921 held-out AUC**; **Peer-relative usage "
            "rule—selected: explainable prioritisation and actions**."
        ),
        "points": [
            "Call the supervised output disengagement risk, not churn probability.",
            "Use the forecast to identify who may drop next month and the peer-relative rule to explain context and prescribe action.",
            "Clustering and anomaly detection diagnose behaviour; they are not competing production models.",
        ],
        "line": "We use prediction for an outcome we can observe and transparent rules for decisions people must explain.",
    },
    {
        "title": "14. Strategies for Retention",
        "time": "35 sec",
        "serves": "Solution & Recommendation",
        "headline": "Match the retention play to the likely reason for low engagement.",
        "figure": (
            "Two horizontal playbook lanes with a Primary Product tag on each customer. **New & "
            "Struggling (518): product-specific onboarding milestone → 30/60/90-day review.** "
            "**Established & Low Engagement (893): product-specific workflow prompt → short training "
            "→ human escalation only if needed.** Add examples: Jira production project, Confluence "
            "team space, Trello board + Butler, Bitbucket PR + Pipelines, and Loom async update."
        ),
        "points": [
            "Risk category determines intervention intensity; Primary Product determines the workflow.",
            "Make onboarding recovery milestone-based rather than a generic check-in.",
            "Automate the established-account play first so human effort is reserved for failed interventions.",
            "Treat the workflow as a recommended check, not a detected feature gap; feature-event data is not supplied.",
        ],
        "line": "Retention action should remove the barrier to value, not simply reward disengagement.",
        "source": "research-cs-playbook-actions.md",
    },
    {
        "title": "15. Strategies for Value Protection and Expansion",
        "time": "30 sec",
        "serves": "Solution & Recommendation",
        "headline": "Protect high-value accounts and test deeper adoption where usage is already healthy.",
        "figure": (
            "A two-column action panel. **Protect: 661 High-Value Disengaged → product-specific "
            "executive value review** using measures such as Jira issue throughput, Bitbucket pull "
            "requests, or Confluence contribution. **Expand: 2,318 Active, Shallow Integration "
            "accounts → targeted integration enablement pilot.** Show the pilot as **target vs "
            "control**, not as a promised outcome."
        ),
        "points": [
            "High-value disengagement earns proactive human attention and an agreed recovery plan.",
            "Healthy activity with shallow integration is an expansion hypothesis to test, not proof of propensity.",
            "Measure incremental integration adoption and usage against a control group before scaling.",
        ],
        "line": "The framework protects current value first, then tests expansion where a specific adoption gap is visible.",
    },
    {
        "title": "16. How the Solution Fits Together",
        "time": "20 sec",
        "serves": "Solution & Recommendation",
        "headline": "One pipeline, corroborated and forecast, converging on three outputs.",
        "figure": (
            "A left-to-right pipeline: **Usage data -> Reliability-weighted composites -> Peer-relative "
            "rule -> Risk Score & Category**. Beneath it, a labelled branch, **corroborated by, and given "
            "an early warning from**, showing **KMeans clustering**, **Isolation Forest**, and the "
            "**Month-5 forecaster** feeding upward rather than deciding anything. Both converge on two "
            "final boxes: **Product-specific recommended action** and **Live Risk Scorer tool**."
        ),
        "points": [
            "One backbone does the deciding: data, composites, rule, score. Nothing downstream overrides it.",
            "The three diagnostic/forecasting components corroborate or warn; they are not competing "
            "production models and do not decide who gets flagged.",
            "Everything converges on two outputs a person can act on: a recommended action, and a live tool.",
        ],
        "line": "One backbone, corroborated and forecast, converging on what a person actually uses.",
    },
    {
        "title": "17. Three Outputs, One Pipeline",
        "time": "20 sec",
        "serves": "Solution & Recommendation",
        "headline": "Everything the analysis produces, reduced to three things a person can use.",
        "figure": (
            "Three equal columns, one per output. **Risk Score & Risk Category**: built from the "
            "peer-relative rule on reliability-weighted composites; explainable to a human without "
            "translation. **Recommended Action**: built from product-specific actions applied to the "
            "Risk Category; a named CS playbook, not a generic email. **Live Risk Scorer**: built from all "
            "six components surfaced together; the analysis only matters if someone can act on it in "
            "real time."
        ),
        "points": [
            "Risk Score & Risk Category: every customer scored 0-100 and placed in one of four categories, "
            "compared only to peers on the same Plan Type and Primary Product.",
            "Recommended Action: category sets the intensity, Primary Product sets the workflow.",
            "Live Risk Scorer: score, peer comparison, category, recommended action, and forecast "
            "probability, all on one screen.",
        ],
        "line": "Three outputs, one pipeline: a score, a specific action, and a tool to act on both.",
    },
    {
        "title": "18. Introducing the Customer Risk Playbook",
        "time": "20 sec",
        "serves": "Product reveal and close",
        "headline": "One account, one explanation, one next action.",
        "figure": (
            "A large screenshot of the live Risk Scorer showing customer context, risk score, peer "
            "comparison, and recommended action. Place a tested QR code and short URL beside it. "
            "Use a local screenshot or video fallback if the deployed app requires sign-in."
        ),
        "points": [
            "Close with the working product, not another summary slide.",
            "Final caption: **Detect earlier. Prioritise fairly. Act specifically.**",
        ],
        "line": "This is how the analysis becomes a repeatable Customer Success decision, account by account.",
        "warn": "Verify the deployment from a logged-out browser before printing the QR code; the current app may redirect unauthenticated judges.",
    },
]

st.divider()
st.subheader("Slide by slide")

for slide in SLIDES:
    with st.expander(f"{slide['title']}  ·  {slide['time']}", expanded=False):
        st.caption(f"Serves: {slide['serves']}")
        st.markdown(f"### {slide['headline']}")
        st.markdown("**Figure to add**")
        st.markdown(slide["figure"])
        st.markdown("**Put on the slide**")
        st.markdown("\n".join(f"- {point}" for point in slide["points"]))
        if "table" in slide:
            st.dataframe(slide["table"], width="stretch", hide_index=True)
        st.markdown(f"**Line to say:** {slide['line']}")
        if "warn" in slide:
            st.warning(slide["warn"], icon=":material/warning:")
        if "source" in slide:
            st.caption(f"Source: {slide['source']}")

st.divider()

with st.expander("Backup slides, for Q&A only", expanded=False):
    st.markdown(
        "1. Full ticket data-quality audit and impossible timestamp examples.\n"
        "2. Reliability table and trend permutation distributions.\n"
        "3. Cutoff, weighting, and bootstrap sensitivity tables.\n"
        "4. Full action-playbook evidence and ownership model.\n"
        "5. Revenue concentration and company-specific context, only if a judge asks.\n"
        "6. Live Risk Scorer walkthrough."
    )

with st.expander("Claims to leave out", expanded=False):
    st.markdown(
        "- Generic retention myths such as ‘5× cheaper to retain’ or ‘5% retention raises profit 25–95%’.\n"
        "- Product-specific adoption claims as the main business-stakes story; they require too much context.\n"
        "- Accuracy, precision, recall, AUC, or churn probability for contract churn without a churn outcome label.\n"
        "- Causal claims that usage or integration alone produces revenue growth.\n"
        "- Any conversion of Cloud ARR shares into GAAP revenue dollars."
    )

st.caption(
    "Standing caveat: the 8,320 accounts are a datathon dataset, not Atlassian's real customers. "
    "State this once, clearly. Every number shown should be computed from the supplied data or linked "
    "to a named source."
)
