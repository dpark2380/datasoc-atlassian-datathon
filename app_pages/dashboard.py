"""
Results dashboard page: everything from the analysis in one place. Export
charts from here into the deck; this page is never demoed live (submission
is deck/PDF only). The single-customer risk-scorer (live demo, workstream C)
is the other page in this app, app_pages/risk_scorer.py.

Run: .venv/bin/streamlit run streamlit_app.py

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

# Atlassian-blue-led qualitative palette, for chart color consistency.
ATLASSIAN_COLORS = ["#0052CC", "#4C9AFF", "#00B8D9", "#6554C0", "#FF991F", "#DE350B"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ATLASSIAN_COLORS

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


def z_score(col: pd.Series) -> pd.Series:
    return (col - col.mean()) / col.std()


@st.cache_data
def load_data():
    risk = pd.read_csv(RISK_CSV)
    risk["Plan Type"] = pd.Categorical(risk["Plan Type"], categories=PLAN_ORDER, ordered=True)
    risk["Risk Category"] = pd.Categorical(risk["Risk Category"], categories=CATEGORY_ORDER, ordered=True)
    risk["Usage Volume"] = pd.concat(
        [z_score(risk[c]) for c in ["Active Days", "Sessions", "Product Actions"]], axis=1
    ).mean(axis=1)
    risk["Integration Depth"] = pd.concat(
        [z_score(risk[c]) for c in ["Collaborators", "Integrations Used"]], axis=1
    ).mean(axis=1)
    tickets = pd.read_csv(TICKETS_CSV)
    usage = pd.read_csv(USAGE_CSV)
    return risk, tickets, usage


@st.cache_data
def load_sensitivity_results(_risk: pd.DataFrame):
    bootstrap_mean, bootstrap_detail = sensitivity_checks.bootstrap_flag_stability(_risk)
    return {
        "cutoff": sensitivity_checks.cutoff_sensitivity(_risk),
        "embeddedness": sensitivity_checks.embeddedness_weight_sensitivity(_risk),
        "urgency": sensitivity_checks.urgency_coefficient_sensitivity(_risk),
        "bootstrap_mean": bootstrap_mean,
        "bootstrap_detail": bootstrap_detail,
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

tab_overview, tab_risk, tab_segments, tab_robustness, tab_docs = st.tabs(
    ["Overview", "Risk model", "Usage segments (ML)", "Robustness checks", "Documentation"]
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

    st.subheader("Support ticket data (descriptive only, not predictive)")
    st.caption(
        "Ticket Type, Priority, Channel, and Satisfaction are confirmed random in this dataset "
        "(near-zero spread across every field we tested; see the data quality audit doc). "
        "These charts show raw operational volume, not a driver of risk."
    )
    c_ticket1, c_ticket2 = st.columns(2)
    with c_ticket1:
        fig = px.bar(tickets["Ticket Type"].value_counts().reset_index(), x="Ticket Type", y="count")
        st.plotly_chart(fig, width="stretch")
    with c_ticket2:
        fig = px.bar(tickets["Ticket Channel"].value_counts().reset_index(), x="Ticket Channel", y="count")
        st.plotly_chart(fig, width="stretch")

# --- Risk model --------------------------------------------------------------
with tab_risk:
    st.subheader("Usage scales with plan tier (the real signal)")
    st.caption("Active Days by Plan Type. This is genuine, not a data artifact (see Documentation tab).")
    means = risk.groupby("Plan Type", observed=True)["Active Days"].mean().reindex(PLAN_ORDER).reset_index()
    fig = px.bar(means, x="Plan Type", y="Active Days")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Risk category breakdown")
        counts = filtered["Risk Category"].value_counts().reindex(CATEGORY_ORDER).reset_index()
        fig = px.bar(counts, x="Risk Category", y="count")
        st.plotly_chart(fig, width="stretch")
        st.markdown(
            "- **Monitor Only**: not at risk. Usage sits above the bottom quarter for this customer's plan "
            "and product peer group. No action.\n"
            "    - At Risk = Engagement Percentile ≤ 25, where Engagement Percentile is this customer's "
            "Engagement Composite ranked (percentile, 0-100) only against customers on the same Plan Type "
            "and Primary Product.\n"
            "    - Engagement Composite = the average of Active Days, Sessions, and Product Actions, each "
            "min-max scaled to 0-1 first so no single metric's raw scale dominates the average.\n"
            "    - Monitor Only is simply every customer where this condition is false (Engagement "
            "Percentile > 25).\n"
            "- **New & Struggling**: at risk, and recently acquired relative to the rest of the customer "
            "base. Reads as an onboarding problem, not churn.\n"
            "    - Recently acquired = Account Age ≤ the 25th percentile of Account Age across *all* "
            "customers, where Account Age = (2023-05-31 minus Account Created Date), in days.\n"
            "    - This is a relative quartile, not an absolute cutoff like \"under 90 days\": no customer "
            "in this dataset is younger than about 1.5 years by the 2023 usage window, so \"recently "
            "acquired\" means the youngest 25% of the base, not literally new.\n"
            "- **Established & Declining**: at risk, longer-tenured, and either lower plan tier or lower "
            "embeddedness. A real but lower-stakes churn risk.\n"
            "    - Applies when At Risk is true, Recently Acquired is false, and High-Value (defined below) "
            "is also false.\n"
            "- **High-Value Disengaged**: at risk, longer-tenured, and either Enterprise/Premium tier or "
            "heavily integrated (top quartile of Collaborators + Integrations Used). The account most "
            "worth protecting.\n"
            "    - High-Value = Plan Type is Enterprise or Premium, OR Embeddedness Percentile ≥ 75.\n"
            "    - Embeddedness Percentile = the percentile rank (0-100), across *all* customers, of "
            "(Collaborators × 1) + (Integrations Used × 2). Integrations Used is weighted double because it "
            "showed a sharper relationship with plan tier in testing (see the Documentation tab).\n"
            "    - Applies when At Risk is true, Recently Acquired is false, and High-Value is true."
        )
    with c2:
        st.subheader("Usage by product")
        st.caption("Secondary real cut: Jira and other daily-use tools show higher engagement than Loom.")
        by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
        fig = px.bar(by_product, x="Product", y="Active Days")
        st.plotly_chart(fig, width="stretch")

    st.subheader("At-risk customers and recommended action (sample)")
    st.dataframe(
        at_risk[
            ["Customer ID", "Plan Type", "Primary Product", "Risk Category", "Risk Score",
             "Active Days", "Embeddedness Percentile", "Recommended Action"]
        ].sort_values("Risk Score", ascending=False).head(50),
        width="stretch",
    )

# --- Usage segments (ML) -----------------------------------------------------
with tab_segments:
    st.subheader("Usage segments (unsupervised, independent of the Risk Score)")
    st.caption(
        "KMeans on standardised usage metrics, discovered from the data rather than hand-picked."
    )

    with st.expander("How these labels are decided", expanded=False):
        st.markdown(
            "- KMeans is fit first, purely on the numbers. It has no idea what \"Power users\" means, "
            "it just finds groups of customers with similar usage patterns.\n"
            "- Each cluster's centroid (its average member) is reduced to two scores: **usage volume** "
            "(Active Days, Sessions, Product Actions, standardised and averaged) and **integration depth** "
            "(Collaborators, Integrations Used, standardised and averaged).\n"
            "- The clusters are ranked against each other on both scores, split into a top half and bottom "
            "half on each axis.\n"
            "- That gives four combinations: high volume + high depth is named \"Power users\"; high volume "
            "+ low depth is \"Active, shallow integration\"; low volume + high depth is \"Integration-heavy, "
            "moderate usage\"; low volume + low depth is \"Low engagement\".\n"
            "- The labels are computed from where each cluster actually sits every time the pipeline reruns, "
            "not hardcoded to a cluster number (KMeans' own numbering is arbitrary).\n"
            "- Usage volume and integration depth correlate at 0.63 in this data, so the four groups sit "
            "along one diagonal, not in four separated corners. They're useful bands for prioritisation, "
            "not four naturally distinct customer types. k=2 (below) shows the same split without that "
            "overstatement."
        )

    st.caption("Usage anomalies (Isolation Forest, 5% contamination) vs. the At Risk flag:")
    anomaly_overlap = filtered.groupby("Usage Anomaly")["At Risk"].mean().reset_index()
    anomaly_overlap["Usage Anomaly"] = anomaly_overlap["Usage Anomaly"].map({True: "Anomaly", False: "Not anomaly"})
    fig = px.bar(anomaly_overlap, x="Usage Anomaly", y="At Risk", labels={"At Risk": "Share also At Risk"})
    st.plotly_chart(fig, width="stretch")

    st.subheader("Usage clustered into 2 vs. 4 segments")
    st.caption(
        "Five raw usage metrics can't be plotted directly, so both use the same two composite axes that "
        "named the clusters. This is the actual logic behind the labels, not an arbitrary PCA projection. "
        "k=2 has the cleanest separation (silhouette 0.40); k=4 trades some separation for more actionable "
        "nuance (silhouette 0.30) -- see the expander above for why."
    )
    c5, c6 = st.columns(2)
    for col, k in zip([c5, c6], [2, 4]):
        with col:
            cluster_col = f"Usage Cluster (k={k})"
            st.markdown(f"**k={k}**")
            counts = filtered[cluster_col].value_counts().reset_index()
            fig = px.bar(counts, x=cluster_col, y="count")
            st.plotly_chart(fig, width="stretch")
            fig = px.scatter(
                filtered, x="Usage Volume", y="Integration Depth", color=cluster_col,
                opacity=0.35, render_mode="webgl",
            )
            st.plotly_chart(fig, width="stretch")

    st.subheader("Where the usage anomalies sit")
    st.caption(
        "The same axes, colored by whether Isolation Forest flagged the account as an unusual usage shape "
        "(not just a low level, a different concept from the At Risk flag)."
    )
    anomaly_plot = filtered.copy()
    anomaly_plot["Usage Anomaly"] = anomaly_plot["Usage Anomaly"].map({True: "Anomaly", False: "Not anomaly"})
    fig = px.scatter(
        anomaly_plot.sort_values("Usage Anomaly"), x="Usage Volume", y="Integration Depth", color="Usage Anomaly",
        color_discrete_map={"Not anomaly": "#DFE1E6", "Anomaly": "#DE350B"},
        opacity=0.5, render_mode="webgl",
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("How this connects to the Risk Categories")
    st.caption(
        "The clusters were built with no knowledge of the Risk Score or Risk Category logic. This checks "
        "whether they agree anyway -- computed live from the full dataset, not filtered by the sidebar."
    )
    at_risk_rate = risk.groupby("Usage Cluster (k=4)")["At Risk"].mean().reindex(
        ["Power users", "Active, shallow integration", "Integration-heavy, moderate usage", "Low engagement"]
    )
    cat_by_cluster = pd.crosstab(risk["Risk Category"], risk["Usage Cluster (k=4)"], normalize="index")

    def top_two(category: str) -> str:
        top = cat_by_cluster.loc[category].sort_values(ascending=False)
        return f"{top.index[0]} ({top.iloc[0]:.0%}), {top.index[1]} ({top.iloc[1]:.0%})"

    st.markdown(
        f"- **At-risk rate by cluster**: Power users {at_risk_rate['Power users']:.1%}, Active/shallow "
        f"integration {at_risk_rate['Active, shallow integration']:.1%}, Integration-heavy/moderate usage "
        f"{at_risk_rate['Integration-heavy, moderate usage']:.1%}, Low engagement "
        f"{at_risk_rate['Low engagement']:.1%}. The two high-volume clusters are almost never at risk; "
        "the two lower-volume clusters carry nearly all of it.\n"
        f"- **High-Value Disengaged** customers come mostly from: {top_two('High-Value Disengaged')}. This "
        "category is specifically defined by high embeddedness, and \"Integration-heavy\" is the cluster "
        "built around that same axis -- two independently-built methods landing on the same distinction.\n"
        f"- **Established & Declining** customers come mostly from: {top_two('Established & Declining')}. "
        "This is the *lower*-embeddedness at-risk group, and it lines up with the lowest-volume, "
        "lowest-depth cluster.\n"
        f"- **New & Struggling** customers come mostly from: {top_two('New & Struggling')}. This category is "
        "defined by tenure, not usage level, so a mixed split across clusters is expected here.\n"
        "- None of this validates that either method predicts churn (there's still no label to check that "
        "against). It shows the two methods agree on who's engaged and who isn't, despite being built "
        "independently and from different logic -- corroboration, not proof."
    )

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
    cutoff_long = results["cutoff"].melt(
        id_vars=["Cutoff %", "Customers flagged"],
        value_vars=["% Enterprise", "% Premium", "% Standard", "% Free"],
        var_name="Plan Type", value_name="Share",
    )
    fig = px.bar(cutoff_long, x="Cutoff %", y="Share", color="Plan Type", barmode="stack")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(results["cutoff"], width="stretch")

    st.markdown("**Embeddedness weight.** Rank correlation and category-flip rate, across Integrations Used weights from 1x to 5x:")
    fig = px.line(
        results["embeddedness"], x="Integrations weight", y="Rank correlation vs. baseline (2x)", markers=True,
    )
    fig.update_yaxes(range=[0, 1.05])
    st.plotly_chart(fig, width="stretch")
    st.dataframe(results["embeddedness"], width="stretch")

    st.markdown("**Urgency coefficient.** Risk Score rank correlation across coefficients from 0.2 to 0.5 (Risk Category doesn't depend on this at all):")
    fig = px.line(
        results["urgency"], x="Urgency coefficient", y="Rank correlation vs. baseline (0.3)", markers=True,
    )
    fig.update_yaxes(range=[0, 1.05])
    st.plotly_chart(fig, width="stretch")
    st.dataframe(results["urgency"], width="stretch")

    st.markdown("**Bootstrap stability.** Per-customer agreement rate with the full-population At Risk flag, across 20 resamples:")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Average agreement", f"{results['bootstrap_mean']:.1%}")
    with col_b:
        fig = px.histogram(results["bootstrap_detail"], nbins=20, labels={"value": "Agreement rate"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

# --- Documentation -----------------------------------------------------------
with tab_docs:
    st.caption("Every finding behind this dashboard, in one place.")
    choice = st.selectbox("Choose a document", list(DOC_FILES))
    doc_path = DOCS_DIR / DOC_FILES[choice]
    if doc_path.exists():
        st.markdown(doc_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"{doc_path} not found yet.")
