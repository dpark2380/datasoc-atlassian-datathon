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
import hashlib
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
try:
    from analysis import reliability_checks, sensitivity_checks  # noqa: E402
except ImportError:
    import reliability_checks  # noqa: E402
    import sensitivity_checks  # noqa: E402

RISK_CSV = ROOT / "analysis" / "customer_risk.csv"
TICKETS_CSV = ROOT / "analysis" / "cleaned_tickets.csv"
USAGE_CSV = ROOT / "references" / "Dataset" / "product_usage.csv"
DOCS_DIR = ROOT / "docs"

PLAN_ORDER = ["Free", "Standard", "Premium", "Enterprise"]
CATEGORY_ORDER = ["Monitor Only", "New & Struggling", "Established & Low Engagement", "High-Value Disengaged"]

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
    "Metric reliability and the trend test": "findings-reliability.md",
    "Sensitivity and robustness checks": "findings-sensitivity.md",
    "Customer success playbook research": "research-cs-playbook-actions.md",
    "Business context research (SEC filings)": "research-differentiators.md",
    "Business context figures, with sources": "research-business-context-figures.md",
    "Deck outline": "deck-outline.md",
}


def _module_version(*modules) -> str:
    """Hash of one or more modules' source, to use as an explicit cache key.

    st.cache_data hashes the wrapped function's own bytecode plus its
    non-underscore args. It does NOT hash the code of functions that function
    calls into from another module, and an underscore-prefixed argument (used
    here for the DataFrames, which are expensive to hash) is excluded from
    the key entirely. A prior version of this cache had no dependency on
    sensitivity_checks.py's contents at all, so a code change there (the
    cutoff_sensitivity rewrite) was not enough to invalidate a stale cached
    result on a long-lived deployed process that survived the redeploy,
    which produced a KeyError when the dashboard's melt() looked for columns
    the stale cached table didn't have. Passing this hash as a normal argument
    forces recomputation whenever any of these modules actually changes.
    """
    combined = b"".join(Path(m.__file__).read_bytes() for m in modules)
    return hashlib.sha256(combined).hexdigest()


def _check_known_values(series: pd.Series, expected: list[str], column: str) -> None:
    """Fail loudly if the data contains labels the app does not know about.

    pd.Categorical silently turns unrecognised values into NaN, which renders
    as a labelled bar of height zero rather than an error. That is worse than
    a crash: a stale file would quietly show an empty category in a chart
    somebody might put in front of judges. This surfaces it instead.
    """
    unknown = sorted(set(series.dropna().unique()) - set(expected))
    if unknown:
        st.error(
            f"`{column}` in analysis/customer_risk.csv contains values this app does not recognise: "
            f"{unknown}. That file is stale or was written by a different version of the pipeline. "
            "Re-run `.venv/bin/python analysis/eda.py` to regenerate it.",
            icon=":material/error:",
        )
        st.stop()


@st.cache_data
def load_data():
    risk = pd.read_csv(RISK_CSV)
    _check_known_values(risk["Plan Type"], PLAN_ORDER, "Plan Type")
    _check_known_values(risk["Risk Category"], CATEGORY_ORDER, "Risk Category")
    risk["Plan Type"] = pd.Categorical(risk["Plan Type"], categories=PLAN_ORDER, ordered=True)
    risk["Risk Category"] = pd.Categorical(risk["Risk Category"], categories=CATEGORY_ORDER, ordered=True)
    # Standardised WITHIN Primary Product, matching how the clustering itself
    # is computed (analysis/eda.py's standardise_within_product). Plotting
    # these on a globally-standardised axis instead would show a "Power
    # users" point sitting in the visually low-volume region just because
    # its product's baseline is lower, which is the exact distortion the
    # within-product fix removed from the clustering in the first place.
    def z_within_product(cols: list[str]) -> pd.Series:
        return risk.groupby("Primary Product", observed=True)[cols].transform(
            lambda s: (s - s.mean()) / (s.std() or 1)
        ).mean(axis=1)

    risk["Usage Volume"] = z_within_product(["Active Days", "Sessions", "Product Actions"])
    risk["Integration Depth"] = z_within_product(["Collaborators", "Integrations Used"])
    tickets = pd.read_csv(TICKETS_CSV)
    usage = pd.read_csv(USAGE_CSV)
    return risk, tickets, usage


@st.cache_data
def load_reliability_results(_usage: pd.DataFrame, code_version: str):
    return {
        "table": reliability_checks.reliability_table(_usage),
        "trend": reliability_checks.trend_permutation_test(_usage),
    }


@st.cache_data
def load_sensitivity_results(_risk: pd.DataFrame, code_version: str):
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

if not plans:
    st.info("Select at least one plan type in the sidebar to see the analysis.", icon=":material/filter_alt:")
    st.stop()

filtered = risk[risk["Plan Type"].isin(plans)]
at_risk = filtered[filtered["At Risk"]]

tab_overview, tab_risk, tab_segments, tab_reliability, tab_robustness, tab_docs = st.tabs(
    ["Overview", "Risk model", "Usage segments (ML)", "Data reliability",
     "Robustness checks", "Documentation"]
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
        st.plotly_chart(fig, width="stretch", key="dash_chart_1")
    with c_ticket2:
        fig = px.bar(tickets["Ticket Channel"].value_counts().reset_index(), x="Ticket Channel", y="count")
        st.plotly_chart(fig, width="stretch", key="dash_chart_2")

    with st.expander("Answering \"you just ignored our data\"", expanded=False):
        st.caption("The strongest single number in the audit, and a direct answer to that question.")
        m1, m2 = st.columns(2)
        m1.metric("Customers with zero tickets", "0 of 8,320")
        m2.metric("Expected under random assignment", "~3,006", "Poisson, λ=1.018")
        st.markdown(
            "- Getting exactly zero is not a coincidence. `customers.csv` is the deduplicated identity "
            "list built FROM the ticket file's email column, not a separate table tickets were randomly "
            "matched to.\n"
            "- The same logic applies to product usage: the exact set of products a customer's tickets "
            "mention matches their `product_usage.csv` rows 100% of the time, for every customer, "
            "including the 114 with 2 products and 4 with 3. That precision only happens if the usage "
            "file was generated per customer per ticket-mentioned product.\n"
            "- **This corrects an earlier version of our own findings**, which called that 100% match "
            "\"a real, if narrow, fact\" about the ticket data. It is not independent evidence of "
            "anything: it is a fact about how the files share a common origin, not about whether any "
            "ticket field is trustworthy.\n"
            "- We did not ignore the data we were given. We reverse engineered how it was built, and "
            "that is what let us tell the difference between what's real (usage) and what's a "
            "generated label (everything else in the ticket file)."
        )

# --- Risk model --------------------------------------------------------------
with tab_risk:
    st.subheader("Usage scales with plan tier (the real signal)")
    st.caption("Active Days by Plan Type. This is genuine, not a data artifact (see Documentation tab).")
    means = risk.groupby("Plan Type", observed=True)["Active Days"].mean().reindex(PLAN_ORDER).reset_index()
    fig = px.bar(means, x="Plan Type", y="Active Days")
    st.plotly_chart(fig, width="stretch", key="dash_chart_3")

    st.subheader("Risk category breakdown")
    st.caption("How many customers fall into each of the four risk categories. Full definitions below the chart.")
    counts = filtered["Risk Category"].value_counts().reindex(CATEGORY_ORDER).reset_index()
    fig = px.bar(counts, x="Risk Category", y="count")
    st.plotly_chart(fig, width="stretch", key="dash_chart_4")
    st.markdown(
        "- **Monitor Only**: not at risk. Usage sits above the bottom quarter for this customer's plan "
        "and product peer group. No action.\n"
        "    - At Risk = Engagement Percentile ≤ 25, where Engagement Percentile is this customer's "
        "Engagement Composite ranked (percentile, 0-100) only against customers on the same Plan Type "
        "and Primary Product.\n"
        "    - Engagement Composite = Active Days, Sessions, and Product Actions, each standardised and "
        "then weighted by its measured reliability (0.92 to 0.98 for these three). See the Data "
        "reliability tab.\n"
        "    - Monitor Only is simply every customer where this condition is false (Engagement "
        "Percentile > 25).\n"
        "- **New & Struggling**: at risk, and recently acquired relative to the rest of the customer "
        "base. Reads as an onboarding problem, not churn.\n"
        "    - Recently acquired = Account Age ≤ the 25th percentile of Account Age across *all* "
        "customers, where Account Age = (2023-05-31 minus Account Created Date), in days.\n"
        "    - This is a relative quartile, not an absolute cutoff like \"under 90 days\": no customer "
        "in this dataset is younger than about 1.5 years by the 2023 usage window, so \"recently "
        "acquired\" means the youngest 25% of the base, not literally new.\n"
        "- **Established & Low Engagement**: at risk, longer-tenured, and either lower plan tier or lower "
        "embeddedness. A real but lower-stakes churn risk.\n"
        "    - Applies when At Risk is true, Recently Acquired is false, and High-Value (defined below) "
        "is also false.\n"
        "- **High-Value Disengaged**: at risk, longer-tenured, and either Enterprise/Premium tier or "
        "heavily integrated (top quartile of Collaborators + Integrations Used). The account most "
        "worth protecting.\n"
        "    - High-Value = Plan Type is Enterprise or Premium, OR Embeddedness Percentile ≥ 75.\n"
        "    - Embeddedness Percentile = the percentile rank (0-100), across *all* customers, of "
        "Collaborators and Integrations Used, each standardised and then weighted by its measured "
        "reliability (0.63 and 0.89, giving a 41/59 split). See the Data reliability tab.\n"
        "    - Applies when At Risk is true, Recently Acquired is false, and High-Value is true."
    )

    st.subheader("Usage by product")
    st.caption("Secondary real cut: Jira and other daily-use tools show higher engagement than Loom.")
    by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
    fig = px.bar(by_product, x="Product", y="Active Days")
    st.plotly_chart(fig, width="stretch", key="dash_chart_5")

    st.subheader("At-risk customers and recommended action (sample)")
    st.caption("The top 50 at-risk customers by Risk Score, each with the specific action assigned to their category.")
    st.dataframe(
        at_risk[
            ["Customer ID", "Plan Type", "Primary Product", "Risk Category", "Risk Score",
             "Active Days", "Embeddedness Percentile", "Recommended Action"]
        ].sort_values("Risk Score", ascending=False).head(50),
        width="stretch",
    )

    with st.expander("Where each recommended action came from", expanded=False):
        st.markdown(
            "The first draft of these was generic: send an email, schedule a check-in. That is not a "
            "solution, so each one was replaced with a documented process from a named Customer Success "
            "platform, each matched to the reason that category is at risk. Full citations "
            "are in the playbook research doc in the Documentation tab.\n\n"
            "**Monitor Only: no action.** Not sourced, and deliberately so. This is the null case. A model "
            "that recommends action on every account is useless, and saying plainly that 6,248 of 8,320 "
            "accounts need nothing is what makes the other three credible.\n\n"
            "**New & Struggling: milestone-tracked onboarding review.** From Gainsight's published "
            "onboarding process: a kickoff with a named owner, customer-side pre-work, and progress "
            "tracked against segment-specific milestones using a report that flags accounts falling "
            "behind. Their adoption workshop has a concrete completion target rather than being an "
            "open-ended demo, and the 30/60/90 day checkpoint is theirs too. Chosen for this category "
            "because these accounts are at risk and recently acquired, which reads as an adoption failure "
            "rather than a relationship in decline. The session material can be Atlassian's own published "
            "Jira Adoption Guide, so it needs no new collateral.\n\n"
            "**High-Value Disengaged: executive business review.** Gainsight, ChurnZero and Vitally "
            "publish near-identical guidance: a quarterly exec-to-exec review of delivered ROI, reserved "
            "for the highest-value segment rather than run for everyone. ChurnZero adds including a "
            "leadership attendee as a signal of commitment, and pairing a technical resource when the "
            "review gets into implementation detail. Chosen for this category because it is the tier "
            "above the size threshold where Atlassian does assign people, so human effort is justified "
            "here and only here. Logged through Jira Product Discovery, which Atlassian's Customer "
            "Success team already uses for account prioritisation, making it a process extension rather "
            "than a new tool.\n\n"
            "**Established & Low Engagement: automated feature-specific play.** The sequence is "
            "ChurnZero's documented low and mid-touch feature adoption play, not an invention: an "
            "automated trigger when usage of a specific feature stalls, an email naming that feature and "
            "its benefit, an in-app message one to two days later, then a complimentary training session "
            "scoped to the unused feature. HubSpot's tech-touch model supports the same routing, keeping "
            "human time for the high-value tier. Chosen for this category because heavy touch is not cost "
            "justified here, and because most accounts at this size have no assigned owner at all, so the "
            "intervention has to be as automatic as the detection."
        )
        st.warning(
            "Three limits to state if asked. These are vendor-published best practices rather than "
            "experimentally proven interventions, and Gainsight and ChurnZero publish them partly as "
            "marketing for their own platforms. No outcome data proves they work on Atlassian's customers "
            "specifically, because this dataset has no churn label. And differentiating the action by "
            "category is our attempt to target responsiveness rather than raw risk, which is the right "
            "instinct per the targeting literature, but the responsiveness assumptions are themselves "
            "unvalidated.",
            icon=":material/balance:",
        )

# --- Usage segments (ML) -----------------------------------------------------
with tab_segments:
    st.subheader("Usage segments (unsupervised, independent of the Risk Score)")
    st.caption(
        "KMeans on standardised usage metrics, discovered from the data rather than hand-picked."
    )

    st.caption("Usage anomalies (Isolation Forest, 5% contamination) vs. the At Risk flag:")
    anomaly_overlap = filtered.groupby("Usage Anomaly")["At Risk"].mean().reset_index()
    anomaly_overlap["Usage Anomaly"] = anomaly_overlap["Usage Anomaly"].map({True: "Anomaly", False: "Not anomaly"})
    fig = px.bar(anomaly_overlap, x="Usage Anomaly", y="At Risk", labels={"At Risk": "Share also At Risk"})
    st.plotly_chart(fig, width="stretch", key="dash_chart_6")

    st.subheader("Usage clustered into 2 vs. 4 segments")
    st.caption(
        "Five raw usage metrics can't be plotted directly, so both use the same two composite axes that "
        "named the clusters. This is the actual logic behind the labels, not an arbitrary PCA projection. "
        "k=2 has the cleanest separation (silhouette 0.40); k=4 trades some separation for more actionable "
        "nuance (silhouette 0.30) -- see how the labels are decided, below."
    )
    for k in [2, 4]:
        cluster_col = f"Usage Cluster (k={k})"
        st.markdown(f"**k={k}**")
        counts = filtered[cluster_col].value_counts().reset_index()
        fig = px.bar(counts, x=cluster_col, y="count")
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch", key=f"cluster_counts_k{k}")

        fig = px.scatter(
            filtered, x="Usage Volume", y="Integration Depth", color=cluster_col,
            opacity=0.35, render_mode="webgl",
        )
        fig.update_traces(marker=dict(size=6))
        dot_traces = list(fig.data)
        fig.data = []

        # Centroids computed on the full, unfiltered population -- these
        # are the actual KMeans cluster centres the labels correspond to.
        # Recomputing them on a sidebar-filtered subset would drift from
        # the real cluster definition (e.g. filtering to Free removes
        # most Power users, so their mean position would no longer
        # represent that cluster).
        centroids = risk.groupby(cluster_col, observed=True)[["Usage Volume", "Integration Depth"]].mean()

        # Label lines/text are plain traces, not annotations, and are added
        # to the figure BEFORE the dot cloud and centroid markers below, so
        # dots always draw on top and stay readable no matter where a label
        # line crosses. Each label is pushed outward from the data's center
        # of mass toward blank space (the cloud runs along the diagonal),
        # and labels sharing the same outward quadrant are staggered further
        # apart so they don't sit on top of each other.
        x_range = filtered["Usage Volume"].max() - filtered["Usage Volume"].min()
        y_range = filtered["Integration Depth"].max() - filtered["Integration Depth"].min()
        data_center = filtered[["Usage Volume", "Integration Depth"]].mean()
        quadrant_seen: dict[tuple[bool, bool], int] = {}
        for label, row in centroids.iterrows():
            dx = row["Usage Volume"] - data_center["Usage Volume"]
            dy = row["Integration Depth"] - data_center["Integration Depth"]
            quadrant = (dx >= 0, dy >= 0)
            stagger = quadrant_seen.get(quadrant, 0)
            quadrant_seen[quadrant] = stagger + 1
            reach = 0.22 + stagger * 0.14
            label_x = row["Usage Volume"] + (reach * x_range if dx >= 0 else -reach * x_range)
            label_y = row["Integration Depth"] + (reach * y_range if dy >= 0 else -reach * y_range)
            fig.add_trace(go.Scatter(
                x=[row["Usage Volume"], label_x], y=[row["Integration Depth"], label_y],
                mode="lines", line=dict(color="red", width=1.5), showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=[label_x], y=[label_y], mode="text", text=[f"<b>{label}</b>"],
                textfont=dict(color="red", size=14), showlegend=False, hoverinfo="skip",
            ))

        for trace in dot_traces:
            fig.add_trace(trace)
        fig.add_trace(go.Scatter(
            x=centroids["Usage Volume"], y=centroids["Integration Depth"],
            mode="markers", marker=dict(symbol="circle", size=14, color="red", line=dict(width=2, color="white")),
            name="Centroid", showlegend=False,
        ))
        fig.update_layout(height=650)
        st.plotly_chart(fig, width="stretch", key=f"cluster_scatter_k{k}")

    st.markdown("#### How these labels are decided")
    st.markdown(
        "- KMeans is fit first, purely on the numbers. It has no idea what \"Power users\" means, it "
        "just finds groups of customers with similar usage patterns.\n"
        "- Each cluster's centroid (its average member) is reduced to two scores:\n"
        "    - **Usage volume**: Active Days, Sessions, Product Actions, standardised and averaged.\n"
        "    - **Integration depth**: Collaborators, Integrations Used, standardised and averaged.\n"
        "- Clusters are ranked against each other on both scores, split into a top half and bottom half "
        "on each axis.\n"
        "- Labels are computed from where each cluster actually sits every time the pipeline reruns, not "
        "hardcoded to a cluster number (KMeans' own numbering is arbitrary)."
    )
    st.markdown(
        "**Where each label sits on the chart** (x-axis = Usage Volume, y-axis = Integration Depth):\n"
        "- **Top-right** (high volume, high depth) → Power users\n"
        "- **Bottom-right** (high volume, low depth) → Active, shallow integration\n"
        "- **Top-left** (low volume, high depth) → Integration-heavy, moderate usage\n"
        "- **Bottom-left** (low volume, low depth) → Low engagement"
    )
    st.markdown(
        "**Added after review, standardising within Primary Product instead of globally:**\n"
        "- Products have different usage baselines (Jira ~10.0 avg active days/month vs. Loom ~6.7).\n"
        "- Standardising globally meant a typical Loom customer looked lower on every metric purely from "
        "which product they use, not from being less engaged.\n"
        "- Before the fix: Loom was 26.7% of the lowest-usage cluster against its 19.2% base rate.\n"
        "- After the fix: every product lands within a point of its base rate.\n"
        "- Cost of the fix: essentially none (silhouette 0.304 → 0.302 at k=4).\n"
        "- The plan-tier corroboration below is unaffected, since Plan Type varies independently of "
        "Primary Product."
    )

    st.info(
        "The clusters visibly overlap, and that is real rather than an artifact of squashing five "
        "dimensions into two. We checked: silhouette measured on just these two plotted axes is 0.46 at "
        "k=2, slightly higher than the 0.40 measured in the full five-dimensional space the clustering "
        "actually runs in. The plot is not hiding separation. The cause is the 0.63 correlation between "
        "usage volume and integration depth: this data is one continuous diagonal cloud, so k-means is "
        "cutting a continuum rather than finding islands that were already there. That is why these are "
        "described as bands for prioritisation and not as four naturally distinct customer types.",
        icon=":material/query_stats:",
    )

    st.subheader("Cluster composition by plan and product")
    st.caption(
        "What this chart shows: for each of the 4 usage clusters, what share of its customers fall into "
        "each Plan Type or Primary Product. It answers the most likely objection to this whole clustering "
        "exercise: \"aren't these just your plan tiers?\" The answer is mostly yes on plan, and almost not "
        "at all on product, both shown below with the actual numbers. Computed live from the full dataset."
    )
    plan_mix = pd.crosstab(risk["Usage Cluster (k=4)"], risk["Plan Type"], normalize="index") * 100
    product_mix = pd.crosstab(risk["Usage Cluster (k=4)"], risk["Primary Product"], normalize="index") * 100
    product_base = risk["Primary Product"].value_counts(normalize=True) * 100

    mix_choice = st.radio(
        "Show cluster composition by", options=["Plan Type", "Primary Product"], horizontal=True,
        label_visibility="collapsed", key="cluster_mix_choice",
    )
    mix = plan_mix if mix_choice == "Plan Type" else product_mix
    long = mix.reset_index().melt(id_vars="Usage Cluster (k=4)", var_name=mix_choice, value_name="Share of cluster (%)")
    fig = px.bar(long, x="Usage Cluster (k=4)", y="Share of cluster (%)", color=mix_choice, barmode="stack")
    st.plotly_chart(fig, width="stretch", key="cluster_mix_chart")

    integration_heavy = plan_mix.loc["Integration-heavy, moderate usage"]
    low_engagement = plan_mix.loc["Low engagement"]
    st.markdown(
        f"- **Plan tier explains most of it.** The Integration-heavy cluster is "
        f"{integration_heavy['Enterprise'] + integration_heavy['Premium']:.0f}% Enterprise or Premium. "
        f"Low engagement is {low_engagement['Free'] + low_engagement['Standard']:.0f}% Free or Standard. "
        "These clusters track what a customer pays for.\n"
        f"- **Product explains almost none of it.** Every product sits within a point of its "
        f"{product_base.min():.0f} to {product_base.max():.0f}% base rate in every cluster (e.g. Loom is "
        f"{product_mix.loc['Low engagement', 'Loom']:.0f}% of Low engagement, base rate "
        f"{product_base['Loom']:.0f}%). That's not an accident: the five usage metrics are standardised "
        "within each Primary Product before clustering, precisely so a naturally lower-touch product like "
        "Loom doesn't get its customers lumped into 'low engagement' just for using a naturally "
        "lower-touch product.\n"
        "- **The plan-tier result is evidence, not a defect.** KMeans was given five usage metrics and "
        "nothing else. It never saw Plan Type or Primary Product. Reconstructing plan bands at that "
        "concentration from behaviour alone is independent confirmation that the usage-to-plan "
        "relationship the risk model depends on is real, since a second method found it without being "
        "pointed at it.\n"
        "- **Why the clustering is not split by product.** Splitting would give five separate "
        "clusterings averaging about 1,664 customers each, which weakens every cluster to remove a "
        "distortion the numbers above show is small. The clustering's job here is corroboration rather "
        "than discovering new segments, and the risk model already does the peer-group comparison by "
        "Plan Type and Product where it actually matters."
    )

    st.subheader("Where the usage anomalies sit")
    st.caption(
        "The same axes, colored by whether Isolation Forest flagged the account as an unusual usage shape "
        "(an unusual shape of usage, which is a different concept from the At Risk flag)."
    )
    anomaly_plot = filtered.copy()
    anomaly_plot["Usage Anomaly"] = anomaly_plot["Usage Anomaly"].map({True: "Anomaly", False: "Not anomaly"})
    fig = px.scatter(
        anomaly_plot.sort_values("Usage Anomaly"), x="Usage Volume", y="Integration Depth", color="Usage Anomaly",
        color_discrete_map={"Not anomaly": "#DFE1E6", "Anomaly": "#DE350B"},
        opacity=0.5, render_mode="webgl",
    )
    st.plotly_chart(fig, width="stretch", key="dash_chart_7")

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
        # Tolerate a category that isn't present rather than taking the whole
        # page down: every tab body executes on each run, so one lookup error
        # here would blank the entire dashboard.
        if category not in cat_by_cluster.index:
            return "not present in this data"
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
        f"- **Established & Low Engagement** customers come mostly from: {top_two('Established & Low Engagement')}. "
        "This is the *lower*-embeddedness at-risk group, and it lines up with the lowest-volume, "
        "lowest-depth cluster.\n"
        f"- **New & Struggling** customers come mostly from: {top_two('New & Struggling')}. This category is "
        "defined by tenure, not usage level, so a mixed split across clusters is expected here.\n"
        "- None of this validates that either method predicts churn (there's still no label to check that "
        "against). It shows the two methods agree on who's engaged and who isn't, despite being built "
        "independently and from different logic -- corroboration, not proof."
    )

# --- Data reliability ---------------------------------------------------------
with tab_reliability:
    st.subheader("We ran the same audit on our own data")
    st.caption(
        "The ticket audit showed that file is random. This is the same audit turned on the usage data "
        "we did build the model on. It changed how the model is weighted and what one category is called. "
        "Computed live from product_usage.csv."
    )
    reliability = load_reliability_results(usage, _module_version(reliability_checks))

    st.markdown("#### How much of each metric is signal")
    st.markdown(
        "A metric is only useful if it measures something stable about a customer rather than which month "
        "you happened to look. The intraclass correlation splits each metric's variance into the part that "
        "separates customers from each other and the part that just moves month to month. The model averages "
        "5 months per customer, so the last column is the figure that applies to it."
    )
    st.dataframe(reliability["table"], width="stretch")

    rel_col = [c for c in reliability["table"].columns if c.startswith("Reliability")][0]
    fig = px.bar(
        reliability["table"].sort_values(rel_col), x="Metric", y=rel_col,
        labels={rel_col: "Reliability of the 5-month average"},
    )
    fig.update_yaxes(range=[0, 1.05])
    st.plotly_chart(fig, width="stretch", key="dash_chart_8")

    st.markdown(
        "Collaborators is the weakest input by a clear margin. In any single month it is mostly noise: its "
        "within-customer variance is larger than its between-customer variance, meaning the same customer's "
        "collaborator count moves around more than customers differ from each other.\n\n"
        "Every composite in the model now weights each metric by its measured reliability instead of by a "
        "hand-picked number. Stated plainly, because it would be easy to imply otherwise: this does **not** "
        "reduce Collaborators' influence. The old scheme multiplied raw values, so the effective split was "
        "38% Collaborators to 62% Integrations Used, driven by raw scale rather than intent. Reliability "
        "weighting gives Collaborators 41%. The gain is that the split is now measured and explainable, not "
        "that a noisy variable was removed. Applying it moved exactly one customer between categories."
    )

    st.divider()
    st.markdown("#### Trend test on the 5-month panel")
    trend = reliability["trend"]
    st.markdown(
        "The obvious question about a 5-month panel is why there is no trend analysis. We tested for one. "
        f"We fit a slope through each customer's 5 monthly Active Days values ({trend['customers']:,} customers "
        "with complete months), then did the same after shuffling each customer's months into a random order. "
        "Shuffling destroys any real time ordering, so if customers had real trends the shuffled slopes would "
        "be visibly flatter."
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Real slope spread (SD)", f"{trend['real_slope_sd']:.4f}")
    m2.metric("Shuffled slope spread (SD)", f"{trend['shuffled_slope_sd']:.4f}")
    m3.metric("Ratio", f"{trend['sd_ratio']:.3f}", "1.0 means indistinguishable from noise")

    st.markdown(
        f"A ratio of 1.0 means real slopes are indistinguishable from slopes fitted to randomly reordered "
        f"data. At {trend['sd_ratio']:.3f}, that is what we have.\n\n"
        f"The split-half check says the same thing from another angle. A real trend persists, so a customer "
        f"trending up in the first half should still be trending up in the second. The actual correlation "
        f"between first-half and second-half slopes is **{trend['split_half_corr']:.3f}**. It is negative, "
        f"which is mean reversion: a customer above their own average one month tends to be below it the "
        f"next. That is fluctuation around a stable level, not a trajectory. Consistent with both, "
        f"{trend['share_declining']:.1%} of customers look like they are declining and "
        f"{trend['share_rising']:.1%} look like they are rising, close to the even split noise would produce."
    )
    st.markdown(
        "Two consequences. Every slope, percent-change, or trend feature derivable from this panel is "
        "measuring noise. And a category previously called \"Established & Declining\" claimed a trajectory "
        "the data cannot support, so it is now \"Established & Low Engagement\", describing a level rather "
        "than a direction. The risk model compares a customer's usage against their peer group rather than "
        "against their own history, and this is the reason why."
    )


# --- Robustness checks -------------------------------------------------------
with tab_robustness:
    st.subheader("Parameter sensitivity")
    st.caption(
        "The Risk Score's parameters (25% cutoff, 2x Integrations weight, 0.3 urgency coefficient) were chosen "
        "by judgment, since there's no churn label to fit them against. The question this whole tab answers: "
        "does the exact parameter choice matter, or would a reasonable alternative flag a very different set "
        "of customers rather than just fine-tune the result? Four checks below, one per parameter, plus a "
        "resampling check on the flag itself."
    )
    results = load_sensitivity_results(risk, _module_version(sensitivity_checks))

    st.markdown("#### At Risk cutoff")
    st.caption("How the four-way Risk Category split changes across cutoffs from 15% to 35%:")
    st.caption(
        "An earlier version of this chart compared the tier mix of who gets flagged and reported it as "
        "stable. That was an identity, not a finding: Engagement Percentile is ranked separately within "
        "each Plan Type x Product group, so any cutoff selects that same share of every group by "
        "construction, and the flagged population's tier mix is guaranteed to match the whole "
        "population's regardless of cutoff. It has been replaced with what can actually move: category, "
        "which also depends on tenure and the high-value gate."
    )
    cutoff_long = results["cutoff"].melt(
        id_vars=["Cutoff %"],
        value_vars=["Monitor Only", "New & Struggling", "Established & Low Engagement", "High-Value Disengaged"],
        var_name="Risk Category", value_name="Customers",
    )
    fig = px.bar(cutoff_long, x="Cutoff %", y="Customers", color="Risk Category", barmode="stack")
    st.plotly_chart(fig, width="stretch", key="dash_chart_9")
    st.dataframe(results["cutoff"], width="stretch")
    st.caption(
        "Every category grows roughly in proportion as the cutoff loosens, and the ratios between "
        "categories stay close to stable (New & Struggling to Established & Low Engagement runs 0.57 to "
        "0.59; High-Value Disengaged to the same runs 0.73 to 0.74). That stability is not guaranteed by "
        "the definition, since it depends on the tenure and embeddedness mix of the customers each wider "
        "cutoff adds."
    )

    st.markdown("#### Embeddedness weight")
    st.caption("Rank correlation and category-flip rate, across Integrations Used weights from 1x to 5x:")
    fig = px.line(
        results["embeddedness"], x="Integrations weight", y="Rank correlation vs. baseline (2x)", markers=True,
    )
    fig.update_yaxes(range=[0, 1.05])
    st.plotly_chart(fig, width="stretch", key="dash_chart_10")
    st.dataframe(results["embeddedness"], width="stretch")

    st.markdown("#### Urgency coefficient")
    st.caption("Risk Score rank correlation across coefficients from 0.2 to 0.5. Risk Category doesn't depend on this at all:")
    fig = px.line(
        results["urgency"], x="Urgency coefficient", y="Rank correlation vs. baseline (0.3)", markers=True,
    )
    fig.update_yaxes(range=[0, 1.05])
    st.plotly_chart(fig, width="stretch", key="dash_chart_11")
    st.dataframe(results["urgency"], width="stretch")

    st.markdown("#### Bootstrap stability")
    st.caption("Per-customer agreement rate with the full-population At Risk flag, across 20 resamples:")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Average agreement", f"{results['bootstrap_mean']:.1%}")
    with col_b:
        fig = px.histogram(results["bootstrap_detail"], nbins=20, labels={"value": "Agreement rate"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", key="dash_chart_12")

# --- Documentation -----------------------------------------------------------
with tab_docs:
    st.caption("Every finding behind this dashboard, in one place.")
    choice = st.selectbox("Choose a document", list(DOC_FILES))
    doc_path = DOCS_DIR / DOC_FILES[choice]
    if doc_path.exists():
        st.markdown(doc_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"{doc_path} not found yet.")
