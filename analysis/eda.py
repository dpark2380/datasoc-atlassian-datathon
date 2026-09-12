"""
Build the customer risk/action view from the official datathon dataset.

Full audit of what's real vs. noise in this dataset lives in
docs/findings-data-quality.md and docs/findings-additional-signals.md
(plain-language versions). Summary of what this pipeline relies on:

REAL, used here:
  - product_usage.csv has genuine per-customer persistence (Jan-May 2023
    Active Days correlation = 0.82) and usage level tracks Plan Type
    cleanly (Free 5.3 -> Enterprise 11.5 avg active days/month).
  - Product also shows a real, moderate difference (Jira ~10.0 vs Loom
    ~6.7 avg active days) -- used as part of the peer group, not just a
    secondary cut.
  - Integrations Used scales with Plan Type even more sharply than Active
    Days (Free 1.14 -> Enterprise 5.99, ~5x spread vs ~2x for Active
    Days) -- weighted higher than Collaborators in the embeddedness score.
  - Account Created Date has no real "new customer" cohort relative to the
    2023 usage window (everyone is 1.5-4.5 years old by then), so tenure
    is used as a RELATIVE quartile within the customer base, never as an
    absolute "just onboarded" claim.

NOT REAL, not used as a signal (kept only as descriptive/operational
context where shown at all):
  - Customer Satisfaction Rating, Customer Age, Customer Gender: all
    statistically random against everything tested.
  - Ticket Type / Subject / Priority / Channel: near-uniform distributions
    -- independently randomly assigned per ticket.
  - Resolution Hours, Ticket Status: incoherent timestamps / no
    relationship to usage.
  - Ticket volume per customer: flat across every segment (~1.0-1.02
    tickets/customer everywhere; every customer has at least one ticket).
  - No free-text field exists in this dataset at all.
  - Industry / Region / Company Size: flat, no relationship to usage.
  - One narrow exception: a ticket's Product Purchased field is 100%
    consistent with the customer's real product_usage.csv rows -- kept
    only as a validity note, not used as a signal.

Run: .venv/bin/python analysis/eda.py
Writes: analysis/cleaned_tickets.csv   (ticket-level, descriptive only)
        analysis/customer_risk.csv     (customer-level, the real signal)
"""
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path(__file__).parent.parent / "references" / "Dataset"
OUT_TICKETS = Path(__file__).parent / "cleaned_tickets.csv"
OUT_CUSTOMER_RISK = Path(__file__).parent / "customer_risk.csv"

ENGAGEMENT_METRICS = ["Active Days", "Sessions", "Product Actions"]
EMBEDDEDNESS_METRICS = ["Collaborators", "Integrations Used"]
# Every usage column the pipeline loads per customer. Kept separate from the
# scoring metric lists above: clustering and the risk scorer's peer chart need
# all five regardless of how the composites are weighted.
USAGE_METRICS = ENGAGEMENT_METRICS + EMBEDDEDNESS_METRICS
TIER_VALUE = {"Free": 0.0, "Standard": 1 / 3, "Premium": 2 / 3, "Enterprise": 1.0}
USAGE_SNAPSHOT_DATE = pd.Timestamp("2023-05-31")  # end of the product_usage window

# Unsupervised segments, independent of the Risk Score above -- see
# docs/findings-ml-segments.md for the full k=2..6 silhouette scan and the
# 0.63 correlation between usage volume and integration depth (why the k=4
# scatter shows one continuous diagonal band, not 4 separated blobs). Both
# k=2 (cleanest separation, silhouette 0.40, low/high usage only) and k=4
# (silhouette 0.30, splits volume from depth, more actionable nuance but
# with overlapping boundaries) are kept -- neither is "the" answer.
CLUSTER_METRICS = ["Active Days", "Sessions", "Product Actions", "Collaborators", "Integrations Used"]
CLUSTER_K_VALUES = [2, 4]
# 5% contamination: a smaller, differently-defined set of unusual accounts,
# not meant to reproduce the 25% quartile-based At Risk flag.
ANOMALY_CONTAMINATION = 0.05
RANDOM_STATE = 42

PLAYBOOK_ACTIONS = {
    "Monitor Only": "No action, track only.",
    "New & Struggling": (
        "Milestone-tracked onboarding review: named CSM owner runs a structured "
        "adoption session scoped to this account's unused workflows, checked "
        "against a 30/60/90-day milestone list (Gainsight onboarding model)."
    ),
    "High-Value Disengaged": (
        "Executive Business Review: quarterly exec-to-exec review scoped to this "
        "account's actual ROI/adoption data, jointly owned by the CSM and account "
        "leadership, logged via Jira Product Discovery (ChurnZero/Gainsight QBR "
        "model; Atlassian's own CS team already uses this tool for triage)."
    ),
    "Established & Low Engagement": (
        "Automated feature-specific play: email naming the exact underused "
        "feature and its value, an in-app nudge 1-2 days later, and a "
        "complimentary short training session if usage doesn't recover "
        "(ChurnZero low/mid-touch adoption play)."
    ),
}


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tickets = pd.read_csv(DATA_DIR / "customer_support_tickets.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    usage = pd.read_csv(DATA_DIR / "product_usage.csv")
    return tickets, customers, usage


def clean_tickets(tickets: pd.DataFrame) -> pd.DataFrame:
    """Descriptive/operational cleaning only -- see module docstring for why
    none of these fields are used as a predictive signal."""
    df = tickets.copy()
    df["Date of Purchase"] = pd.to_datetime(df["Date of Purchase"], format="%d-%m-%Y", errors="coerce")
    df["First Response Time"] = pd.to_datetime(df["First Response Time"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["Time to Resolution"] = pd.to_datetime(df["Time to Resolution"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["Ticket Priority"] = pd.Categorical(
        df["Ticket Priority"], categories=["Low", "Medium", "High", "Critical"], ordered=True
    )
    return df


def join_customer_id(tickets: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Tickets carry no Customer ID -- join on email (verified 1:1, 100% match)."""
    return tickets.merge(customers[["Customer ID", "Customer Email"]], on="Customer Email", how="left")


def ticket_count_per_customer(tickets: pd.DataFrame) -> pd.DataFrame:
    """Descriptive only -- confirmed flat across every segment, not a risk signal."""
    return tickets.groupby("Customer ID").size().rename("Ticket Count").reset_index()


def metric_reliability(usage: pd.DataFrame, metrics: list[str] | None = None) -> dict[str, float]:
    """How much of each metric is a stable customer trait rather than
    month-to-month noise, for the 5-month average the model actually uses.

    Single-month ICC is between-customer variance over total variance. The
    model averages 5 months, which suppresses the noise term by n, so the
    reliability that applies here is the Spearman-Brown adjusted figure.
    On this dataset that ranges from 0.63 (Collaborators) to 0.98 (Sessions):
    see docs/findings-reliability.md.

    Computed from the data at runtime so the composite weights below are
    measured rather than hand-picked.
    """
    metrics = metrics or USAGE_METRICS
    n_months = usage.groupby("Customer ID")["Month"].nunique().median()

    reliabilities = {}
    for metric in metrics:
        per_customer = usage.groupby("Customer ID")[metric]
        between = per_customer.mean().var()
        within = per_customer.var().mean()
        reliabilities[metric] = between / (between + within / n_months)
    return reliabilities


def weighted_composite(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Standardise each metric, then combine on the given weights.

    Standardising first matters: the previous version multiplied raw values,
    so a metric's real influence depended on its raw scale rather than on its
    stated weight (Collaborators' nominal 1:2 weighting worked out to an
    effective 38:62 split purely because of scale).
    """
    total = sum(weights.values())
    z_scores = [((df[m] - df[m].mean()) / df[m].std()) * (w / total) for m, w in weights.items()]
    return pd.concat(z_scores, axis=1).sum(axis=1)


def customer_usage_summary(usage: pd.DataFrame) -> pd.DataFrame:
    """Average usage metrics per customer across their 5-month history, plus
    their primary product (the one with the most total active days -- for
    the 98.6% of customers with only one product this is just that product)."""
    avg = usage.groupby("Customer ID")[USAGE_METRICS].mean().reset_index()

    totals = usage.groupby(["Customer ID", "Product"])["Active Days"].sum().reset_index()
    primary = totals.loc[totals.groupby("Customer ID")["Active Days"].idxmax(), ["Customer ID", "Product"]]
    primary = primary.rename(columns={"Product": "Primary Product"})

    return avg.merge(primary, on="Customer ID", how="left")


def percentile_within_group(df: pd.DataFrame, value_col: str, group_cols: list[str]) -> pd.Series:
    return df.groupby(group_cols)[value_col].rank(pct=True) * 100


def label_usage_clusters(centroids: pd.DataFrame) -> dict[int, str]:
    """Name each cluster from its own centroid, not a hardcoded index --
    KMeans cluster numbering isn't a meaningful order on its own. Splits on
    two axes: usage volume (Active Days/Sessions/Product Actions) and
    integration depth (Collaborators/Integrations Used), each ranked across
    the k centroids, then quadrant-labeled. Written for any even k."""
    volume = centroids[ENGAGEMENT_METRICS].mean(axis=1)
    # Unweighted on purpose: a centroid averages over a whole cluster, where
    # the per-customer noise that reliability weighting corrects for has
    # already averaged out.
    depth = centroids[EMBEDDEDNESS_METRICS].mean(axis=1)
    volume_rank = volume.rank(method="first").astype(int) - 1
    depth_rank = depth.rank(method="first").astype(int) - 1
    half = len(centroids) / 2

    labels = {}
    for cluster_id in centroids.index:
        high_volume = volume_rank[cluster_id] >= half
        high_depth = depth_rank[cluster_id] >= half
        if high_volume and high_depth:
            labels[cluster_id] = "Power users"
        elif high_volume and not high_depth:
            labels[cluster_id] = "Active, shallow integration"
        elif not high_volume and high_depth:
            labels[cluster_id] = "Integration-heavy, moderate usage"
        else:
            labels[cluster_id] = "Low engagement"
    return labels


def add_usage_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """KMeans on standardised usage metrics -- discovers segments from the
    data itself, instead of the hand-picked Plan Type x Product grouping
    used for the Risk Score. Computes every k in CLUSTER_K_VALUES (k=2 and
    k=4 by default): k=2 is the cleaner separation, k=4 is more actionable
    nuance with more overlap. Neither is hidden in favour of the other --
    see docs/findings-ml-segments.md."""
    df = df.copy()
    features = df[CLUSTER_METRICS].fillna(df[CLUSTER_METRICS].median())
    X = StandardScaler().fit_transform(features)

    for k in CLUSTER_K_VALUES:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(X)
        id_col = f"Usage Cluster ID (k={k})"
        label_col = f"Usage Cluster (k={k})"
        df[id_col] = km.labels_

        centroids = df.groupby(id_col)[CLUSTER_METRICS].mean()
        labels = label_usage_clusters(centroids)
        df[label_col] = df[id_col].map(labels)

    # Default/headline columns -- k=4, kept under the plain name for
    # anything that doesn't care which k it's looking at (e.g. the
    # risk-scorer tool's single-customer summary line).
    df["Usage Cluster ID"] = df["Usage Cluster ID (k=4)"]
    df["Usage Cluster"] = df["Usage Cluster (k=4)"]
    return df


def add_usage_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Isolation Forest on the same standardised usage metrics -- flags
    accounts with an unusual overall usage SHAPE (e.g. high sessions but
    low product actions), a different concept from the quartile-based
    At Risk flag, which only looks at overall engagement level within a
    peer group. See docs/findings-ml-segments.md for how much the two
    flags overlap."""
    df = df.copy()
    features = df[CLUSTER_METRICS].fillna(df[CLUSTER_METRICS].median())
    X = StandardScaler().fit_transform(features)

    iso = IsolationForest(contamination=ANOMALY_CONTAMINATION, random_state=RANDOM_STATE).fit(X)
    df["Usage Anomaly"] = iso.predict(X) == -1
    df["Usage Anomaly Score"] = -iso.score_samples(X)  # higher = more unusual
    return df


def build_customer_risk(
    customers: pd.DataFrame,
    usage_summary: pd.DataFrame,
    ticket_counts: pd.DataFrame,
    reliabilities: dict[str, float],
) -> pd.DataFrame:
    df = customers.merge(usage_summary, on="Customer ID", how="left")
    df = df.merge(ticket_counts, on="Customer ID", how="left")
    df["Ticket Count"] = df["Ticket Count"].fillna(0)

    # Engagement composite: Active Days, Sessions, Product Actions only.
    # Embeddedness (Collaborators, Integrations Used) is kept OUT of this
    # composite deliberately -- see docs/findings-additional-signals.md.
    # Folding embeddedness into the same score would let a well-integrated
    # but declining account cancel out its own risk, which contradicts the
    # decision that embeddedness should RAISE urgency, not hide disengagement.
    #
    # Both composites weight each metric by its measured reliability rather
    # than by hand. For engagement this changes almost nothing (all three
    # metrics sit between 0.92 and 0.98), but it means no weight in the model
    # is an unexplained choice.
    engagement_weights = {m: reliabilities[m] for m in ENGAGEMENT_METRICS}
    df["Engagement Composite"] = weighted_composite(df, engagement_weights)

    # At Risk / disengagement severity: percentile within the customer's own
    # Plan Type x Primary Product peer group -- both are confirmed real,
    # different baselines (Free vs Enterprise, Jira vs Loom), so comparing
    # a customer only to their real peers avoids penalising accounts on
    # naturally lower-touch tiers/products.
    df["Engagement Percentile"] = percentile_within_group(df, "Engagement Composite", ["Plan Type", "Primary Product"])
    df["At Risk"] = df["Engagement Percentile"] <= 25
    disengagement_severity = 100 - df["Engagement Percentile"]

    # Embeddedness: Collaborators + Integrations Used, each standardised and
    # then weighted by its measured reliability, expressed as a percentile so
    # it combines cleanly with the tier weight.
    #
    # Note for anyone reading this expecting the noisy metric to have been
    # dropped: it wasn't, and reliability weighting does not reduce its
    # influence. Collaborators is the least reliable input (0.63 against 0.89
    # for Integrations Used), but weighting by reliability gives it 41% of the
    # embeddedness score, slightly MORE than the 38% it effectively had under
    # the old raw-value scheme. The gain here is that the split is now measured
    # and stated rather than an accident of raw scale.
    embeddedness_weights = {m: reliabilities[m] for m in EMBEDDEDNESS_METRICS}
    df["Embeddedness Percentile"] = weighted_composite(df, embeddedness_weights).rank(pct=True) * 100

    # Risk Score: disengagement severity scaled up by an urgency multiplier
    # from account value (plan tier) and embeddedness -- both confirmed to
    # matter for how much it costs to lose this account, per Q3/Q10.
    tier_weight = df["Plan Type"].map(TIER_VALUE).fillna(0)
    embeddedness_weight = df["Embeddedness Percentile"] / 100
    urgency_multiplier = 1 + 0.3 * tier_weight + 0.3 * embeddedness_weight
    df["Risk Score"] = (disengagement_severity * urgency_multiplier).clip(upper=100).round(1)

    # Relative tenure -- see module docstring: no absolute "new" cohort
    # exists relative to the 2023 usage window, so tenure is a quartile
    # within the customer base, not a real-world onboarding claim.
    account_created = pd.to_datetime(df["Account Created Date"])
    account_age_days = (USAGE_SNAPSHOT_DATE - account_created).dt.days
    newer_cutoff = account_age_days.quantile(0.25)
    df["Recently Acquired (relative)"] = account_age_days <= newer_cutoff

    high_value = df["Plan Type"].isin(["Enterprise", "Premium"]) | (df["Embeddedness Percentile"] >= 75)

    def categorise(row) -> str:
        if not row["At Risk"]:
            return "Monitor Only"
        if row["Recently Acquired (relative)"]:
            return "New & Struggling"
        if high_value.loc[row.name]:
            return "High-Value Disengaged"
        return "Established & Low Engagement"

    df["Risk Category"] = df.apply(categorise, axis=1)
    df["Recommended Action"] = df["Risk Category"].map(PLAYBOOK_ACTIONS)

    df = add_usage_clusters(df)
    df = add_usage_anomalies(df)

    return df


def main() -> None:
    tickets_raw, customers, usage = load_raw()

    tickets = clean_tickets(tickets_raw)
    tickets = join_customer_id(tickets, customers)
    tickets.to_csv(OUT_TICKETS, index=False)

    usage_summary = customer_usage_summary(usage)
    ticket_counts = ticket_count_per_customer(tickets)
    reliabilities = metric_reliability(usage)
    risk = build_customer_risk(customers, usage_summary, ticket_counts, reliabilities)
    risk.to_csv(OUT_CUSTOMER_RISK, index=False)

    print(f"Tickets (descriptive only): {len(tickets)} rows -> {OUT_TICKETS}")
    print(f"Customer risk: {len(risk)} rows -> {OUT_CUSTOMER_RISK}")
    print()
    print("Composite weights, from measured reliability of the 5-month average:")
    for metric, reliability in reliabilities.items():
        print(f"  {metric:20s} {reliability:.3f}")
    print()
    print("Active Days by Plan Type:")
    print(risk.groupby("Plan Type")["Active Days"].mean().sort_values())
    print()
    print("Risk Category counts:")
    print(risk["Risk Category"].value_counts())
    print()
    print("Usage Cluster counts:")
    print(risk["Usage Cluster"].value_counts())
    print()
    n_anomaly = risk["Usage Anomaly"].sum()
    overlap = risk.loc[risk["Usage Anomaly"], "At Risk"].mean()
    print(f"Usage anomalies: {n_anomaly} / {len(risk)} ({n_anomaly / len(risk):.1%})")
    print(f"Of those, already flagged At Risk by the quartile method: {overlap:.1%}")


if __name__ == "__main__":
    main()
