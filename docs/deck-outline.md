# Deck outline

This follows the same presentation rhythm as the 15-slide sample deck from
last year: title, problem, business stakes, one decisive finding, evidence,
method, results, scenarios, recommendations, and a final product reveal. The
content is changed completely for this problem and solution.

The timings total 8 minutes 35 seconds, 35 seconds OVER an 8-minute
presentation after adding slides 16 and 17. This needs to be cut down before
presenting: either trim two of the shorter slides' speaking time, fold slide
17 into slide 16 as one slide, or drop something else from the narrative.
Solution and Recommendation carries 35% of the marks,
Analysis and Insights 30%, Presentation and Q&A 20%, and Story and Problem
Statement 15%.

## The one-sentence story

The support-ticket file cannot reliably reveal customer sentiment, but
product usage can identify who needs attention, why, and what action to take
next.

## Slide 1. From Noise to Next Best Action

Time: 10 seconds. Purpose: opening.

Headline: Turn product signals into timely customer action.

Figure to add: a clean hero graphic with three connected blocks labelled
**Signals -> Priority -> Action**. Use the Atlassian blue palette and a small
crop of the Risk Scorer. Keep the rest of the slide clear.

Put on the slide:

- Title: From Noise to Next Best Action.
- Subtitle: A usage-led customer risk and action playbook.
- Team name and member names.

Line to say: We built a practical way to turn noisy account data into the
next best customer action.

## Slide 2. Problem Statement

Time: 25 seconds. Purpose: Story and Problem Statement.

Headline: Customer risk is useful only if it is detected before value is
lost.

Figure to add: a left-to-right problem chain: **Low adoption -> Unseen risk
-> Late intervention -> Lost customer value**. Put a warning icon over the
gap between unseen risk and late intervention.

Put on the slide:

- Business question: which customer needs attention now, and what should the
  team do?
- The brief points to support tickets; first test whether they contain a
  defensible signal.

Line to say: The goal is not to describe churn after it happens; it is to
find the accounts where action can still change the outcome.

## Slide 3. Why Should Atlassian Care?

Time: 30 seconds. Purpose: Story and Problem Statement.

Headline: Protect revenue, increase customer value, and focus limited human
attention.

Figure to add: three equal columns with simple icons and one outcome each:
**Protect recurring revenue**, **Increase realised customer value**, and
**Scale Customer Success**. Under the third column, add a small funnel marked
**8,320 accounts -> 2,072 prioritised for action**. Do not use a financial
filing chart or product-specific adoption statistics on this slide.

Put on the slide:

- Protect recurring revenue: disengagement can become renewal or downsell
  risk if nobody sees it early.
- Increase realised customer value: customers benefit when they adopt the
  products and integrations they already have.
- Scale Customer Success: in this dataset, prioritisation narrows 8,320
  accounts to 2,072 that need action.

Line to say: This matters to any subscription business: keep customers, help
them realise more value, and spend human attention where it can make a
difference.

Caution: 8,320 and 2,072 describe the datathon dataset, not Atlassian's real
customer base.

## Slide 4. The Finding That Changed Our Approach

Time: 25 seconds. Purpose: Analysis and Insights.

Headline: The ticket file cannot support the sentiment analysis in the
brief.

Figure to add: one oversized **49.3%** with the label **resolved tickets with
impossible event order**, beside a second card reading **0 customer-written
text fields**. This plays the same role as the sample deck's large
headline-number slide.

Put on the slide:

- 2,769 tickets are marked resolved, but almost half have resolution before
  first response.
- Without customer-written text, there is nothing genuine to score for
  sentiment.

Line to say: We could have produced a sentiment chart, but it would have been
noise with a trend line on it.

Source: `findings-data-quality.md`.

## Slide 5. What Each Dataset Can Tell Us

Time: 35 seconds. Purpose: Analysis and Insights.

Headline: Three datasets, three different levels of decision value.

Figure to add: export the three-column EDA panel from the Dashboard.

- **customers.csv:** 8,320 rows, 10 fields, four plan tiers.
- **customer_support_tickets.csv:** 8,469 rows, zero usable text fields,
  49.3% impossible resolved-event order.
- **product_usage.csv:** 42,210 observations, five months, 0.82 January-May
  usage persistence.

Put on the slide: one conclusion under each column: account context; audit
only; repeated behavioural signal.

Line to say: We did not combine every column simply because it was available;
we assigned each dataset only the role it could support.

## Slide 6. Why the Ticket File Cannot Measure Sentiment

Time: 30 seconds. Purpose: Analysis and Insights.

Headline: Ticket labels are present, but meaningful relationships are not.

Figure to add: the Dashboard's **average satisfaction by ticket priority**
bar chart, with every bar visibly close to 3.0. Add a callout reading
**Critical approximately equals Low satisfaction** and a small 49.3% invalid
timestamp badge.

Put on the slide:

- Priority, type, channel, resolution time, and satisfaction are effectively
  flat against each other.
- Nearly every customer has exactly one ticket, so ticket-volume comparisons
  have almost no variation.
- Exclude ticket fields from the score rather than manufacture confidence.

Line to say: The responsible analytical decision was to reject the ticket
file as a risk signal.

Sources: `findings-data-quality.md` and `findings-additional-signals.md`.

## Slide 7. The Real Signal: Product Usage

Time: 35 seconds. Purpose: Analysis and Insights.

Headline: Usage is repeatable enough to compare customers fairly.

Figure to add: use the Dashboard's **January active days vs May active days**
scatter as the main chart and call out **r = 0.82**. Add two small KPI cards:
**5.3 Free vs 11.5 Enterprise active days** and **1.1 vs 6.0 integrations
(5.3x)**.

Put on the slide:

- The same customers tend to remain relatively high- or low-usage across the
  five-month window.
- Usage separates coherently by plan and product, unlike ticket fields.

Line to say: Repeated behaviour, not a random ticket label, is the strongest
available signal of customer engagement.

## Slide 8. How We Define Risk

Time: 40 seconds. Purpose: Analysis into Solution.

Headline: Forecast next-month disengagement, then explain it against fair
peers.

Figure to add: a two-lane model diagram.

- **Early warning:** Months 1-4 usage -> predict bottom-quartile engagement
  in Month 5.
- **Action layer:** Five-month usage -> Plan x product peer group -> Bottom
  25% engagement -> Value and embeddedness weighting.

End both lanes at one customer card showing forecast probability, risk
category, and next action.

Put on the slide:

- The forecast provides a one-month warning using an observed future usage
  outcome.
- A Free Loom account is not judged against an Enterprise Jira account.
- Neither layer claims to predict contract churn because no churn label
  exists.
- The final 0-100 score ranks urgency after the at-risk rule is applied.

Line to say: One layer tells us who may disengage next month; the other
explains who they are and what to do.

## Slide 9. Results: Who Needs Action?

Time: 30 seconds. Purpose: Solution and Recommendation.

Headline: 2,072 accounts need action; 6,248 should be left alone.

Figure to add: a horizontal 100% stacked bar or account funnel with these
segments:

| Category | Accounts |
|---|---:|
| Monitor Only | 6,248 |
| New & Struggling | 518 |
| Established & Low Engagement | 893 |
| High-Value Disengaged | 661 |

Use grey for Monitor Only and progressively warmer colours for the three
action groups. Label **25% prioritised** and **75% no intervention** directly
on the figure.

Put on the slide: the headline, the chart, and the four category labels only.

Line to say: The model's first useful decision is who not to contact; only
one account in four enters an action queue.

## Slide 10. Usage Segments and Anomaly Detection

Time: 30 seconds. Purpose: Analysis and Insights.

Headline: Unsupervised clustering and anomaly detection corroborate the risk
categories, independently.

Figure to add: the Dashboard's k=4 usage-cluster scatter (Usage Volume vs
Integration Depth), with the four segment counts labelled: **Low engagement
(3,154)**, **Active, shallow integration (2,318)**, **Integration-heavy,
moderate usage (1,807)**, **Power users (1,041)**. Beside it, one card:
**416 of 8,320 customers (5.0%) flagged as usage anomalies**, **only 18.3%
overlap with At Risk**.

Put on the slide:

- KMeans on the five usage metrics, standardised within each customer's
  Primary Product so a Loom account is not penalised for a lower category
  baseline than Jira.
- k=2 is the cleanest split (silhouette 0.40) but mostly restates the
  plan-tier finding; k=4 (silhouette 0.30) trades some separation to split
  usage volume from integration depth instead.
- Isolation Forest (5% contamination) flags a mostly different population
  from the At Risk rule: unusual usage shape, not just low usage level.
- Both are unsupervised, since there is no churn label to train or validate
  a supervised model against; each is evaluated on internal statistical
  properties, not prediction accuracy.

Line to say: This is independent evidence, not decoration: the categories we
built by hand and the segments KMeans found on its own point at the same
customers.

Source: `findings-ml-segments.md`.

## Slide 11. Validation: Can We Trust the Result?

Time: 35 seconds. Purpose: Analysis and Insights.

Headline: The forecast separates next-month disengagement, and the action
queue stays stable.

Figure to add: a two-panel validation slide.

- **Forecast panel:** held-out ROC curve with **0.921 AUC**, **74.1%
  precision**, **70.4% recall**, and **n = 1,664**.
- **Prioritisation panel:** **99.1% bootstrap agreement**, **0.63-0.98 metric
  reliability**, and **0.997 real-vs-shuffled trend spread**.

Use the trend result as amber evidence for rejecting trend claims; use the
held-out and bootstrap results as green evidence for the two valid model
outputs.

Put on the slide:

- The supervised outcome is Month-5 bottom-quartile engagement, not churn or
  renewal.
- The forecast is tested out of sample; the descriptive risk queue is tested
  for stability.
- Avoid a dense statistical table.

Line to say: We kept the part the data can reproduce and removed the part it
cannot.

Sources: `findings-reliability.md` and `findings-sensitivity.md`.

## Slide 12. Customer Scenarios: Score to Action

Time: 35 seconds. Purpose: Solution and Recommendation.

Headline: The same low-usage signal requires different action in different
contexts.

Figure to add: a 2x2 scenario matrix with one anonymised customer card per
category. Axes are **new to established** and **lower to higher value**. Each
card should show plan, product, peer percentile, risk score, and a one-line
next action.

Put on the slide:

- New & Struggling -> onboarding recovery.
- Established & Low Engagement -> targeted feature reactivation.
- High-Value Disengaged -> human-led value review.
- Monitor Only -> no intervention.

Line to say: Urgency, likely cause, and appropriate cost of response are not
the same for every account.

## Slide 13. Method Selection

Time: 30 seconds. Purpose: Analysis and Insights.

Headline: Choose the method the available evidence can actually support.

Figure to add: a four-row decision table:

| Method | Decision | Why |
|---|---|---|
| Sentiment model | Rejected | No customer-written text |
| Supervised churn model | Rejected | No contract churn outcome label |
| Month-5 usage forecaster | Selected | Observed next-month engagement label and 0.921 held-out AUC |
| Peer-relative usage rule | Selected | Explainable prioritisation and actions |

Add clustering and anomaly detection in a small footer labelled
**behavioural diagnosis**, not as competing production models.

Put on the slide:

- Call the supervised output disengagement risk, not churn probability.
- Use the forecast to identify who may drop next month and the peer-relative
  rule to explain context and prescribe action.

Line to say: We use prediction for an outcome we can observe and transparent
rules for decisions people must explain.

## Slide 14. Strategies for Retention

Time: 35 seconds. Purpose: Solution and Recommendation.

Headline: Match the retention play to the likely reason for low engagement.

Figure to add: two horizontal playbook lanes with a Primary Product tag on
each customer:

- **New & Struggling (518): product-specific onboarding milestone ->
  30/60/90-day adoption review.**
- **Established & Low Engagement (893): product-specific workflow prompt ->
  short training -> human escalation only if needed.**

Add five compact examples: Jira production project; Confluence team space;
Trello board plus Butler automation; Bitbucket pull request plus Pipelines;
and Loom async update.

Put on the slide:

- Risk category determines intervention intensity; Primary Product determines
  the workflow.
- Make onboarding recovery milestone-based rather than a generic check-in.
- Automate the established-account play first so human effort is reserved
  for failed interventions.
- Treat the workflow as a recommended check, not a detected feature gap;
  feature-event data is not supplied.

Line to say: Retention action should remove the barrier to value, not simply
reward disengagement.

Source: `research-cs-playbook-actions.md`.

## Slide 15. Strategies for Value Protection and Expansion

Time: 30 seconds. Purpose: Solution and Recommendation.

Headline: Protect high-value accounts and test deeper adoption where usage is
already healthy.

Figure to add: a two-column action panel:

- **Protect: 661 High-Value Disengaged -> product-specific executive value
  review**, using measures such as Jira issue throughput, Bitbucket pull
  requests, or Confluence contribution.
- **Expand: 2,318 Active, Shallow Integration accounts -> targeted
  integration enablement pilot.**

Show the expansion pilot as **target group vs control group**, not as a
promised outcome.

Put on the slide:

- High-value disengagement earns proactive human attention and an agreed
  recovery plan.
- Healthy activity with shallow integration is a testable expansion
  hypothesis, not proof of propensity.
- Measure incremental integration adoption and usage against a control before
  scaling.

Line to say: Protect current value first, then test expansion where a specific
adoption gap is visible.

## Slide 16. How the Solution Fits Together

Time: 20 seconds. Purpose: Solution and Recommendation.

Headline: One pipeline, corroborated and forecast, converging on three
outputs.

Figure to add: a left-to-right pipeline: **Usage data -> Reliability-weighted
composites -> Peer-relative rule -> Risk Score & Category**. Beneath it, a
labelled branch, **corroborated by, and given an early warning from**,
showing **KMeans clustering**, **Isolation Forest**, and the **Month-5
forecaster** feeding upward rather than deciding anything. Both converge on
two final boxes: **Product-specific recommended action** and **Live Risk
Scorer tool**.

Put on the slide:

- One backbone does the deciding: data, composites, rule, score. Nothing
  downstream overrides it.
- The three diagnostic and forecasting components corroborate or warn; they
  are not competing production models and do not decide who gets flagged.
- Everything converges on two outputs a person can act on: a recommended
  action, and a live tool.

Line to say: One backbone, corroborated and forecast, converging on what a
person actually uses.

## Slide 17. Three Outputs, One Pipeline

Time: 20 seconds. Purpose: Solution and Recommendation.

Headline: Everything the analysis produces, reduced to three things a person
can use.

Figure to add: three equal columns, one per output.

- **Risk Score & Risk Category:** built from the peer-relative rule on
  reliability-weighted composites; explainable to a human without
  translation.
- **Recommended Action:** built from product-specific actions applied to the
  Risk Category; a named CS playbook, not a generic email.
- **Live Risk Scorer:** built from all six components surfaced together; the
  analysis only matters if someone can act on it in real time.

Put on the slide:

- Risk Score & Risk Category: every customer scored 0-100 and placed in one
  of four categories, compared only to peers on the same Plan Type and
  Primary Product.
- Recommended Action: category sets the intensity, Primary Product sets the
  workflow.
- Live Risk Scorer: score, peer comparison, category, recommended action,
  and forecast probability, all on one screen.

Line to say: Three outputs, one pipeline: a score, a specific action, and a
tool to act on both.

## Slide 18. Introducing the Customer Risk Playbook

Time: 20 seconds. Purpose: product reveal and close.

Headline: One account, one explanation, one next action.

Figure to add: a large screenshot of the live Risk Scorer showing customer
context, score, peer comparison, and recommended action. Put a tested QR code
and short URL beside it. Keep a local screenshot or video fallback if the
deployed app requires sign-in.

Put on the slide:

- The product screenshot.
- QR code and short URL.
- Final caption: **Detect earlier. Prioritise fairly. Act specifically.**

Line to say: This is how the analysis becomes a repeatable Customer Success
decision, account by account.

Caution: verify the deployment from a logged-out browser before printing the
QR code. The current app may redirect unauthenticated judges.

## Backup slides for Q&A

Build these, but keep them out of the timed narrative:

1. Full ticket data-quality audit and impossible timestamp examples.
2. Reliability table and trend permutation distributions.
3. Cutoff, weighting, and bootstrap sensitivity tables.
4. Full action-playbook evidence and ownership model.
5. Revenue concentration and company-specific business context, only if a
   judge asks.
6. Live Risk Scorer walkthrough.

## Claims to leave out

- Generic retention myths such as "5x cheaper to retain" or "5% retention
  raises profit 25-95%".
- Product-specific adoption claims as the main business-stakes story; they
  require too much context for this point in the pitch.
- Accuracy, precision, recall, AUC, or churn probability for contract churn
  without a churn outcome label.
- Causal claims that usage or integration alone produces revenue growth.
- Any conversion of Cloud ARR shares into GAAP revenue dollars.

## Standing caveat

The 8,320 accounts are a datathon dataset, not Atlassian's real customers.
State this once, clearly. Every number shown should be computed from the
supplied data or linked to a named source.
