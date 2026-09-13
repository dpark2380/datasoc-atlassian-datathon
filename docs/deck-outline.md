# Deck outline

This follows the same presentation rhythm as the 15-slide sample deck from
last year: title, problem, business stakes, one decisive finding, evidence,
method, results, scenarios, recommendations, and a final product reveal. The
content is changed completely for this problem and solution.

The timings total 7 minutes 25 seconds, leaving 35 seconds of buffer in an
8-minute presentation. Solution and Recommendation carries 35% of the marks,
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

Headline: Compare every account with peers who have the same plan and primary
product.

Figure to add: a four-step pipeline: **Five-month usage -> Plan x product
peer group -> Bottom 25% engagement -> Value and embeddedness weighting**.
Beneath it, show one Risk Scorer peer-comparison chart for an example
customer.

Put on the slide:

- A Free Loom account is not judged against an Enterprise Jira account.
- The rule detects low engagement; it is not an observed churn probability.
- The final 0-100 score ranks urgency after the at-risk rule is applied.

Line to say: Risk here means unusually low engagement for a fair peer group,
not a black-box probability of churn.

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

## Slide 10. Validation: Can We Trust the Result?

Time: 35 seconds. Purpose: Analysis and Insights.

Headline: The prioritisation is stable, while trend claims are not.

Figure to add: a four-card validation scorecard:

- **0.63-0.98:** reliability range across the five usage metrics.
- **99.1%:** bootstrap agreement with the at-risk flag.
- **0.997:** real-vs-shuffled trend spread ratio, showing no reliable trend.
- **18.3%:** overlap between anomaly flags and at-risk flags, showing they
  capture different concepts.

Use green for stable-score evidence and amber for the rejected trend
evidence.

Put on the slide: one short interpretation under each figure. Avoid a dense
statistical table.

Line to say: We kept the part the data can reproduce and removed the part it
cannot.

Sources: `findings-reliability.md` and `findings-sensitivity.md`.

## Slide 11. Customer Scenarios: Score to Action

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

## Slide 12. Method Selection

Time: 30 seconds. Purpose: Analysis and Insights.

Headline: Choose the method the available evidence can actually support.

Figure to add: a three-row decision table:

| Method | Decision | Why |
|---|---|---|
| Sentiment model | Rejected | No customer-written text |
| Supervised churn model | Rejected | No outcome label |
| Peer-relative usage rule | Selected | Repeated behaviour and explainable actions |

Add clustering and anomaly detection in a small footer labelled
**independent validation**, not as competing production models.

Put on the slide: the table and one statement: no accuracy, precision,
recall, AUC, or churn probability is valid without ground truth.

Line to say: The simplest defensible model beat the most
impressive-sounding model we could not validate.

## Slide 13. Strategies for Retention

Time: 35 seconds. Purpose: Solution and Recommendation.

Headline: Match the retention play to the likely reason for low engagement.

Figure to add: two horizontal playbook lanes:

- **New & Struggling (518): Diagnose -> reset milestones -> 30/60/90-day
  adoption review.**
- **Established & Low Engagement (893): identify unused feature -> in-app
  nudge -> short training -> human escalation only if needed.**

Put on the slide:

- Make onboarding recovery milestone-based rather than a generic check-in.
- Automate the established-account play first so human effort is reserved
  for failed interventions.
- Do not lead with discounts; solve adoption and value gaps first.

Line to say: Retention action should remove the barrier to value, not simply
reward disengagement.

Source: `research-cs-playbook-actions.md`.

## Slide 14. Strategies for Value Protection and Expansion

Time: 30 seconds. Purpose: Solution and Recommendation.

Headline: Protect high-value accounts and test deeper adoption where usage is
already healthy.

Figure to add: a two-column action panel:

- **Protect: 661 High-Value Disengaged -> CSM-led executive value review.**
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

## Slide 15. Introducing the Customer Risk Playbook

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
4. Cluster profiles and anomaly-overlap detail.
5. Full action-playbook evidence and ownership model.
6. Revenue concentration and company-specific business context, only if a
   judge asks.
7. Live Risk Scorer walkthrough.

## Claims to leave out

- Generic retention myths such as "5x cheaper to retain" or "5% retention
  raises profit 25-95%".
- Product-specific adoption claims as the main business-stakes story; they
  require too much context for this point in the pitch.
- Accuracy, precision, recall, AUC, or churn probability without an outcome
  label.
- Causal claims that usage or integration alone produces revenue growth.
- Any conversion of Cloud ARR shares into GAAP revenue dollars.

## Standing caveat

The 8,320 accounts are a datathon dataset, not Atlassian's real customers.
State this once, clearly. Every number shown should be computed from the
supplied data or linked to a named source.
