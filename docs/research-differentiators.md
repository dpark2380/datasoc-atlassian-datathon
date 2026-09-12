# Research: two differentiating additions

Question asked: find one or two things this team could build in about a day
that other teams almost certainly would not think of, checked against primary
sources.

All web sources were fetched on 12 September 2026. Every figure below is
either quoted from the named document or is arithmetic on figures from it,
and I say which. Where I could not verify something I say so instead of
estimating.

The two things I recommend building are in sections 1 and 4. Sections 2, 3, 5
and 6 are avenues I checked and am ruling out or downgrading, with the reason.

---

## 1. Revenue concentration, from Atlassian's own SEC filings

This is the strongest finding. Atlassian publishes, in documents filed with
the SEC, exactly the number the team has been refusing to invent.

### The figures

From Atlassian's Q4 FY26 shareholder letter, filed as an exhibit to a Form
8-K on 6 August 2026, covering the fiscal year ended 30 June 2026
(https://www.sec.gov/Archives/edgar/data/1650372/000165037226000031/teamq42026shareholderlet.htm):

> "We ended Q4'26 with 57,334 customers with greater than $10,000 in Cloud
> ARR. This cohort accounts for over 85% of total Cloud ARR."

The same letter reports ">350K customers across all industries" and ">700
customers with $1M+ in ARR".

From Atlassian's Form 10-K for fiscal year 2026, filed 14 August 2026
(https://www.sec.gov/Archives/edgar/data/1650372/000165037226000036/team-20260630.htm):

| Figure | Value | Where in the 10-K |
|---|---|---|
| Customers with >$10,000 Cloud ARR at 30 Jun 2024 | 45,842 | Customer metrics table, Item 7 |
| Customers with >$10,000 Cloud ARR at 30 Jun 2025 | 51,978 | same table |
| Customers with >$10,000 Cloud ARR at 30 Jun 2026 | 57,334 | same table |
| Total customers at 30 Jun 2026 | "more than 350,000" | Item 7, customer metrics |
| FY26 Cloud revenue | $4,410,627 thousand | Revenues by deployment option |
| FY26 total revenue | $6,572,308 thousand | same table |
| FY26 research and development expense | $3,269,257 thousand, 50% of revenue | Results of operations table |
| FY26 marketing and sales expense | $1,541,178 thousand, 24% of revenue | same table |

The 10-K also states, verbatim:

> "Customers with greater than $10,000 in Cloud ARR represent the majority of
> our Cloud revenue."

> "We are focused on continuing to grow our total customer base, specifically
> the number of customers with more than $10,000 in annualized recurring
> revenue from our Cloud offerings ('Cloud ARR'), as it measures our ability
> to successfully expand within our existing customer base."

> "We believe our ability to attract new customers is critical, and expanding
> within the existing customer base is the primary driver of our success as a
> business."

The one arithmetic step the team would take: 57,334 divided by 350,000 is
16.4%, and because the 10-K says "more than 350,000", the true share is at or
below 16.4%. So roughly one account in six holds over 85% of Cloud ARR. That
is a division of two published numbers, nothing more.

### Why this is the thing to build

The team's self-imposed rule was no invented dollar figures. This removes the
need for one. The slide is not "we assume $X ARR per tier". The slide is
"Atlassian told its shareholders that 16% of its accounts hold over 85% of
Cloud ARR, and our rule ranks accounts inside that shape".

It also answers the brief's own example of a good insight ("here's why 23% of
customers are at risk and what to do about it") with a real denominator
attached, which the brief's bad example lacks.

### The Q&A quote to keep in the back pocket

The 10-K risk factors contain this sentence, which is Atlassian stating the
team's problem in Atlassian's own words:

> "Additionally, we may be unable to timely address any retention issues with
> specific customers, which could harm our results of operations."

The word doing the work there is "specific". Atlassian's own filing says the
risk is not knowing which customers. That is the gap the usage-based rule
fills.

### Feasibility

No code. One slide plus one backup slide. About an hour including checking
the quotes against the filings. The team must open both documents themselves
before presenting, because a judge who works at Atlassian may well know these
numbers.

### Caveat the team must state

Cloud ARR and Cloud revenue are different measures and Atlassian says so
explicitly ("Cloud ARR and Cloud MRR should be viewed independently of
revenue and do not represent our revenue under GAAP"). Do not multiply 85% by
$4.41B and present the product as a dollar figure. State the 85% and the 16%
as the published ratios they are, and state Cloud revenue separately as
context for scale. Also state plainly that the 8,320 customers in the
datathon dataset are not Atlassian's customers, so the concentration figure
describes the business the method would run in, not the sample.

---

## 2. List pricing crossed with Company Size: ruling this out

I got the prices. The problem is the other half.

### What I verified

Fetched 12 September 2026 from the schema.org `Product`/`Offer` structured
data embedded in Atlassian's own pricing pages. These are the per-user,
per-month rates the page publishes at its default view.

| Product | Free | Standard | Premium | Enterprise | Page |
|---|---|---|---|---|---|
| Jira | $0, max 10 users | $7.91 | $14.54 | not priced in markup | https://www.atlassian.com/software/jira/pricing |
| Confluence | $0 | $6.70 | $13.20 | not priced in markup | https://www.atlassian.com/software/confluence/pricing |
| Bitbucket | $0 | $3.65 | $7.25 | not offered | https://www.atlassian.com/software/bitbucket/pricing |

I could not verify Trello or Loom prices. Both pages render their price
tables entirely in client-side JavaScript and expose no structured data, so
there is nothing to quote without driving a browser. Do not put a Trello or
Loom number on a slide unless someone on the team opens the page and reads it
off.

Enterprise has no published per-seat rate on any of these pages. It is
quote-based and annual only. Any Enterprise-tier dollar figure would be
invented, which is the thing the team decided not to do.

### Why I am ruling it out anyway

To turn a per-seat price into an account value you need a seat count. The
only candidate in the data is `Company Size` in customers.csv, and that column
carries no signal. I tested it:

Mean monthly usage by Company Size band, across all 8,320 customers:

| Company Size | Active Days | Sessions | Product Actions | Collaborators | Integrations |
|---|---|---|---|---|---|
| 1-10 | 8.99 | 17.95 | 102.69 | 11.14 | 3.12 |
| 11-50 | 8.72 | 17.46 | 100.06 | 11.05 | 3.18 |
| 51-200 | 8.85 | 17.76 | 102.32 | 11.15 | 3.21 |
| 201-500 | 8.57 | 17.13 | 98.60 | 11.01 | 3.12 |
| 501-1000 | 8.64 | 17.20 | 98.62 | 11.01 | 3.24 |
| 1000+ | 8.55 | 17.10 | 97.67 | 11.04 | 3.12 |

One-way ANOVA of Active Days on Company Size gives p = 0.159. A chi-square
test of Company Size against Plan Type gives p = 0.439, so the two are
independently assigned. A 1000+ employee company in this dataset is no more
likely to be on Enterprise than a 1-10 employee company is, and uses the
products no more heavily.

So `Company Size` belongs in the same bucket as Ticket Priority and Channel:
a column that was generated independently of everything else. Building
account value on it would put an invented seat count under a real price,
which is worse than inventing the price, because it looks sourced.

There is a smaller version that survives. Plan Type is real and does drive
usage, and the published price ladder ($0, $6.70 to $7.91, $13.20 to $14.54)
is real. The team can say "the plan ladder the risk model weights by is the
same ladder Atlassian publishes, and the step from Standard to Premium is
roughly a doubling of list price per seat". That is a sourced sanity check on
the tier weighting, not an account-value model. Worth one line on a backup
slide, not worth a build.

---

## 3. Atlassian's published statements on adoption and stickiness

Two of these are directly useful. The rest I checked and would skip.

### Useful: integration depth and stickiness

Q4 FY26 shareholder letter, same SEC exhibit as section 1:

> "MCP adopters are significantly stickier, expand their paid seats faster,
> and grow their ARR at rates 2x faster than non-adopters."

This matters because the team's embeddedness score is built on
`Integrations Used`. Atlassian has just told shareholders that the customers
who connect more tools into the platform are stickier and expand faster. The
team can put that quote next to their own finding that Integrations Used runs
from 1.1 on Free to 6.0 on Enterprise and is the sharpest tier discriminator
in the dataset. That is the "Atlassian said X, we found Y" structure the brief
rewards, sourced to a filed document rather than a blog.

The same letter also reports "Rovo adopters continue to grow their ARR more
than 2x faster than non-adopters" and "Customers that adopt Rovo are
completing 20% more Jira work items and creating/editing 25% more Confluence
pages versus non-adopters". These say the same thing in a different product:
Atlassian itself measures customer health as depth of product action counts,
which is exactly what product_usage.csv contains.

### Useful: Atlassian's support model is low-touch by design

From the FY26 10-K, Item 1:

> "Our model focuses on a land-and-expand strategy, with automated and
> low-touch customer service, superior product quality, and transparent
> pricing to land new customers and the initial expansion to new users and
> teams."

> "To land new customers, we've engineered a frictionless flywheel with an
> emphasis on self-service."

> "Relative to other enterprise software companies, we invest significantly
> more in research and development relative to marketing and sales."

The R&D and marketing lines in the same filing back that up: $3,269M of R&D
against $1,541M of marketing and sales in FY26.

This is the bridge from the team's data audit to the team's solution. The
argument becomes: Atlassian's support is deliberately automated and low-touch,
which means support tickets are a thin and late signal about account health
by design, not by accident. Usage telemetry has to carry the load. That turns
"the ticket file is random" from a complaint about the dataset into a
statement about how Atlassian's business actually works.

### Checked and skipping: net revenue retention

I could not verify an NRR figure from a primary source. The FY26 10-K
contains no instance of "net revenue retention" or "net expansion rate".
Atlassian does not disclose the metric in its filings. The widely repeated
"approximately 120%" traces to earnings call commentary and third-party
trackers, not a filed document. Do not put it on a slide. The >$10,000 Cloud
ARR cohort figures in section 1 do the same job and are filed.

### Checked and downgrading: the Atlassian Team Playbook Health Monitor

https://www.atlassian.com/team-playbook/health-monitor is real, is
Atlassian's own, and is free. It is a self-assessment a team runs on itself
against eight attributes in a 90-minute session. It is not a customer health
scoring method and does not use telemetry. It is usable as a one-line
rhetorical hook (Atlassian publishes a health monitor for teams, and the
recommendation extends the same habit to accounts) but it is not evidence and
should not be presented as methodological support.

---

## 4. Reliability analysis of the usage panel, and a permutation test on trend

This is the second thing to build. It is a genuinely appropriate technique for
label-free data, it takes about two hours, and it turns up a result the team
needs to know before Monday regardless of whether they present it.

### What I found

The five-month panel has no temporal structure at all. Correlation of Active
Days between months, all pairs:

| | Jan | Feb | Mar | Apr | May |
|---|---|---|---|---|---|
| Jan | 1.000 | 0.821 | 0.821 | 0.819 | 0.816 |
| Feb | 0.821 | 1.000 | 0.818 | 0.826 | 0.819 |
| Mar | 0.821 | 0.818 | 1.000 | 0.817 | 0.818 |
| Apr | 0.819 | 0.826 | 0.817 | 1.000 | 0.820 |
| May | 0.816 | 0.819 | 0.819 | 0.820 | 1.000 |

In any real behavioural series, adjacent months correlate more strongly than
distant ones. Here Jan-to-Feb is 0.821 and Jan-to-May is 0.816. The matrix is
flat. Each customer has a fixed level plus independent monthly noise, and
nothing carries over from one month to the next beyond that level.

I confirmed this two ways. First, a permutation test: shuffle the five month
labels within each customer-product row, refit a per-row linear slope, and
compare the spread of real slopes to the shuffled ones.

| Metric | SD of observed slopes | SD of slopes after shuffling months | Ratio |
|---|---|---|---|
| Active Days | 0.6682 | 0.6560 | 1.019 |
| Sessions | 1.0218 | 1.0231 | 0.999 |
| Integrations Used | 0.4000 | 0.4023 | 0.994 |

Second, a split-half check: the slope over Jan to Mar against the slope over
Mar to May correlates at -0.49, -0.49 and -0.51 for those three metrics. A
customer genuinely declining would show these two slopes agreeing. A value
near -0.5 is what pure mean-reverting noise produces when the two halves
share a middle month.

So every trend, slope and percent-change feature computable from this panel is
noise. `combined_dataset.csv` already carries ten such columns (Active Days
Slope, Active Days Pct Change, and so on for each metric). None of them mean
anything.

Then the reliability side. Splitting each metric's variance into the part that
differs between customers and the part that differs between months within a
customer gives an intraclass correlation, and from that the reliability of the
five-month average:

| Metric | ICC, single month | Reliability of the 5-month mean |
|---|---|---|
| Sessions | 0.892 | 0.976 |
| Active Days | 0.820 | 0.958 |
| Product Actions | 0.668 | 0.910 |
| Integrations Used | 0.592 | 0.879 |
| Collaborators | 0.122 | 0.410 |

Four of the five metrics are highly reliable once averaged over five months.
Collaborators is not. An ICC of 0.122 means 88% of the month-to-month
variation in a customer's Collaborators count is noise, and averaging five
months only gets the reliability to 0.41.

### Why this matters to the team's own model right now

`analysis/eda.py` sets `EMBEDDEDNESS_WEIGHTS = {"Collaborators": 1,
"Integrations Used": 2}`. One third of the embeddedness weight sits on the one
variable in the file with almost no per-customer persistence. The existing
sensitivity check varies the ratio between them, which is the right instinct,
but it cannot detect this because it only tests how much the category split
moves, not whether the underlying measurement is stable.

The fix is a one-line change and a sentence on the slide. The team can either
drop Collaborators from embeddedness and say why, or keep it and state the
reliability figure openly. Either is defensible. Silently keeping it is the
only option that is not.

The second thing to check is the "Established & Declining" label. `eda.py`
defines that category by tenure and plan tier, not by any trend, which is
correct given the above. But the word "Declining" claims a trajectory the data
cannot support, and a judge asking "declining relative to what?" would be
asking a fair question with no good answer. Renaming it to something about
level rather than direction removes the exposure.

### What goes on the slide

The team already has a strong audit slide for the ticket file. This is the
same move applied to the file they built on, and it is more impressive
because it cuts against their own work rather than the organisers'. The line
is roughly: we ran the same audit on the data we did trust, kept the four
variables that survived, and threw out every trend feature in the file after
testing them against a shuffled null.

It also pre-empts the most likely technical question in Q&A. Any judge looking
at a five-month panel will ask why there is no trend analysis. The permutation
test is the answer, and it is a better answer than "the window was too short".

### Feasibility

Both computations are about thirty lines of pandas and numpy against
product_usage.csv, and both already run in the repo's venv. Budget two to
three hours including the slide and the decision about Collaborators. The
numbers above are reproducible; the seed for the permutation was 0.

---

## 5. Techniques checked against these three files and ruled out

### Survival analysis and time-to-event

Not possible. `Active Days` never takes the value 0 anywhere in
product_usage.csv. Minimum is 1, maximum is 31, and all 8,320 customers appear
in all five months for their product. There is no lapse, no dormancy, no
disappearance, and therefore no event to time. Survival analysis needs an
event and this file contains none.

### Cohort retention curves

Not possible, for two reasons. Every customer is present in every month, so
any retention curve is flat at 100% by construction. And `Account Created
Date` spans July 2018 to December 2021 but correlates with usage at 0.006 for
Active Days, 0.006 for Collaborators and -0.002 for Integrations Used. Signup
cohort predicts nothing, so cohort curves would be five flat identical lines.

### RFM adapted for SaaS

Recency is unusable: no customer has a gap, so every customer's recency is
identical. Frequency and monetary reduce to the usage composite and the plan
tier the team already uses. RFM here is the existing model with worse naming.

### Uplift modelling

Uplift needs a treatment assignment and an outcome. The dataset has neither.

### What does hold up

The reliability analysis in section 4 is the technique that fits. It needs no
labels, no outcomes and no time dimension. It answers a question the team is
already answering informally ("which columns are real?") with a number per
column, and it is unusual enough in a student datathon that it will read as
genuine statistical maturity rather than a library call.

---

## 6. Ranked recommendation

### First: the concentration slide from Atlassian's filings

Build it. About an hour, no code, entirely deck work plus reading two SEC
documents.

It differentiates because every other team will either skip business impact
entirely or invent an ARR assumption. This team can put a filed number on the
screen. The Solution and Recommendation criterion carries 35% of the score and
is where an unsourced dollar figure gets punished hardest in Q&A.

The sentence no other team can say: "Atlassian told its shareholders in August
that 57,334 accounts, about one in six of its 350,000 customers, hold over 85%
of Cloud ARR. Our rule ranks accounts by disengagement inside a book shaped
like that, using only telemetry Atlassian already collects."

Pair it with the risk factor quote about being "unable to timely address any
retention issues with specific customers" and the statement that Atlassian's
customer service is "automated and low-touch" by design. Those two together
explain why the ticket file could not have carried this signal even if it were
real.

### Second: the reliability and permutation slide

Build it. Two to three hours including the decision about Collaborators.

It differentiates because it is the team auditing itself. The data audit the
team already has is good but it is an audit of someone else's file. Running
the same test on their own features, finding that one of their five inputs is
88% noise in any given month, and changing the model because of it, is a
different and better kind of credibility. It also converts the most awkward
Q&A question about the five-month window into a prepared answer.

The sentence no other team can say: "We shuffled the month labels and refit
every trend feature. The real slopes were indistinguishable from the shuffled
ones, so we deleted all ten trend columns and kept only the four variables
whose five-month averages are reliable above 0.87."

### Do not build

Any account-value model built on Company Size. It fails the same independence
test the ticket fields fail, at p = 0.44 against Plan Type and p = 0.16
against usage, and dressing an invented seat count in a real list price is
more dangerous than not having a dollar figure at all.

Any slide carrying a net revenue retention figure. Atlassian does not disclose
it in its filings and I could not verify it from a primary source.

Any Trello or Loom price, unless someone on the team opens the page and reads
it.

---

## Source list

| Document | Period covered | URL |
|---|---|---|
| Atlassian Form 10-K, FY2026, filed 14 Aug 2026 | Fiscal year ended 30 Jun 2026 | https://www.sec.gov/Archives/edgar/data/1650372/000165037226000036/team-20260630.htm |
| Atlassian Q4 FY26 shareholder letter, 8-K exhibit, filed 6 Aug 2026 | Quarter and fiscal year ended 30 Jun 2026 | https://www.sec.gov/Archives/edgar/data/1650372/000165037226000031/teamq42026shareholderlet.htm |
| Atlassian Q4 and FY2026 earnings release, 6 Aug 2026 | Quarter and fiscal year ended 30 Jun 2026 | https://www.sec.gov/Archives/edgar/data/1650372/000165037226000031/ex991q4fy26.htm |
| Atlassian Form 10-K, FY2025, filed 15 Aug 2025 | Fiscal year ended 30 Jun 2025 | https://www.sec.gov/Archives/edgar/data/1650372/000165037225000036/team-20250630.htm |
| Jira pricing page | Retrieved 12 Sep 2026 | https://www.atlassian.com/software/jira/pricing |
| Confluence pricing page | Retrieved 12 Sep 2026 | https://www.atlassian.com/software/confluence/pricing |
| Bitbucket pricing page | Retrieved 12 Sep 2026 | https://www.atlassian.com/software/bitbucket/pricing |
| Atlassian Team Playbook Health Monitor | Retrieved 12 Sep 2026 | https://www.atlassian.com/team-playbook/health-monitor |

All statistics in sections 2, 4 and 5 were computed directly from
`references/Dataset/customers.csv` and `references/Dataset/product_usage.csv`
in this repository on 12 September 2026, using the project venv. They are not
quoted from any external source and are reproducible from those two files.
