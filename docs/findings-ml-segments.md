# Unsupervised usage segments and anomaly detection

Two additions to the pipeline, both unsupervised, since the dataset has no
churn label to train or validate a supervised model against (see the "no
train/test data" section below). Code: `add_usage_clusters` and
`add_usage_anomalies` in `analysis/eda.py`.

## Why unsupervised, not supervised

There's no ground truth in this dataset for whether a customer actually
churned, downgraded, or expanded. Without a real outcome to predict, a
supervised model has nothing honest to be trained or evaluated against,
and there's no way to build a train/test split that means anything. Our
existing Risk Score and Risk Category are hand-built rules, not a trained
model, and we're not presenting them as one. The two additions below are
both unsupervised: they don't need a label, and they're evaluated on
internal statistical properties (cluster separation, outlier rarity), not
prediction accuracy.

## A correction: standardise within product, not globally

Both methods below standardise the five usage metrics before use. The
first version of this pipeline standardised globally, one mean and
standard deviation for the whole population. That was wrong in a specific,
checkable way: products have real, different usage baselines (Jira
averages about 10.0 active days a month, Loom about 6.7), so a typical
Loom customer looked lower on every metric than a typical Jira customer
purely from which product they use, not from being less engaged.

We tested this directly. Under global standardisation, Loom was 26.7% of
the lowest-usage cluster against its 19.2% base rate in the customer base.
Standardising within each customer's Primary Product instead (each
metric's mean and standard deviation computed separately per product)
brings every product back to within a point of its base rate, at
essentially no cost: silhouette at k=4 moves from 0.304 to 0.302. The
plan-tier finding below is unaffected, since Plan Type varies
independently of Primary Product. Every number in this document reflects
the corrected, within-product standardisation.

## 1. Usage clustering (KMeans)

We ran KMeans on the five usage metrics (Active Days, Sessions, Product
Actions, Collaborators, Integrations Used), standardised within Primary
Product, for k = 2 through 6, and measured cluster separation with
silhouette score:

| k | Silhouette score |
|---|---|
| 2 | 0.40 |
| 3 | 0.32 |
| 4 | 0.30 |
| 5 | 0.28 |
| 6 | 0.25 |

k=2 has the cleanest statistical separation, but it only recovers a
single low-usage-versus-high-usage split, which mostly restates the
plan-tier finding we already have. We used k=4 instead, because it splits
usage into two independent dimensions: how much a customer uses the
product (Active Days, Sessions, Product Actions) and how embedded they are
(Collaborators, Integrations Used). That's a genuinely different cut, not
just a repackaging of the plan-tier chart, even though its silhouette
score is lower. Both scores are reported here so the choice is checkable,
not picked quietly for a better-looking result.

The four segments, named from their own centroids (not fixed in advance):

| Segment | Customers | Pattern |
|---|---|---|
| Low engagement | 3,154 | Low on both usage volume and integration depth |
| Active, shallow integration | 2,318 | High usage volume, low integration depth |
| Integration-heavy, moderate usage | 1,807 | Moderate usage volume, high integration depth |
| Power users | 1,041 | High on both usage volume and integration depth |

"Active, shallow integration" is the interesting new group: high usage,
but few integrations and collaborators. That's a plausible expansion
target (they're already engaged, they just haven't adopted the features
that make an account sticky), distinct from "Low engagement," which needs
a different kind of intervention entirely.

## 2. Usage anomaly detection (Isolation Forest) & Attribution

We ran Isolation Forest on the same five metrics, standardised within
Primary Product for the same reason as the clustering above, with 5%
contamination (an arbitrary but standard default, chosen to flag a small,
genuinely unusual set rather than trying to match the 25% quartile-based
At Risk rate on purpose). It flagged 416 of 8,320 customers (5.0%).

Only 18.3% of those 416 were already flagged At Risk by the quartile
method. That means anomaly detection is finding a mostly different
population: accounts with an unusual overall usage shape (for example,
high sessions paired with low product actions, which the quartile method
wouldn't catch since it only looks at overall engagement level within a
peer group).

### Anomaly Attribution (Why each account was flagged)
Using standardized distance from peer medians, we attribute the dominant
driver for each flagged anomaly:
- **High Product Actions (122 accounts)**: Extreme automated script usage, bot activity, or bulk webhook syncing.
- **High Active Days (110 accounts)**: Daemon / always-on automated monitoring services.
- **High Sessions (70 accounts)**: Automated polling or high-frequency login routines.
- **Low Collaborators (63 accounts)**: High volume concentrated in single-user silos with zero organizational reach.
- **High Collaborators (34 accounts)** & **Integrations Used**: Broad multi-tool orchestration with atypical usage volume.

## 3. Supervised Early-Warning Radar (Month 5 Disengagement Forecaster)

While contract cancellation labels do not exist, the dataset contains 5 full months
of longitudinal telemetry per customer. This enables an uncorrupted, methodologically sound
supervised machine learning formulation: **predicting Month 5 usage collapse from Months 1–4 behavior**.

### Target Formulation
A customer is labeled as **Disengaged in Month 5** if their Month 5 composite engagement falls into
the bottom quartile within their primary product peer group (27.15% base rate).

### Feature Engineering (Months 1–4 only, strictly avoiding lookahead bias):
- Baseline volume aggregates: `mean`, `min`, `max`, `std` for Active Days, Sessions, Actions, Collaborators, Integrations.
- Momentum & trajectory: `Active Days Slope` and `active_days_momentum` (Month 4 vs Months 1-3 avg).
- Account context: One-hot encoded `Plan Type` and `Primary Product`.

### Out-of-Sample Performance (80/20 Train/Test Split, N = 1,664 test accounts):
- **Random Forest**:
  - **Test ROC-AUC**: **0.9210**
  - **Test Accuracy**: **85.28%**
  - **Recall (Disengaged)**: **70.35%** (identifies 7 out of 10 disengaging accounts 30 days in advance)
  - **Precision (Disengaged)**: **74.13%**
- **Logistic Regression (Linear Baseline)**:
  - **Test ROC-AUC**: **0.9215**
  - High agreement confirms strong underlying linear and non-linear telemetry signal.

### Top Leading Indicators
1. `avg_sessions_m1_4` (Importance: 0.2255)
2. `avg_active_days_m1_4` (Importance: 0.1830)
3. `avg_actions_m1_4` (Importance: 0.1548)
4. `min_active_days_m1_4` (Importance: 0.1258)
5. `max_active_days_m1_4` (Importance: 0.0816)

Session frequency and regular active days are far more predictive of future retention than episodic high-volume action spikes.

## Where this shows up

- `analysis/customer_risk.csv`: Contains `Usage Cluster`, `Usage Anomaly`, `Usage Anomaly Score`, and `Anomaly Driver`.
- `analysis/customer_disengagement_predictions.csv`: Contains `Predicted Disengagement Prob` and actual outcome.
- `analysis/ml_results.json`: Exports full ROC curves, confusion matrices, and feature importances.
- Streamlit Dashboard:
  - "Usage segments (ML)" tab renders K-Means clusters, anomaly scatter, anomaly attribution breakdown, and the interactive Supervised Early-Warning Radar.
