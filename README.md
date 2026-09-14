# UNSW DataSoc x Atlassian Datathon 2026: Customer Risk & Proactive Retention Engine

An end-to-end, methodologically rigorous Customer Success machine learning engine built for Atlassian products (Jira, Confluence, Trello, Bitbucket, Loom). Combines an out-of-sample **Supervised Early-Warning Radar (ROC-AUC 0.921)** with **Unsupervised Behavioral Segmentation & Anomaly Attribution** to diagnose account risk and prescribe targeted, high-ROI retention playbooks 30 days before contract renewal.

---

## 1. Problem Statement & The Analytical Breakthrough

### The Problem
In product-led SaaS, customer churn is silent. Customers do not submit warning tickets before leaving—they quietly stop logging in and abandon workflows. Waiting for a customer to file a complaint or cancellation request is too late. How can Atlassian proactively forecast which accounts will disengage 30 days in advance, and prescribe the right Customer Success playbooks to preserve contract value?

### The Methodological Stand: Auditing the Data
The competition prompt provided three datasets: `customers.csv`, `customer_support_tickets.csv`, and `product_usage.csv`. A naive approach would assume support tickets reflect customer sentiment and churn. 

**Our rigorous audit proved that `customer_support_tickets.csv` is uninformative synthetic noise:**
- **Zero Correlation with Churn**: Accounts filing a *"Cancellation request"* ticket used the product for **8.85 active days in Month 5**—identical to accounts filing a *"Product inquiry"* (8.84 days) ($r = +0.0099, p = 0.368$).
- **Random Satisfaction Ratings**: 5-star customers disengaged in Month 5 at **26.8%**, while 1-star customers disengaged at **27.8%** (a statistical coin-flip, $r = -0.012$).
- **Causal Inconsistencies**: Ticket resolution timestamps frequently occur *before* first response times, and text fields contain synthetic Markov filler.
- **Ticketing is Not a Trigger**: 100% of accounts filed a ticket (98.3% filed exactly 1). 

**Our Decision**: We rejected synthetic ticket fields and built our engine exclusively on genuine, longitudinal product telemetry (`product_usage.csv`), which exhibits high stability ($r = 0.82$ persistence Jan–May) and scales cleanly with plan tier (Free: 5.3 active days $\rightarrow$ Enterprise: 11.5 active days).

---

## 2. The 2-Part Machine Learning Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │                   THE 2-PART ENGINE                    │
                       └────────────────────────────────────────────────────────┘
                                                    │
             ┌──────────────────────────────────────┴──────────────────────────────────────┐
             ▼                                                                             ▼
 ┌───────────────────────────────────────┐                     ┌───────────────────────────────────────┐
 │   PART 1: SUPERVISED FORECASTER       │                     │   PART 2: UNSUPERVISED DIAGNOSTIC     │
 │            (The Radar)                │                     │              (The Map)                │
 ├───────────────────────────────────────┤                     ├───────────────────────────────────────┤
 │ • Predicts WHEN an account drops off  │                     │ • Diagnoses WHO they are & WHAT to do │
 │ • Monitors Months 1-4 session drops   │                     │ • K-Means: Volume vs. Depth quadrants │
 │ • Out-of-sample ROC-AUC: 0.921        │                     │ • Isolation Forest: Filters bot syncs │
 │ • 30-day proactive warning runway     │                     │ • Prescribes exact CS playbook play   │
 └───────────────────────────────────────┘                     └───────────────────────────────────────┘
             │                                                                             │
             └──────────────────────────────────────┬──────────────────────────────────────┘
                                                    ▼
                               ┌────────────────────────────────────────┐
                               │  TARGETED CUSTOMER SUCCESS PLAYBOOK    │
                               │  (Executive Review, Onboarding, Plays) │
                               └────────────────────────────────────────┘
```

---

## 3. Part 1: Supervised Early-Warning Radar (Predicting *WHEN*)

### Formulation
Using 4 months of longitudinal telemetry (January–April 2023), the model predicts which accounts collapse into the bottom quartile of composite engagement within their product peer group in Month 5 (May 2023). Strict 80/20 train/test split ($N = 1,664$ test accounts) with zero lookahead bias.

### Performance Summary (Held-Out Test Set)

| Metric | Random Forest | Logistic Regression | Meaning / Business Impact |
| :--- | :--- | :--- | :--- |
| **Test ROC-AUC** | **`0.9210`** | `0.9215` | Outstanding separation across all classification thresholds |
| **Test Accuracy** | **`85.28%`** | `85.10%` | High overall correctness vs 72.85% baseline |
| **Disengaged Precision** | **`74.13%`** | `74.39%` | Nearly 3 out of 4 flagged accounts truly drop (prevents alert fatigue) |
| **Disengaged Recall** | **`70.35%`** | `68.14%` | Catches **7 out of 10 disengaging accounts** 30 days in advance |
| **Disengaged F1-Score** | **`0.7219`** | `0.7112` | Strong harmonic balance on the minority at-risk class |

### Out-of-Sample Confusion Matrix ($N = 1,664$)

```
                                 PREDICTED BY MODEL
                             Predicted           Predicted
                              Engaged           Disengaged
ACTUAL OUTCOME         ┌───────────────────┬───────────────────┐
Actually Engaged (M5)  │    1,101 (TN)     │     111 (FP)      │  → 1,212 total
                       │ Specificity: 90.8%│ False Alarm: 9.2% │
                       ├───────────────────┼───────────────────┤
Actually Disengaged(M5)│     134 (FN)      │     318 (TP)      │  →   452 total
                       │  Missed: 29.6%    │  Recall: 70.4%    │
                       └───────────────────┴───────────────────┘
```

### Top Leading Indicators of Disengagement
1. `avg_sessions_m1_4` (0.2255 importance) — Monthly login session frequency
2. `avg_active_days_m1_4` (0.1830 importance) — Consistency of active days
3. `avg_actions_m1_4` (0.1548 importance) — Platform action volume
4. `min_active_days_m1_4` (0.1258 importance) — Historic low-water mark
5. `active_days_momentum` (0.0146 importance) — Month 4 drop vs Month 1–3 baseline

> **Core Telemetry Insight**: Session frequency and daily routine regularity are far more predictive of future retention than episodic volume spikes. Disengagement starts with decreasing login frequency before total volume drops.

### Explainable AI: SHAP Beeswarm Summary & Bi-Directional Risk Attribution
While global feature rankings show aggregate importance, our engine implements **SHAP (SHapley Additive exPlanations) TreeExplainer** (`analysis/shap_utils.py`) to provide granular, account-level positive vs. negative risk attribution:
- **SHAP Beeswarm Summary Plot (Red & Blue Dots along X-Axis)**:
  - **X-Axis (SHAP Value)**: Spread along the horizontal axis showing marginal impact on Month 5 disengagement probability. Left of 0 (< 0) represents protective retention factors; right of 0 (> 0) represents risk drivers.
  - **Dot Color**: Feature value for that specific customer (**Red = High**, **Blue = Low**).
  - **Key Empirical Discovery**: For *Avg Sessions (M1-4)*, a heavy cluster of **Blue dots (low session counts)** stretches far to the right (+15% to +25% disengagement risk), while **Red dots (high session counts)** pull risk down by -10% to -15%. Conversely, ticket volume dots cluster tightly around zero with no separation between red and blue, confirming support tickets do not differentiate churn.
- **Double-Sided Impact Plot (+/-)**: Centered at zero for an individual customer, horizontal bars extend **Right (Red / +)** for metrics that escalate disengagement risk, and **Left (Blue / -)** for protective retention factors (e.g. high collaborator counts or integrations mitigating a session drop).
- **Global Bi-Directional Impact**: Decomposes company-wide feature impacts into their average risk-escalating magnitude versus protective retention magnitude.
- **Interactive Tooling**: Available dynamically in the `Risk Scorer` live demo, in the `Dashboard` case study expander, and exported at `docs/shap_beeswarm.png` (300-DPI publication asset), `docs/shap_beeswarm_interactive.html`, and `docs/shap_double_sided.html`.

---

## 4. Part 2: Unsupervised Behavioral Segmentation & Anomaly Attribution (Diagnosing *WHO* & *WHAT TO DO*)

Once an account is flagged at risk, Customer Success needs to know what kind of customer they are to take the right action.

### K-Means Behavioral Quadrants ($k=4$, Standardized Within Product)
Clustering all 5 usage metrics proves customer behavior is organized along two orthogonal dimensions: **Usage Volume** and **Integration Depth**:
1. **Power Users (1,041 accounts / 12.5%)**: High volume + high depth. **0.0% Month 5 disengagement**.
2. **Active, Shallow Integration (2,318 accounts / 27.9%)**: High usage volume, but low integration depth. **Atlassian's highest-ROI expansion opportunity**: onboarding them to integrations (Slack, GitHub, Confluence) cements stickiness. Only 6.2% disengage.
3. **Integration-Heavy, Moderate Usage (1,807 accounts / 21.7%)**: High depth, moderate/low volume. Heavily Enterprise/Premium accounts where IT connected integrations but end-user adoption is stalling (15.9% disengage).
4. **Low Engagement (3,154 accounts / 37.9%)**: Low volume + low depth. Mostly Free/Standard tier accounts (58.0% disengage).

### Isolation Forest with Anomaly Attribution (5% Contamination, 416 Accounts)
Only 18.3% overlap with the quartile At Risk flag, proving Isolation Forest detects abnormal behavioral shapes, not simply low usage:
- **High Product Actions (122 accounts)**: Automated API scripts and webhook syncing.
- **High Active Days (110 accounts)**: Always-on monitoring daemons.
- **Low Collaborators (63 accounts)**: Single-user silos prone to sudden turnover churn.
- **High Collaborators (34 accounts)**: Unused team licenses (shelfware).

---

## 5. Targeted Customer Success Playbooks

| Risk Category | Customer Segment | Prescribed CS Playbook Action | Tooling / Sourced Framework |
| :--- | :--- | :--- | :--- |
| **High-Value Disengaged** | Enterprise / High Embeddedness | Quarterly Executive Business Review scoped to adoption gaps; re-align with business sponsor | Jira Product Discovery / Gainsight EBR |
| **Active, Shallow Integration** | High Volume, Zero Integrations | Integration Onboarding Campaign (connect Slack, GitHub, Figma, Confluence) | In-app feature adoption nudges |
| **New & Struggling** | First quartile relative tenure | Milestone-tracked onboarding review (Day 30/60/90 checklist) | Atlassian Published Jira Adoption Guide |
| **Established & Low Engagement** | Standard / Free tiers | Automated feature-specific re-engagement play (email, template library) | HubSpot / ChurnZero automated plays |
| **Usage Anomaly (Bot Sync)** | Extreme actions / zero days | Technical webhook audit; filter out from human CSM workflows | Atlassian Developer API health check |

---

## 6. Repository Structure

```
├── README.md                                  # Comprehensive documentation
├── requirements.txt                           # Frozen Python environment dependencies
├── streamlit_app.py                           # App entry point (verifies pipeline & launches navigation)
├── app_pages/
│   ├── dashboard.py                           # Full results dashboard (Segments, Radar, Reliability, Sensitivity)
│   ├── risk_scorer.py                         # Single-customer lookup tool (Live Demo with SHAP Waterfall & Risk Forecast)
│   └── chart_styling.py                       # Atlassian brand chart design system
├── analysis/
│   ├── eda.py                                 # Feature engineering, peer standardization, K-Means & Anomaly attribution
│   ├── predict_disengagement.py               # Supervised Random Forest & Logistic Regression pipeline
│   ├── shap_utils.py                          # TreeExplainer & interactive Plotly SHAP waterfall generator
│   ├── trajectory_utils.py                    # 5-month longitudinal engagement trajectories & archetypes
│   ├── customer_risk.csv                      # Generated 33-column customer database with risk & cluster tags
│   ├── customer_disengagement_predictions.csv # Customer-level predicted probabilities vs actual outcomes
│   ├── ml_results.json                        # Machine-readable test metrics, ROC coordinates, and confusion matrix
│   ├── reliability_checks.py                  # ICC metric reliability & trend permutation tests
│   └── sensitivity_checks.py                  # Cutoff, embeddedness weight, and bootstrap sensitivity audits
├── docs/
│   ├── monthly_engagement_trajectories.png    # 300 DPI multi-panel longitudinal engagement plot
│   ├── monthly_engagement_trajectories.html   # Interactive Plotly longitudinal trajectory tool
│   ├── shap_beeswarm.png                      # Publication-quality (300 DPI) SHAP summary beeswarm plot
│   ├── shap_beeswarm_interactive.html         # Interactive Plotly beeswarm plot (red & blue dots along x-axis)
│   ├── shap_double_sided.html                 # Standalone interactive double-sided positive/negative attribution
│   ├── shap_waterfall.html                    # Standalone interactive Plotly SHAP waterfall explanation
│   ├── confusion_matrix.html                  # Standalone interactive Plotly Confusion Matrix & F1 report
│   ├── supervised_model_performance.html      # Standalone interactive 3-panel Radar dashboard
│   ├── findings-summary.md                    # One-page executive findings summary
│   ├── findings-ml-segments.md                # Detailed writeup on K-Means, Isolation Forest, and Supervised ML
│   ├── findings-data-quality.md               # Audit proving support tickets are synthetic noise
│   └── deck-outline.md                        # Presentation structure for the 8-minute pitch
└── references/Dataset/                        # Raw source files (READ ONLY)
    ├── customers.csv                          # Account metadata
    ├── customer_support_tickets.csv           # Support ticket records
    └── product_usage.csv                      # 5-month longitudinal product telemetry
```

---

## 7. How to Run

### Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the Supervised Pipeline
```bash
.venv/bin/python analysis/predict_disengagement.py
```

### Launch the Streamlit App
```bash
.venv/bin/streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`:
- **Dashboard Page**: Explore behavioral clusters, anomaly attribution, the Supervised Early-Warning Radar, interactive ROC curves, and download publication-ready HTML reports.
- **Risk Scorer Page**: Pick any customer ID (or click "Pick a random one") to view their peer usage comparison, 30-Day Disengagement Probability, risk score, and assigned Customer Success action.
