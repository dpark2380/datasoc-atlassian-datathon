# Additional signal check (plain-language version)

This is a follow-up to `docs/findings-data-quality.md`. That doc established
which parts of the dataset are real and which are randomly generated noise.
This doc goes through everything we hadn't tested yet, specifically looking
for anything that ties back to the support ticket file, since that's what
the challenge brief asks us to use. Read `docs/findings-data-quality.md`
first if you haven't; we don't repeat what's already confirmed there.

## What we tested, and what we found

### 1. Customer age and gender

We checked age and gender against satisfaction rating, ticket volume, and
usage level (average Active Days).

- Satisfaction by age bucket: means range from 2.94 to 3.08 across six age
  brackets, a spread of 0.14 on a 1-5 scale. Age vs. satisfaction
  correlation: r = -0.0037.
- Satisfaction by gender: means range from 2.97 to 3.03, a spread of 0.06.
- Ticket volume by age bucket: means range from 1.013 to 1.024 tickets per
  customer, a spread of 0.011.
- Ticket volume by gender: means range from 1.016 to 1.020, a spread of
  0.004.
- Usage level (avg. Active Days) by age bucket: means range from 8.51 to
  8.88 days, a spread of 0.36 on a scale where Plan Type alone spreads
  usage by over 6 days. Age vs. usage correlation: r = 0.0035.
- Usage level by gender: means range from 8.71 to 8.74 days, a spread of
  0.03.

**Verdict: noise.** Every spread here is close to zero and every
correlation is close to zero. Age and gender behave exactly like the
already-confirmed-random fields: no real relationship to anything.

### 2. Ticket Subject

Ticket Subject is the more granular field under Ticket Type (e.g. "Product
setup", "Network problem", "Data loss"), with 16 possible values.

- Distribution of Ticket Subject by Product Purchased: every product's row
  of percentages sits between 4.6% and 8.1% across the 16 subjects, close
  to the flat 6.25% you'd expect from 16 equally likely categories. A
  chi-square test gives chi2 = 62.3 on 60 degrees of freedom, which is
  right at the value you'd expect from randomness (chi2 approximately
  equal to degrees of freedom means no detectable association). The
  effect size (Cramer's V) is 0.043, essentially zero.
- Satisfaction by Ticket Subject: means range from 2.80 ("Email delivery
  problem") to 3.18 ("Installation support"), a spread of 0.38. This looks
  bigger than the other satisfaction spreads we found, but with 150-200
  tickets per subject the expected noise band on a mean is around
  +/-0.2-0.3 just from sample size, and we're comparing across 16 groups
  at once, so some groups will land far apart by chance alone.
  Satisfaction has already been shown to be uniform noise against every
  other field tested; this one more comparison doesn't overturn that.

**Verdict: noise.** Ticket Subject behaves the same way as Ticket Type,
Priority, and Channel: assigned independently of the product and
independently of the outcome.

### 3. Ticket Status vs. current usage level

We grouped each customer into "has an Open or Pending ticket right now" vs.
"all their tickets are Closed," and compared average Active Days,
Collaborators, and Integrations Used between the two groups (a snapshot
association, not a before/after claim).

- Avg. Active Days: 8.71 (all closed) vs. 8.74 (open/pending), a spread of
  0.02 on a ~8.5-9 day scale.
- Avg. Collaborators: 11.06 vs. 11.08, a spread of 0.02.
- Avg. Integrations Used: 3.16 vs. 3.18, a spread of 0.02.

**Verdict: noise.** Whether a customer currently has an unresolved ticket
has no measurable relationship to how much they use the product.

### 4. Number of tickets filed vs. usage / embeddedness

We checked whether customers who happened to file more tickets (1, 2, 3,
or 4) show different usage patterns, independent of why they filed more.

- Correlation between ticket count and avg. Active Days: r = -0.0068.
- Correlation between ticket count and Collaborators: r = 0.0023.
- Correlation between ticket count and Integrations Used: r = -0.0180.

All three are effectively zero. Worth flagging separately: this whole
question turns out to be close to moot. Every one of the 8,320 customers
in `customers.csv` filed at least one ticket (zero customers with 0
tickets), 8,181 of them filed exactly 1, and only 139 filed 2 or more (6
filed 3, 2 filed 4). There's almost no variation in ticket count to find a
pattern in.

**Verdict: noise** (and a low-variance field to begin with).

### 5. Industry x Product and Region x Product

We checked whether particular industries or regions lean toward particular
products, both in raw usage-row counts and in average Active Days.

- Chi-square on Industry x Product (row percentages, based on 42,210 usage
  rows): chi2 = 154.6 on 36 degrees of freedom, which looks significant on
  its own, but with 42,210 rows even tiny differences become
  "statistically significant." The actual effect size, Cramer's V = 0.030,
  says the relationship is close to nothing. Row percentages by industry
  only range roughly 17%-24% per product, versus an even 20% for 5
  products.
- Chi-square on Region x Product: chi2 = 105.1 on 16 degrees of freedom,
  Cramer's V = 0.025. Same story: statistically detectable purely because
  of sample size, practically flat (17%-23% per product by region).
- Average Active Days by Industry x Product and by Region x Product both
  reproduce the already-known per-product pattern (Jira highest, Loom
  lowest) inside every single industry and region, in roughly the same
  order and magnitude. There's no industry or region that inverts or
  meaningfully bends the product-level pattern already established.
- One relevant structural fact that shapes how to read all of this: 8,202
  of 8,320 customers (98.6%) use exactly one product across the whole
  five-month window. So "Industry x Product" is really "which single
  product got assigned to this customer, by industry," not a mix of
  products per account.

**Verdict: noise.** No industry or region shows a real product
preference; the pattern in every cross-tab is just the already-known
product-level usage difference showing up identically everywhere.

### 6. Embeddedness (Collaborators, Integrations Used) vs. Plan Type and Company Size

- By Plan Type: Integrations Used averages 1.14 (Free) -> 2.40 (Standard)
  -> 4.10 (Premium) -> 5.99 (Enterprise), a spread of 4.85, roughly a 5x
  difference between the bottom and top tier. Collaborators averages 9.82
  (Free) -> 11.02 (Standard) -> 11.53 (Premium) -> 11.88 (Enterprise), a
  spread of 2.07. Both climb monotonically with tier, the same shape as
  the already-confirmed Active Days-by-tier pattern.
- By Company Size: Collaborators spread is 0.14 (11.00 to 11.15) and
  Integrations Used spread is 0.13 (3.11 to 3.24), both flat.

**Verdict: real signal for Plan Type, noise for Company Size.**
Embeddedness scales with what a customer pays for, not with how big their
company is. This adds to, rather than overturns, the existing "usage
scales with plan tier" finding: Integrations Used is actually a sharper
tier signal than Active Days (a ~5x spread vs. Active Days' ~2x spread
from Free to Enterprise).

### 7. Subgroup with a real declining trend inside the 5-month window

We fit a straight-line slope of Active Days across Jan-May 2023 for every
customer and bucketed them as declining (slope < -0.5 days/month), flat
(-0.5 to +0.5), or rising (slope > +0.5).

- The slope distribution across all 8,320 customers: mean = -0.014,
  standard deviation = 0.666, and the 25th/50th/75th percentiles are
  -0.40 / 0.00 / +0.40. That's a distribution centered almost exactly on
  zero and symmetric in both directions.
- Bucket sizes: 1,863 declining (22.4%), 4,828 flat (58.0%), 1,629 rising
  (19.6%). Declining and rising are close in size (22.4% vs 19.6%),
  meaning there's no overall skew toward decline. This matches, and
  reinforces, the already-established "flat persistence" finding: month to
  month movement looks like noise around a stable personal average, not a
  trend.
- Plan Type does show a real split in bucket membership: Free customers
  land in "flat" 66.2% of the time (only 18.2% declining), while
  Enterprise customers land in "flat" only 50.7% of the time (26.9%
  declining). Chi-square = 74.9 on 6 degrees of freedom, Cramer's V =
  0.067, a small but real effect, larger than most others in this report.
  The likely explanation is not that Enterprise customers are at more
  churn risk: Free customers sit near a low usage floor (~5.3 days/month)
  where there's less room to move up or down, while Enterprise customers
  sit around 11.5 days with more numerical room to swing either way. The
  "declining" and "rising" buckets both grow at the same time for
  Enterprise (26.9% and 22.5%), which is consistent with a
  higher-baseline group having more raw variance, not with directional
  decline being more common at that tier.
- Ticket status (open/pending vs. all closed) has effectively no
  relationship to which trend bucket a customer falls into: chi2 = 6.5 on
  2 degrees of freedom, Cramer's V = 0.028.

**Verdict: noise (no real decline signal), with one real but explainable
scale artifact.** There is no subgroup that's actually trending down more
than chance would produce. The Plan Type split in bucket membership is a
statistically real pattern, but it's a byproduct of Enterprise customers
having a higher, more variable usage baseline, not evidence of an
at-risk cohort distinct from what's already captured by comparing usage
within a plan tier.

### 8. Other checks

- Every single customer in `customers.csv` (8,320 of 8,320) has filed at
  least one ticket, at every Plan Type, 100% each. This is a structural
  fact about how the dataset was built (ticket volume is confirmed flat
  at ~1.0-1.02 per customer everywhere), not a discovery: there's no
  "never contacted support" segment to find in this data.
- A ticket's "Product Purchased" field lines up with what the customer
  actually uses in `product_usage.csv` 100% of the time: every
  ticket-filer's stated Product Purchased matches a product that
  shows up in their own usage rows. This is worth calling out separately
  from the other ticket fields, because it is *not* a trivial check:
  98.6% of customers (8,202 of 8,320) only use one product across the
  whole five-month window, so this isn't "everyone uses everything
  anyway." Product Purchased is internally consistent with the real usage
  data, unlike Ticket Type, Ticket Subject, Priority, and Channel, which
  are confirmed randomly assigned. It's a real, if narrow, fact about the
  ticket file: which product a customer complained about is trustworthy,
  even though nothing else about the ticket (why, how urgent, how it went,
  how satisfied they were) is.

## So what

None of this changes the team's core story. The plan-tier / product usage
engagement analysis is still the only place in this dataset with real,
checkable signal, and this pass adds one useful reinforcement to it:
Integrations Used scales with Plan Type even more sharply than Active Days
does (about a 5x spread from Free to Enterprise vs. about 2x for Active
Days), so embeddedness by integrations is a second, corroborating way to
rank engagement within a tier, not just a nice-to-have side stat.

On the ticket side, this pass does not overturn the audit finding. Every
ticket-level categorical field we hadn't yet tested (Age, Gender, Ticket
Subject, Ticket Status, ticket count) comes back the same way Ticket Type,
Priority, Channel, and Satisfaction already did: no real relationship to
anything, including to the "real" half of the data. The one new fact worth
keeping is narrow: the Product Purchased field on a ticket is genuinely
tied to what that customer uses, so it's not fabricated. But it doesn't
unlock anything new, since which tickets are worse, how they were handled,
and how the customer felt about it all remain unanswerable questions in
this dataset. The recommendation to the client stands as already written:
the usage-engagement analysis is what we can stand behind, and the ticket
data's audit finding is what we tell them needs to be captured differently
before it can answer the brief's actual question.
