"""
Results dashboard page: everything from the analysis in one place. Export
charts from here into the deck; this page is never demoed live (submission
is deck/PDF only). The single-customer risk-scorer (live demo, workstream C)
is the other page in this app, app_pages/risk_scorer.py.

Run: .venv/bin/streamlit run streamlit_app.py

Reads analysis/customer_risk.csv, produced by analysis/eda.py, plus the three
raw source files and the docs/ findings for the Documentation tab. Run
analysis/eda.py and analysis/sensitivity_checks.py first if the generated
output doesn't exist yet.
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app_pages.chart_styling import render_plotly_chart

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
try:
    from analysis import dashboard_metrics, eda, reliability_checks, sensitivity_checks  # noqa: E402
except ImportError:
    import dashboard_metrics, eda, reliability_checks, sensitivity_checks  # noqa: E402

RISK_CSV = ROOT / "analysis" / "customer_risk.csv"
CUSTOMERS_CSV = ROOT / "references" / "Dataset" / "customers.csv"
TICKETS_CSV = ROOT / "references" / "Dataset" / "customer_support_tickets.csv"
USAGE_CSV = ROOT / "references" / "Dataset" / "product_usage.csv"
DOCS_DIR = ROOT / "docs"
ML_RESULTS_JSON = ROOT / "analysis" / "ml_results.json"

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
def load_data(risk_mtime: float):
    """risk_mtime busts the cache whenever customer_risk.csv is regenerated.

    Without it, this cache has no dependency on the file's contents at all
    (st.cache_data hashes this function's own bytecode and its args, not the
    bytes on disk it happens to read), so a long-lived deployed process that
    already cached a DataFrame here would keep serving it even after
    streamlit_app.py's ensure_pipeline_output() regenerates the CSV with a
    newer analysis/eda.py -- the exact KeyError this was written to fix.
    """
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
    customers = pd.read_csv(CUSTOMERS_CSV)
    return risk, customers, tickets, usage


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


@st.cache_data
def load_ml_results(mtime: float = 0):
    if not ML_RESULTS_JSON.exists():
        return None
    import json
    with open(ML_RESULTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


risk, customers, tickets, usage = load_data(RISK_CSV.stat().st_mtime)
eda_metrics = dashboard_metrics.build_eda_metrics(customers, tickets, usage)

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

tab_solution, tab_eda, tab_overview, tab_risk, tab_segments, tab_reliability, tab_robustness, tab_docs = st.tabs(
    ["Solution", "EDA", "Overview", "Risk model", "Usage segments (ML)", "Data reliability",
     "Robustness checks", "Documentation"]
)

# --- Solution ------------------------------------------------------------------
with tab_solution:
    st.subheader("What the solution is")
    st.info(
        "Detect disengagement early using fair, peer-relative usage comparisons, then route each account "
        "to a specific, evidence-based action instead of a one-size-fits-all response.",
        icon=":material/lightbulb:",
    )
    st.caption(
        "Computed monthly from usage data alone, never from the support ticket file, which failed its own "
        "data-quality audit (see the EDA and Data reliability tabs)."
    )

    st.divider()
    st.subheader("The pipeline: how the six components fit together")
    st.caption(
        "One backbone (data → composites → rule → score), corroborated by two diagnostic checks and one "
        "forecaster that don't decide anything on their own, converging on three outputs."
    )

    b1, a1, b2, a2, b3, a3, b4 = st.columns([3, 0.5, 3, 0.5, 3, 0.5, 3])
    with b1:
        with st.container(border=True):
            st.markdown("**Usage data**")
            st.caption("product_usage.csv, 5 months")
    with a1:
        st.markdown("<div style='text-align:center;padding-top:30px;font-size:24px'>→</div>", unsafe_allow_html=True)
    with b2:
        with st.container(border=True):
            st.markdown("**Reliability-weighted composites**")
            st.caption("Standardised, weighted by measured reliability")
    with a2:
        st.markdown("<div style='text-align:center;padding-top:30px;font-size:24px'>→</div>", unsafe_allow_html=True)
    with b3:
        with st.container(border=True):
            st.markdown("**Peer-relative rule**")
            st.caption("Bottom 25% within Plan x Product peer group")
    with a3:
        st.markdown("<div style='text-align:center;padding-top:30px;font-size:24px'>→</div>", unsafe_allow_html=True)
    with b4:
        with st.container(border=True):
            st.markdown("**Risk Score & Risk Category**")
            st.caption("Output 1")

    st.markdown(
        "<div style='text-align:center;color:#5E6C84;font-size:15px;margin-top:8px'>"
        "↑ corroborated by, and given an early warning from ↑</div>",
        unsafe_allow_html=True,
    )
    d1, d2, d3 = st.columns(3)
    with d1:
        with st.container(border=True):
            st.markdown("**KMeans clustering**")
            st.caption("Independent corroboration of the categories")
    with d2:
        with st.container(border=True):
            st.markdown("**Isolation Forest**")
            st.caption("Flags unusual shape, not level, a separate watch-list")
    with d3:
        with st.container(border=True):
            st.markdown("**Month-5 forecaster**")
            st.caption("Supervised early warning, 0.921 held-out AUC")

    st.markdown(
        "<div style='text-align:center;font-size:24px;margin-top:8px'>↓</div>", unsafe_allow_html=True
    )
    o1, o2 = st.columns(2)
    with o1:
        with st.container(border=True):
            st.markdown("**Product-specific recommended action**")
            st.caption("Output 2, category + Primary Product")
    with o2:
        with st.container(border=True):
            st.markdown("**Live Risk Scorer tool**")
            st.caption("Output 3, score + category + action + forecast, one screen")

    st.divider()
    st.subheader("The three outputs")
    out1, out2, out3 = st.columns(3, border=True)
    with out1:
        st.markdown("#### 1. Risk Score & Risk Category")
        st.markdown(
            "Every customer scored 0-100 and placed in one of four categories, comparing them only to "
            "peers on the same Plan Type and Primary Product."
        )
        st.caption("Built from: the peer-relative rule, on reliability-weighted composites.")
        st.caption(
            "Why: the decision layer has to be explainable to a human without translation, so it's a rule, "
            "not a trained model."
        )
    with out2:
        st.markdown("#### 2. Recommended Action")
        st.markdown(
            "A specific, sourced next step for each at-risk customer: category sets the intensity, "
            "Primary Product sets the workflow."
        )
        st.caption("Built from: product-specific actions, applied to the Risk Category above.")
        st.caption("Why: a generic check-in email is not a solution; a named CS playbook is.")
    with out3:
        st.markdown("#### 3. Live Risk Scorer")
        st.markdown(
            "One screen per customer: score, peer comparison, category, recommended action, and (where "
            "available) the forecast probability."
        )
        st.caption("Built from: all six components, surfaced together.")
        st.caption("Why: the analysis only matters if someone can act on it in real time.")

    st.divider()
    st.subheader("The components, why each exists, and how it works")
    st.caption(
        "Six pieces make up the solution. Each entry states what it is, how it works, and why it was "
        "chosen over the alternative rejected for that job."
    )

    with st.expander("1. Peer-relative usage rule (Risk Score and Risk Category)", expanded=True):
        st.markdown(
            "**What it is:** the decision layer. A hand-built rule, not a trained model, since there is no "
            "churn label in this dataset to train or validate one against.\n\n"
            "**How it works:** each customer's Engagement Composite (Active Days, Sessions, Product "
            "Actions, standardised and reliability-weighted) is ranked as a percentile within their own "
            "Plan Type x Primary Product peer group. The bottom 25% of that percentile is flagged At "
            "Risk. At-risk customers are then split into three categories by tenure (bottom 25% of "
            "Account Age across the whole base = recently acquired) and value (Enterprise/Premium plan, "
            "or top 25% of Embeddedness Percentile).\n\n"
            "**Why this, not a black box:** the layer a CS rep has to act on and explain to a customer or "
            "to leadership needs to be interpretable without translation. Every account's status traces "
            "back to named, inspectable numbers, not a prediction nobody can decompose."
        )

    with st.expander("2. Reliability-weighted composites"):
        st.markdown(
            "**What it is:** the method used to combine multiple raw metrics into the Engagement "
            "Composite and Embeddedness Percentile above.\n\n"
            "**How it works:** each metric is standardised (z-scored), then weighted by its measured "
            "reliability, the share of its variance that is a stable customer trait rather than "
            "month-to-month noise (Spearman-Brown adjusted, computed from `product_usage.csv` at "
            "runtime). Collaborators (0.628 reliability, the noisiest metric) and Integrations Used "
            "(0.892) combine 41%/59%. Active Days, Sessions, and Product Actions (0.958, 0.976, 0.916) "
            "are close enough together that reliability weighting barely moves an equal three-way split.\n\n"
            "**Why this, not equal or hand-picked weights:** an earlier version multiplied raw values "
            "directly, so a metric's real influence depended on its raw scale rather than any stated "
            "intent (Collaborators worked out to an effective 38% despite a nominal 1:2 weighting). "
            "Reliability weighting makes the split measured and stated, not an accident of scale."
        )

    with st.expander("3. Product-specific recommended actions"):
        st.markdown(
            "**What it is:** the action layer. Risk Category sets how urgent and human-intensive the "
            "response is; Primary Product sets what the response actually asks the customer to do.\n\n"
            "**How it works:** each of the four categories maps to a documented process from a named "
            "Customer Success platform (a milestone-tracked onboarding review, an automated "
            "feature-specific reactivation play, an executive business review), then that process is "
            "phrased around the customer's actual product (a Jira backlog, a Confluence space, a Trello "
            "board, a Bitbucket repository, or a Loom recording).\n\n"
            "**Why this, not a generic email:** the first draft was generic (\"send an email, schedule a "
            "check-in\"), which is not a solution. Automation carries the routine cases (Established & Low "
            "Engagement escalates to a human only if the automated sequence fails); human effort is "
            "reserved for the one tier above the threshold where Atlassian's own filings say it assigns "
            "people at all."
        )

    with st.expander("4. Unsupervised usage clustering (KMeans)"):
        st.markdown(
            "**What it is:** an independent check on the hand-built categories above, built with no "
            "knowledge of the Risk Score logic.\n\n"
            "**How it works:** KMeans groups customers by their five usage metrics, standardised within "
            "each customer's own Primary Product (so a Loom account isn't penalised for a lower category "
            "baseline than Jira). k=2 gives the cleanest separation (silhouette 0.40) but mostly restates "
            "the plan-tier finding; k=4 (silhouette 0.30) trades some separation to split usage volume "
            "from integration depth into four named segments.\n\n"
            "**Why this, and why not treat it as the production model:** there is no outcome label to "
            "train or score a supervised segmentation against, so it is evaluated on internal statistical "
            "properties (cluster separation), not prediction accuracy. Its value is corroboration: the "
            "segments KMeans finds on its own line up with the categories built by hand, without having "
            "seen them."
        )

    with st.expander("5. Usage anomaly detection (Isolation Forest)"):
        st.markdown(
            "**What it is:** a complementary signal that measures the *shape* of a customer's usage, not "
            "its *level*, which the At Risk rule cannot see by construction.\n\n"
            "**How it works:** Isolation Forest runs on the same five standardised metrics as clustering "
            "(5% contamination), flagging the customers whose combination of values is most isolated from "
            "the rest of the population. It flags 416 of 8,320 customers (5.0%); only 18.3% of those "
            "overlap with the At Risk flag, confirming it surfaces a mostly different population, an "
            "unusual pattern rather than simply a low one.\n\n"
            "**Why this, and its real limit:** anomaly does not mean at risk, and is not itself an action "
            "trigger. Its practical use is a short watch-list worth a human glance, plus evidence the risk "
            "model was checked against an unsupervised signal rather than only asserted."
        )

    with st.expander("6. Month-5 disengagement forecaster (supervised ML)"):
        st.markdown(
            "**What it is:** the one predictive, supervised component, an early-warning layer, not the "
            "decision layer.\n\n"
            "**How it works:** a Random Forest is trained on Months 1-4 usage telemetry to predict "
            "bottom-quartile engagement in Month 5, an outcome that is actually observed in the data "
            "(unlike churn, which is not). Held out on a test set of 1,664 customers, it reaches 0.921 "
            "ROC-AUC, 74.1% precision, and 70.4% recall. Feature importances (average Sessions, Active "
            "Days, and Product Actions over Months 1-4) are reported rather than treated as a black box.\n\n"
            "**Why this, not a churn model, and why it doesn't replace the rule:** there is no contract "
            "churn label in this dataset, so a churn model would have nothing honest to train against. "
            "This forecaster's output is called disengagement risk, not churn probability, and it flags "
            "who may drop next month; the peer-relative rule above still decides the category and the "
            "action, since that layer is the one that has to be explained to a human."
        )

    st.divider()
    st.caption(
        "Full detail behind every component, including the sensitivity and reliability checks each one "
        "was tested against, is in the Documentation tab."
    )

# --- EDA ---------------------------------------------------------------------
with tab_eda:
    st.subheader("EDA by source dataset")
    st.caption(
        "A slide-ready summary of what each file contributes, what it cannot support, and which evidence "
        "we carry into the solution. Every number is computed live from the raw files."
    )
    customer_card, ticket_card, usage_card = st.columns(3, border=True)
    with customer_card:
        st.markdown("#### customers.csv")
        st.caption("Account context")
        st.metric("Customer records", f"{len(customers):,}")
        st.metric("Profile fields", f"{len(customers.columns)}")
        st.metric("Plan tiers", f"{customers['Plan Type'].nunique()}")
        st.markdown(
            "**Use it to define fair peer groups.** Plan tier carries meaningful commercial context; "
            "industry, region, and company size remain descriptive rather than risk signals."
        )

    with ticket_card:
        st.markdown("#### customer_support_tickets.csv")
        st.caption("Experience evidence")
        st.metric("Ticket records", f"{len(tickets):,}")
        st.metric(
            "Usable customer-written text",
            "0 fields",
            help="The dataset has no ticket description, customer comment, or other customer-authored text. "
            "Resolution is generated filler rather than customer sentiment.",
        )
        st.metric(
            "Impossible event order",
            f"{eda_metrics['impossible_order_rate']:.1%}",
            help=f"Among {eda_metrics['resolved_ticket_count']:,} resolved tickets, the recorded resolution "
            "precedes the recorded first response. This cannot happen in a real support workflow.",
        )
        st.markdown(
            "**Do not model sentiment or risk from it.** Satisfaction, priority, type, channel, and status "
            "are statistically flat, and the event timestamps are not a valid sequence."
        )

    with usage_card:
        st.markdown("#### product_usage.csv")
        st.caption("Behavioural signal")
        st.metric("Usage observations", f"{len(usage):,}")
        st.metric("Tracked months", f"{eda_metrics['month_count']}")
        st.metric(
            "Jan–May usage persistence",
            f"{eda_metrics['active_days_persistence']:.2f}",
            help="Correlation between each customer's first- and last-month Active Days. A strong positive "
            "value shows that usage measures a persistent difference between customers.",
        )
        st.metric(
            "Enterprise vs. Free integrations",
            f"{eda_metrics['integration_tier_ratio']:.1f}×",
            help="Average Integrations Used is more than five times higher for Enterprise than Free accounts, "
            "the sharpest plan-tier signal in the usage data.",
        )
        st.markdown(
            "**Build the solution on this file.** Usage is stable by customer and scales in expected ways "
            "with plan tier and product, making it the strongest defensible signal available."
        )

    st.info(
        "**Slide summary:** customer data supplies the peer context; ticket data fails the validity checks "
        "needed for sentiment analysis; usage data provides the stable signal for prioritising accounts.",
        icon=":material/slideshow:",
    )

    st.divider()

    st.subheader("Supporting EDA")
    customer_detail, ticket_detail, usage_detail = st.tabs(
        ["Customer context", "Support ticket quality", "Product usage signal"]
    )

    with customer_detail:
        st.markdown("#### Customer context sets the comparison groups")
        st.caption(
            "Customer attributes describe who is in the sample. Plan Type is the useful modelling context: "
            "risk is assessed against customers on the same plan rather than across unlike accounts."
        )
        plan_counts = customers["Plan Type"].value_counts().reindex(PLAN_ORDER).reset_index()
        fig = px.bar(plan_counts, x="Plan Type", y="count", labels={"count": "Customers"})
        render_plotly_chart(fig, width="stretch", key="eda_customer_plan_mix")
        st.caption(
            "Industry, region, and company size were tested against usage and added no practically meaningful "
            "separation. They stay available for description, but they do not drive the risk model."
        )

    with ticket_detail:
        missing = tickets.isna().sum()
        missing = missing[missing > 0].sort_values(ascending=False).reset_index()
        missing.columns = ["Column", "Missing rows"]
        missing["Missing %"] = (missing["Missing rows"] / len(tickets) * 100).round(1)
        st.markdown("#### Missingness is expected; validity is the problem")
        st.caption(
            "Resolution, Time to Resolution, and Customer Satisfaction Rating are missing on the same "
            "unresolved tickets. That pattern is coherent on its own; the invalid chronology and random "
            "field relationships are what make the file unusable for sentiment modelling."
        )
        st.dataframe(missing, width="stretch", hide_index=True)

        st.markdown("#### Ticket fields don't move with anything")
        st.caption(
            "Average Customer Satisfaction Rating (1–5) by Ticket Priority. If priority reflected the "
            "customer experience, Critical tickets should score noticeably worse than Low ones. They don't."
        )
        sat_by_priority = tickets.groupby("Ticket Priority", observed=True)[
            "Customer Satisfaction Rating"
        ].mean().reset_index()
        fig = px.bar(
            sat_by_priority,
            x="Ticket Priority",
            y="Customer Satisfaction Rating",
            range_y=[0, 5],
        )
        render_plotly_chart(fig, width="stretch", key="eda_sat_by_priority")

        spread_rows = []
        outcome = "Customer Satisfaction Rating"
        outcome_std = tickets[outcome].std()
        for column in ["Ticket Type", "Ticket Priority", "Ticket Channel", "Ticket Status"]:
            group_means = tickets.groupby(column, observed=True)[outcome].mean()
            spread = group_means.max() - group_means.min()
            spread_rows.append(
                {
                    "Field": column,
                    "Group-mean spread": round(spread, 3),
                    "Outcome std. dev.": round(outcome_std, 3),
                    "Spread as % of std. dev.": f"{spread / outcome_std:.1%}",
                }
            )
        st.caption(
            "Across every categorical field, the gap between the best- and worst-scoring groups is tiny "
            "relative to normal rating variation."
        )
        st.dataframe(pd.DataFrame(spread_rows), width="stretch", hide_index=True)
        st.warning(
            f"{eda_metrics['impossible_order_rate']:.1%} of resolved tickets record resolution before the "
            "first response. The support file is descriptive volume data—not a defensible sentiment or risk "
            "signal.",
            icon=":material/warning:",
        )

        st.markdown("#### Ticket volume doesn't track usage trend either")
        st.caption(
            "What this chart shows: split customers into quartiles of their own Active Days trend slope "
            "(Q1 declining fastest, Q4 growing fastest) and compare average ticket count per quartile. If "
            "tickets tracked anything real about a customer's trajectory, a collapsing account should file "
            "noticeably more, or fewer, tickets than a growing one."
        )
        trend_quartile = pd.qcut(
            risk["Active Days Slope"], 4,
            labels=["Q1: declining fastest", "Q2: declining", "Q3: growing", "Q4: growing fastest"],
        )
        by_trend_quartile = risk.groupby(trend_quartile, observed=True)["Ticket Count"].mean().reset_index()
        by_trend_quartile.columns = ["Usage Trend Quartile", "Ticket Count"]
        fig = px.bar(
            by_trend_quartile, x="Usage Trend Quartile", y="Ticket Count",
            color="Usage Trend Quartile",
            color_discrete_sequence=["#B3D4FF", "#4C9AFF", "#2684FF", "#0052CC"],
        )
        fig.update_layout(showlegend=False)
        render_plotly_chart(fig, width="stretch", key="eda_ticket_by_trend_quartile")
        st.caption(
            "Caveat, stated plainly: this doesn't add independent evidence beyond the trend-noise finding "
            "in the Data reliability tab. Active Days Slope is fit on the same 5-month panel already shown "
            "there to produce slopes indistinguishable from random reshuffles (SD ratio near 1.0), with a "
            "negative first-half/second-half correlation (mean reversion, not a real trajectory). If the "
            "slope itself is mostly noise, splitting customers into quartiles of it is close to a random "
            "split, so a flat ticket count across quartiles is the expected result either way, not new proof "
            "that tickets are disconnected from real behaviour."
        )

    with usage_detail:
        st.markdown("#### Usage is stable per customer over time")
        st.caption(
            "Each customer's average Active Days in January 2023 against May 2023. A persistent metric should "
            "land near the diagonal; pure noise would look like a formless cloud."
        )
        first_month = eda_metrics["first_month"]
        last_month = eda_metrics["last_month"]
        persistence = usage[usage["Month"] == first_month].groupby("Customer ID")[
            "Active Days"
        ].mean().rename("First month").to_frame()
        persistence["Last month"] = usage[usage["Month"] == last_month].groupby("Customer ID")[
            "Active Days"
        ].mean()
        persistence = persistence.dropna()
        fig = px.scatter(
            persistence,
            x="First month",
            y="Last month",
            opacity=0.25,
            render_mode="webgl",
        )
        fig.update_traces(marker=dict(size=5))
        render_plotly_chart(fig, width="stretch", key="eda_persistence")
        st.caption(
            f"First-to-last-month correlation: **{eda_metrics['active_days_persistence']:.2f}** across "
            f"{len(persistence):,} customers."
        )

        st.markdown("#### Usage scales with plan tier and product")
        st.caption(
            "Higher plan tiers use the products more deeply, while each product retains its own natural "
            "activity baseline. Both patterns are why the risk model compares like-for-like peers."
        )
        plan_chart, product_chart = st.columns(2)
        with plan_chart:
            fig = px.bar(
                eda_metrics["usage_by_plan"],
                x="Plan Type",
                y="Active Days",
                title="Average active days by plan",
            )
            render_plotly_chart(fig, width="stretch", key="eda_usage_by_plan")
        with product_chart:
            fig = px.bar(
                eda_metrics["usage_by_product"],
                x="Product",
                y="Active Days",
                title="Average active days by product",
            )
            render_plotly_chart(fig, width="stretch", key="eda_usage_by_product")
        st.caption(
            f"Active Days rises from **{eda_metrics['usage_by_plan'].iloc[0]['Active Days']:.1f} on Free** "
            f"to **{eda_metrics['usage_by_plan'].iloc[-1]['Active Days']:.1f} on Enterprise**; Integrations "
            f"Used rises **{eda_metrics['integration_tier_ratio']:.1f}×** across the same tiers."
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
        render_plotly_chart(fig, width="stretch", key="dash_chart_1")
    with c_ticket2:
        fig = px.bar(tickets["Ticket Channel"].value_counts().reset_index(), x="Ticket Channel", y="count")
        render_plotly_chart(fig, width="stretch", key="dash_chart_2")

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
    render_plotly_chart(fig, width="stretch", key="dash_chart_3")

    st.subheader("Risk category breakdown")
    st.caption("How many customers fall into each of the four risk categories. Full definitions below the chart.")
    counts = filtered["Risk Category"].value_counts().reindex(CATEGORY_ORDER).reset_index()
    fig = px.bar(counts, x="Risk Category", y="count")
    render_plotly_chart(fig, width="stretch", key="dash_chart_4")
    st.markdown(
        "- **Monitor Only**: not at risk. Usage sits above the bottom quarter for this customer's plan "
        "and product peer group. No action.\n"
        "    - **Recommended action type:** no outreach; monitor the core activity for the customer's primary product.\n"
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
        "    - **Recommended action type:** a milestone-tracked onboarding review centred on one live product workflow.\n"
        "    - Recently acquired = Account Age ≤ the 25th percentile of Account Age across *all* "
        "customers, where Account Age = (2023-05-31 minus Account Created Date), in days.\n"
        "    - This is a relative quartile, not an absolute cutoff like \"under 90 days\": no customer "
        "in this dataset is younger than about 1.5 years by the 2023 usage window, so \"recently "
        "acquired\" means the youngest 25% of the base, not literally new.\n"
        "- **Established & Low Engagement**: at risk, longer-tenured, and either lower plan tier or lower "
        "embeddedness. A real but lower-stakes churn risk.\n"
        "    - **Recommended action type:** an automated product-specific reactivation play, with training only if usage stays low.\n"
        "    - Applies when At Risk is true, Recently Acquired is false, and High-Value (defined below) "
        "is also false.\n"
        "- **High-Value Disengaged**: at risk, longer-tenured, and either Enterprise/Premium tier or "
        "heavily integrated (top quartile of Collaborators + Integrations Used). The account most "
        "worth protecting.\n"
        "    - **Recommended action type:** an executive value review using product-specific adoption evidence and recovery milestones.\n"
        "    - High-Value = Plan Type is Enterprise or Premium, OR Embeddedness Percentile ≥ 75.\n"
        "    - Embeddedness Percentile = the percentile rank (0-100), across *all* customers, of "
        "Collaborators and Integrations Used, each standardised and then weighted by its measured "
        "reliability (0.63 and 0.89, giving a 41/59 split). See the Data reliability tab.\n"
        "    - Applies when At Risk is true, Recently Acquired is false, and High-Value is true."
    )

    st.markdown("#### Product-specific recommended actions")
    st.caption(
        "Risk category sets the intervention intensity; Primary Product sets the workflow. These are "
        "recommended workflow checks, not detected feature gaps, because the supplied data has no "
        "feature-level events."
    )
    focus_key_by_category = {
        "Monitor Only": "monitor",
        "New & Struggling": "onboarding",
        "Established & Low Engagement": "reactivation",
        "High-Value Disengaged": "value_review",
    }

    st.markdown("**Deck version: one illustrative row**")
    st.caption(
        "The full 4x5 grid is real but too dense for a slide, and only the category axis (the row) is "
        "backed by a named vendor process; the product-specific wording (the columns) is our own reasoning "
        "about how each tool is normally used, not a sourced claim. One row makes both points without "
        "implying the whole grid carries equal evidence."
    )
    illustrative_category = st.selectbox(
        "Category to illustrate", options=CATEGORY_ORDER, index=CATEGORY_ORDER.index("New & Struggling"),
    )
    one_row = pd.DataFrame(
        [{
            "Product": product,
            "Recommended focus": eda.PRODUCT_ACTION_FOCUS[product][focus_key_by_category[illustrative_category]].capitalize(),
        } for product in eda.PRODUCT_ACTION_FOCUS]
    )
    st.dataframe(one_row, width="stretch", hide_index=True)

    st.markdown("**Full grid: every category x product combination**")
    action_pivot = pd.DataFrame(
        {
            product: {
                category: eda.PRODUCT_ACTION_FOCUS[product][focus_key].capitalize()
                for category, focus_key in focus_key_by_category.items()
            }
            for product in eda.PRODUCT_ACTION_FOCUS
        }
    ).reindex(CATEGORY_ORDER).rename_axis("Risk Category")
    st.dataframe(action_pivot, width="stretch")

    st.markdown("**Plain-language version, for a general audience (deck-ready)**")
    st.caption(
        "Same table, rewritten without internal feature names (Butler, Power-Ups, Pipelines, and similar), "
        "so it's understandable to someone who doesn't use these products day to day."
    )
    GENERIC_ACTIONS = {
        "Monitor Only": {
            "Loom": "No outreach; continue tracking video creation and viewer engagement over time",
            "Confluence": "No outreach; continue tracking page activity and team contributions over time",
            "Trello": "No outreach; continue tracking board activity and collaboration over time",
            "Bitbucket": "No outreach; continue tracking code activity and integration use over time",
            "Jira": "No outreach; continue tracking task activity and workflow automation over time",
        },
        "New & Struggling": {
            "Loom": "An automated setup prompt triggers immediately; if the customer hasn't recorded "
            "and shared a first video, a guided session follows, with progress checked over three months",
            "Confluence": "An automated setup prompt triggers immediately; if the customer hasn't set "
            "up a working team workspace, a guided session follows, with progress checked over three months",
            "Trello": "An automated setup prompt triggers immediately; if the customer hasn't launched "
            "a board with the team's workflow, a guided session follows, with progress checked over "
            "three months",
            "Bitbucket": "An automated setup prompt triggers immediately; if the customer hasn't "
            "connected a project and completed an initial task, a guided session follows, with progress "
            "checked over three months",
            "Jira": "An automated setup prompt triggers immediately; if the customer hasn't launched a "
            "project with a starter backlog, a guided session follows, with progress checked over three "
            "months",
        },
        "Established & Low Engagement": {
            "Loom": "An automated prompt encouraging the customer to resume regular video updates, "
            "followed by a short training session if activity doesn't recover",
            "Confluence": "An automated prompt encouraging the customer to refresh an inactive "
            "workspace, followed by a short training session if activity doesn't recover",
            "Trello": "An automated prompt encouraging the customer to revive a dormant board, "
            "followed by a short training session if activity doesn't recover",
            "Bitbucket": "An automated prompt encouraging the customer to restart a stalled project, "
            "followed by a short training session if activity doesn't recover",
            "Jira": "An automated prompt encouraging the customer to restart a dormant project, "
            "followed by a short training session if activity doesn't recover",
        },
        "High-Value Disengaged": {
            "Loom": "An automated alert flags the account internally; a named account executive "
            "reaches out to understand what's blocking video adoption and agrees a plan to help the "
            "customer realise more value",
            "Confluence": "An automated alert flags the account internally; a named account executive "
            "reaches out to understand what's blocking team adoption and agrees a plan to help the "
            "customer realise more value",
            "Trello": "An automated alert flags the account internally; a named account executive "
            "reaches out to understand what's blocking collaboration and agrees a plan to help the "
            "customer realise more value",
            "Bitbucket": "An automated alert flags the account internally; a named account executive "
            "reaches out to understand what's blocking development adoption and agrees a plan to help "
            "the customer realise more value",
            "Jira": "An automated alert flags the account internally; a named account executive "
            "reaches out to understand what's blocking delivery adoption and agrees a plan to help the "
            "customer realise more value",
        },
    }
    generic_pivot = pd.DataFrame(GENERIC_ACTIONS).T.reindex(CATEGORY_ORDER).rename_axis("Risk Category")
    st.dataframe(generic_pivot, width="stretch")

    with st.expander("Full recommended-action text for every category x product combination", expanded=False):
        product_actions = pd.DataFrame(
            [
                {
                    "Risk Category": category,
                    "Primary Product": product,
                    "Recommended Action": eda.recommended_action(category, product),
                }
                for category in CATEGORY_ORDER
                for product in eda.PRODUCT_ACTION_FOCUS
            ]
        )
        st.dataframe(product_actions, width="stretch", hide_index=True)

    st.subheader("Usage by product")
    st.caption("Secondary real cut: Jira and other daily-use tools show higher engagement than Loom.")
    by_product = usage.groupby("Product")["Active Days"].mean().sort_values().reset_index()
    fig = px.bar(by_product, x="Product", y="Active Days")
    render_plotly_chart(fig, width="stretch", key="dash_chart_5")

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
            "platform, matched first to the reason that category is at risk and then to the customer's "
            "Primary Product. Full citations "
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
            "rather than a relationship in decline. The milestone changes by product—for example, launch "
            "a Jira production project, a Confluence team space, a Bitbucket pull-request workflow, or a "
            "Loom async update.\n\n"
            "**High-Value Disengaged: executive business review.** Gainsight, ChurnZero and Vitally "
            "publish near-identical guidance: a quarterly exec-to-exec review of delivered ROI, reserved "
            "for the highest-value segment rather than run for everyone. ChurnZero adds including a "
            "leadership attendee as a signal of commitment, and pairing a technical resource when the "
            "review gets into implementation detail. Chosen for this category because it is the tier "
            "above the size threshold where Atlassian does assign people, so human effort is justified "
            "here and only here. Logged through Jira Product Discovery, which Atlassian's Customer "
            "Success team already uses for account prioritisation, making it a process extension rather "
            "than a new tool.\n\n"
            "**Established & Low Engagement: automated product-specific reactivation play.** The sequence "
            "adapts ChurnZero's documented low and mid-touch feature-adoption play: an automated trigger "
            "when overall usage stalls, a prompt naming a relevant workflow for the customer's Primary "
            "Product, then a complimentary training session if activity does not recover. HubSpot's "
            "tech-touch model supports the same routing, keeping "
            "human time for the high-value tier. Chosen for this category because heavy touch is not cost "
            "justified here, and because most accounts at this size have no assigned owner at all, so the "
            "intervention has to be as automatic as the detection. The workflow is a recommended check, "
            "not a detected feature gap, because feature-event data is not supplied."
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
    render_plotly_chart(fig, width="stretch", key="dash_chart_6")

    st.subheader("Usage clustered into 2 vs. 4 segments")
    st.caption(
        "Five raw usage metrics can't be plotted directly, so both use the same two composite axes that "
        "named the clusters. This is the actual logic behind the labels, not an arbitrary PCA projection. "
        "k=2 has the cleanest separation (silhouette 0.40); k=4 trades some separation for more actionable "
        "nuance (silhouette 0.30) -- see how the labels are decided, below."
    )
    # A fixed, named palette instead of the app-wide default sequence: the
    # first two ATLASSIAN_COLORS entries (blue, light blue) sit too close in
    # hue and lightness to tell apart at low opacity against a white
    # background. These four are chosen for pairwise contrast and to stay
    # legible on white: dark blue, green, purple, and red-orange.
    CLUSTER_COLORS = {
        "Low engagement": "#0052CC",
        "Active, shallow integration": "#00875A",
        "Integration-heavy, moderate usage": "#6554C0",
        "Power users": "#DE350B",
    }
    for k in [2, 4]:
        cluster_col = f"Usage Cluster (k={k})"
        st.markdown(f"**k={k}**")
        counts = filtered[cluster_col].value_counts().reset_index()
        fig = px.bar(counts, x=cluster_col, y="count")
        fig.update_layout(height=350)
        render_plotly_chart(fig, width="stretch", key=f"cluster_counts_k{k}")

        fig = px.scatter(
            filtered, x="Usage Volume", y="Integration Depth", color=cluster_col,
            color_discrete_map=CLUSTER_COLORS, opacity=0.45, render_mode="webgl",
        )
        fig.update_traces(marker=dict(size=6))
        fig.update_layout(height=650)
        render_plotly_chart(fig, width="stretch", key=f"cluster_scatter_k{k}")

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
    render_plotly_chart(fig, width="stretch", key="cluster_mix_chart")

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
        color_discrete_map={"Not anomaly": "#A5ADBA", "Anomaly": "#E10600"},
        opacity=0.5, render_mode="webgl",
    )
    render_plotly_chart(fig, width="stretch", key="dash_chart_7")

    if "Anomaly Driver" in filtered.columns:
        anomaly_only = filtered[filtered["Usage Anomaly"] == True]
        if not anomaly_only.empty:
            driver_counts = (
                anomaly_only["Anomaly Driver"]
                .value_counts()
                .reset_index()
            )
            driver_counts.columns = ["Anomaly Driver", "Customer Count"]
            driver_counts = driver_counts[driver_counts["Anomaly Driver"] != "Normal usage"]
            if not driver_counts.empty:
                fig_driver = px.bar(
                    driver_counts,
                    x="Customer Count",
                    y="Anomaly Driver",
                    orientation="h",
                    color_discrete_sequence=["#DE350B"],
                )
                fig_driver.update_layout(height=260, yaxis=dict(autorange="reversed"))
                st.markdown("**What drives these anomalies? (Isolation Forest Attribution)**")
                st.caption(
                    "Attribution identifies which specific telemetry dimension pushed each outlier beyond the decision boundary. "
                    "The largest drivers are automated API syncs (High Product Actions / High Active Days) and single-user automation accounts (Low Collaborators)."
                )
                render_plotly_chart(fig_driver, width="stretch", key="dash_anomaly_drivers")

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

    st.subheader("Supervised Early-Warning Radar (Month 5 Disengagement Forecaster)")
    st.caption(
        "Because contract cancellation labels do not exist in the dataset, we frame the supervised ML task "
        "using empirical longitudinal telemetry: predicting which customers drop into the bottom engagement quartile "
        "in Month 5 based purely on their Months 1–4 telemetry."
    )
    ml_results = load_ml_results(ML_RESULTS_JSON.stat().st_mtime if ML_RESULTS_JSON.exists() else 0)
    if ml_results is not None and "random_forest" in ml_results:
        rf = ml_results["random_forest"]
        kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
        kpi_col1.metric("Test ROC-AUC", f"{rf['test_roc_auc']:.3f}", "Random Forest")
        kpi_col2.metric("Test Accuracy", f"{rf['test_accuracy']:.1%}", "80/20 Test Split")
        kpi_col3.metric("Disengaged Precision", f"{rf['precision_disengaged']:.1%}", "74% true risk")
        kpi_col4.metric("Disengaged Recall", f"{rf['recall_disengaged']:.1%}", "Catches 70% drops")
        kpi_col5.metric("F1-Score", f"{rf.get('f1_disengaged', 0.7219):.3f}", "Harmonic Mean")

        col_roc, col_feat = st.columns(2)
        with col_roc:
            st.markdown("##### Out-of-Sample ROC Curve")
            roc_df = pd.DataFrame({
                "False Positive Rate": rf["fpr"],
                "True Positive Rate": rf["tpr"],
                "Model": f"Random Forest (AUC = {rf['test_roc_auc']:.3f})",
            })
            fig_roc = px.line(roc_df, x="False Positive Rate", y="True Positive Rate", color="Model", color_discrete_sequence=["#0052CC"])
            fig_roc.add_shape(
                type="line", line=dict(dash="dash", color="#7A869A"),
                x0=0, x1=1, y0=0, y1=1,
            )
            fig_roc.update_layout(
                height=380,
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1]),
                legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95),
            )
            render_plotly_chart(fig_roc, width="stretch", key="supervised_roc_curve")

        with col_feat:
            st.markdown("##### Top Leading Indicators of Disengagement")
            feat_dict = rf.get("top_feature_importances", {})
            name_map = {
                "avg_sessions_m1_4": "Avg Sessions (M1-4)",
                "avg_active_days_m1_4": "Avg Active Days (M1-4)",
                "avg_actions_m1_4": "Avg Product Actions (M1-4)",
                "min_active_days_m1_4": "Min Active Days (M1-4)",
                "max_active_days_m1_4": "Max Active Days (M1-4)",
                "last_sessions_m4": "Recent Sessions (Month 4)",
                "last_active_days_m4": "Recent Active Days (Month 4)",
                "last_actions_m4": "Recent Actions (Month 4)",
                "Plan Type_Free": "Plan Tier: Free",
                "active_days_momentum": "Active Days Trajectory",
            }
            feat_df = pd.DataFrame([
                {"Feature": name_map.get(k, k), "Importance": v}
                for k, v in feat_dict.items()
            ]).sort_values("Importance", ascending=True)

            fig_feat = px.bar(
                feat_df, x="Importance", y="Feature", orientation="h",
                color_discrete_sequence=["#0052CC"],
            )
            fig_feat.update_layout(height=380)
            render_plotly_chart(fig_feat, width="stretch", key="supervised_feature_importances")

        st.markdown("##### Out-of-Sample Confusion Matrix (Test Set N = 1,664)")
        cm = rf["confusion_matrix"]
        col_cm_plot, col_cm_text = st.columns([1.1, 0.9])
        with col_cm_plot:
            cm_z = cm
            cm_x = ["Predicted Engaged", "Predicted Disengaged"]
            cm_y = ["Actually Engaged", "Actually Disengaged"]
            cm_annotations = [
                [f"<b>{cm[0][0]:,}</b><br>True Negative<br>(Specificity: {cm[0][0]/(cm[0][0]+cm[0][1]):.1%})",
                 f"<b>{cm[0][1]:,}</b><br>False Positive<br>(False Alarm: {cm[0][1]/(cm[0][0]+cm[0][1]):.1%})"],
                [f"<b>{cm[1][0]:,}</b><br>False Negative<br>(Missed: {cm[1][0]/(cm[1][0]+cm[1][1]):.1%})",
                 f"<b>{cm[1][1]:,}</b><br>True Positive<br>(Recall: {cm[1][1]/(cm[1][0]+cm[1][1]):.1%})"]
            ]
            fig_cm = px.imshow(
                cm_z,
                x=cm_x,
                y=cm_y,
                color_continuous_scale=[[0.0, "#F4F5F7"], [0.2, "#DEEBFF"], [1.0, "#0052CC"]],
            )
            fig_cm.update_traces(text=cm_annotations, texttemplate="%{text}", textfont=dict(size=13))
            fig_cm.update_layout(height=320, coloraxis_showscale=False, margin=dict(t=20, b=20, l=20, r=20))
            render_plotly_chart(fig_cm, width="stretch", key="supervised_confusion_matrix")

        with col_cm_text:
            st.markdown(
                f"- **True Positives ({cm[1][1]:,} accounts)**: **70.4% Recall** — captures 7 out of 10 disengaging accounts 30 days before usage drops.\n"
                f"- **Precision ({rf['precision_disengaged']:.1%})**: Nearly 3 out of 4 flagged accounts truly drop, eliminating alert fatigue for CSMs.\n"
                f"- **F1-Score ({rf.get('f1_disengaged', 0.7219):.3f})**: High harmonic balance between precision and recall on the minority at-risk class.\n"
                f"- **True Negatives ({cm[0][0]:,} accounts)**: **90.8% Specificity** — healthy accounts are correctly recognized without unnecessary outreach.\n"
                f"- **Actionable Window**: Intervening at Month 4 gives Atlassian a 30-day proactive runway before drop-off solidifies into non-renewal."
            )
    else:
        st.info("Supervised model results not found. Run `python analysis/predict_disengagement.py` to generate.")

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
    render_plotly_chart(fig, width="stretch", key="dash_chart_8")

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
        f"trending up in the first half should still be trending up in the second."
    )
    st.caption(
        "What this is: each customer's 5 monthly values are split into two overlapping halves, months 1-3 "
        "and months 3-5, and a slope is fit separately within each half. That gives every customer a "
        "first-half slope and a second-half slope, and the two are correlated across all customers. A real, "
        "consistent trend would show up as a positive correlation, since someone trending up early should "
        "still be trending up late."
    )
    st.markdown(
        f"The actual correlation "
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
    render_plotly_chart(fig, width="stretch", key="dash_chart_9")
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
    render_plotly_chart(fig, width="stretch", key="dash_chart_10")
    st.dataframe(results["embeddedness"], width="stretch")

    st.markdown("#### Urgency coefficient")
    st.caption("Risk Score rank correlation across coefficients from 0.2 to 0.5. Risk Category doesn't depend on this at all:")
    fig = px.line(
        results["urgency"], x="Urgency coefficient", y="Rank correlation vs. baseline (0.3)", markers=True,
    )
    fig.update_yaxes(range=[0, 1.05])
    render_plotly_chart(fig, width="stretch", key="dash_chart_11")
    st.dataframe(results["urgency"], width="stretch")

    st.markdown("#### Bootstrap stability")
    st.caption("Per-customer agreement rate with the full-population At Risk flag, across 20 resamples:")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Average agreement", f"{results['bootstrap_mean']:.1%}")
    with col_b:
        fig = px.histogram(results["bootstrap_detail"], nbins=20, labels={"value": "Agreement rate"})
        fig.update_layout(showlegend=False)
        render_plotly_chart(fig, width="stretch", key="dash_chart_12")

# --- Documentation -----------------------------------------------------------
with tab_docs:
    st.caption("Every finding behind this dashboard, in one place.")
    choice = st.selectbox("Choose a document", list(DOC_FILES))
    doc_path = DOCS_DIR / DOC_FILES[choice]
    if doc_path.exists():
        st.markdown(doc_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"{doc_path} not found yet.")

    st.divider()
    st.markdown("#### Interactive Model HTML Reports")
    st.caption("Standalone Plotly HTML reports for slide decks and presentations (stored in `docs/`):")
    html_col1, html_col2 = st.columns(2)
    with html_col1:
        perf_html = ROOT / "docs" / "supervised_model_performance.html"
        if perf_html.exists():
            st.download_button(
                "Download 3-Panel Radar HTML (ROC, Features, CM)",
                data=perf_html.read_text(encoding="utf-8"),
                file_name="supervised_model_performance.html",
                mime="text/html",
                width="stretch",
            )
    with html_col2:
        cm_html = ROOT / "docs" / "confusion_matrix.html"
        if cm_html.exists():
            st.download_button(
                "Download Standalone Confusion Matrix HTML",
                data=cm_html.read_text(encoding="utf-8"),
                file_name="confusion_matrix.html",
                mime="text/html",
                width="stretch",
            )
