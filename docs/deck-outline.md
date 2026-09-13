# Deck outline

Challenge statement (given): "How can Atlassian better leverage raw support
ticket data to understand customer experiences and sentiment, and ultimately
protect business value?"

Submission is a PowerPoint or PDF, due 3pm Monday 14 September. If selected,
8 minutes to present plus 4 minutes of Q&A. Judging weights: Solution and
Recommendation 35%, Analysis and Insights 30%, Presentation and Q&A 20%,
Story and Problem Statement 15%.

Eight minutes is roughly 10 slides. The timings below add to about 7 minutes
30, which leaves a buffer. Solution carries the most marks, so it gets the
most time.

## The one-sentence story

The support ticket data cannot answer the question asked, we can prove it,
and the usage data can answer it instead. Here is who is at risk, why, and
what Atlassian should do about each one.

## Slide 1. The problem (30 seconds)

The challenge statement, then the stakes. Do not open with methodology.

Line to say: Atlassian has more than 350,000 customers and cannot call all of
them, so the question is which account to work next.

## Slide 2. Why getting this right is worth money (45 seconds)

Serves: Story.

- 57,334 customers hold over 85% of Cloud ARR (Q4 FY26 shareholder letter,
  filed with the SEC 6 August 2026).
- Against more than 350,000 customers total, that is about one account in six.
- No single customer is more than 5% of total revenue (FY26 10-K), so this is
  tens of thousands of accounts, not a handful of whales someone already
  watches by name.

Line to say: the concentration is real, but it is spread across tens of
thousands of accounts, which is exactly the range where a person cannot watch
each one and a model can.

Keep Cloud ARR and total ARR apart. The 85% is Cloud ARR.

## Slide 3. The data cannot answer the question as asked (60 seconds)

Serves: Analysis. This is the credibility foundation, so do not soften it.

Every ticket field tested against every other field, all flat: satisfaction
rating, ticket type, priority, channel, subject, resolution time, customer
age, customer gender, ticket count. A Critical ticket scores the same average
satisfaction as a Low one. There is also no customer-written text anywhere in
the dataset, so sentiment analysis is not possible.

Line to say: we could have shown you a sentiment chart. It would have been
noise with a trend line on it.

Sources: `findings-data-quality.md`, `findings-additional-signals.md`.

## Slide 4. We ran the same audit on our own data (45 seconds)

Serves: Analysis. This is the slide most teams will not have.

- Reliability per metric, from 0.98 for Sessions down to 0.63 for
  Collaborators. Every composite weight in the model is set by the measured
  reliability rather than chosen by hand.
- Trend permutation test: shuffling each customer's months produces slopes
  with the same spread as the real ones, ratio 0.997. First-half and
  second-half slopes correlate at -0.49, which is mean reversion.

Line to say: there is no trend to analyse in this panel, and we can show that
rather than assert it. It is also why a category we had called "Declining" is
now called "Low Engagement", because the data cannot support the word
declining.

Source: `findings-reliability.md`.

## Slide 5. What is real (45 seconds)

Serves: Analysis.

Usage is stable per customer (0.82 correlation January to May) and scales
cleanly with plan tier (Free 5.3 active days a month, Enterprise 11.5) and by
product (Loom about 6.7, Jira about 10.0). Two charts, no more.

## Slide 6. The risk model (60 seconds)

Serves: Analysis into Solution.

At risk means bottom quartile of engagement within the same plan tier and
product, so a Free Loom user is not judged against an Enterprise Jira
baseline. Each at-risk account gets a 0 to 100 score weighted by account
value and embeddedness, and one of four categories:

| Category | Count |
|----|----|
| Monitor Only | 6,248 |
| New & Struggling | 518 |
| Established & Low Engagement | 893 |
| High-Value Disengaged | 661 |

## Slide 7. Why you can trust the split (45 seconds)

Serves: Analysis. Condense hard, one line each.

- Unsupervised clustering, given no knowledge of the risk rules,
  independently reproduced the same volume-versus-depth split the categories
  use. High-Value Disengaged draws 62% from the integration-heavy cluster.
- Anomaly detection flags a different 5% of accounts, only 18% overlapping,
  so the rule is not just re-deriving what any outlier detector finds.
- Every judgment-call parameter was varied and the population barely moves.
  Bootstrap resampling agrees with the flag 99.1% of the time.

Source: `findings-ml-segments.md`, `findings-sensitivity.md`.

## Slide 8. What Atlassian does about it (90 seconds, the most important slide)

Serves: Solution, 35% of the marks. Give it the most time.

One specific action per category, each sourced, none of them "send an email":

- New & Struggling: milestone-tracked onboarding review against a 30/60/90
  day checklist, using Atlassian's own published Jira Adoption Guide as the
  session material rather than building new collateral.
- High-Value Disengaged: quarterly executive business review, jointly owned
  by the CSM and account leadership, logged through Jira Product Discovery,
  which Atlassian's Customer Success team already uses for account
  prioritisation.
- Established & Low Engagement: automated play naming the specific unused
  feature, then an in-app nudge, then a short training offer. No CSM time
  unless the automated play fails.
- Monitor Only: nothing. Saying this out loud matters, because a model that
  flags everyone is useless.

Source: `research-cs-playbook-actions.md`.

## Slide 9. Atlassian's own Customer Success team already works this way (45 seconds)

Serves: Solution. This is the strongest single slide in the deck, so do not
bury it in an appendix.

An Atlassian Enterprise CSM published her team's account prioritisation
weighting: Monthly Active Usage 40%, Potential CSM Impact 20%, Months Until
Renewal 20%, Customer Readiness 20%. She inverts the usage term so that low
adoption ranks an account higher.

Line to say: usage is the heaviest input, it is deliberately inverted to
surface disengagement, and there is no ticket count and no satisfaction score
anywhere in those four fields. That is the model we built, described by the
team we built it for.

Call it an Atlassian CSM's published method, not Atlassian's official health
score. The second version is overclaiming and would be corrected.

## Slide 10. What to capture next, and close (30 seconds)

Serves: Solution.

Industry health scores (Gainsight, ChurnZero) combine usage with support
sentiment and survey data. Ours has usage only, because this dataset's ticket
data cannot support the rest. So the closing recommendation is what to start
capturing: ordered and real response timestamps, the actual customer-written
text, and tickets linked to account context. That turns a limitation into the
next action rather than an apology.

Close on the specific thing, not a summary of the talk.

## Backup slides, for Q&A only

Have these built but not in the main flow.

1. Targeting responsiveness, not just risk. Ascarza (Journal of Marketing
   Research, 2018) found that targeting the highest-risk customers is often
   wrong because they are the least movable. Our four categories already
   split on responsiveness, and the Atlassian CSM's "Potential CSM Impact"
   field is the same idea. Best raised by us if the conversation goes there.
2. Full reliability and permutation detail, including the ICC table.
3. Sensitivity tables: cutoff, embeddedness weight, urgency coefficient.
4. Support is thin by design: gross margin up partly on "greater efficiency
   in our customer support operations", cost of revenues up 11% against 26%
   revenue growth, employee compensation inside it down $56.2M. Support
   deliberately made cheaper per customer produces thinner signal per
   customer.
5. Integration depth: "those advantages compound the more applications and
   contexts a customer connects", and 98% of MCP users are also active in the
   Jira UI in the same month, which answers the objection that integration
   traffic might be machines rather than people.
6. The live risk scorer. Pick a customer, show the score, the reason, and the
   recommended action on one screen.

## Do not put these on a slide

Checked and rejected, with reasons in
`research-business-context-figures.md`. If someone else cites one at us, this
is the answer.

- The Reichheld retention figures ("a 5% increase in retention raises profits
  25% to 95%"). Not in the original 1990 article in that form, consumer
  settings only, and later work in the same journal published direct
  pushback.
- "It costs five times more to acquire a customer than to retain one." Traces
  to unavailable 1980s research with no recoverable primary source.
- Net revenue retention. Atlassian does not disclose it in its filings. The
  widely quoted figure comes from call commentary and third-party trackers.
- Churn statistics from vendor blogs. None carried a sample size or method.
- The at-a-glance market opportunity and user diversity splits. The market
  definition changed between Q3 and Q4 FY26, and an Atlassian judge would
  know.
- Any dollar figure produced by multiplying 85% by Cloud revenue. Atlassian
  states that Cloud ARR is not GAAP revenue.

## Standing caveat to state once, early

The 8,320 customers in this dataset are not Atlassian's real customers. The
Atlassian figures describe the business this method would run in, not this
sample. Say it once, clearly, and then stop apologising for it.

## Style rule for every slide

See `docs/agents/writing-style.md`. Say the specific, checkable thing. Not
"sentiment analysis reveals hidden customer pain points" but "the ticket data
in this dataset is statistically random, and here is what we built instead".
Every number on a slide must be one we computed or one we can point to in a
filed document.
