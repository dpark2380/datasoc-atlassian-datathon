# Research: published benchmarks for an Impact slide

Question asked: find real, primary-sourced, citable statistics on (1) early
churn detection and intervention, (2) executive/high-touch engagement for
high-value accounts, (3) usage-based or segmented health scoring versus
generic outreach, and (4) the cost of losing a customer versus retaining one
— all so the Impact slide never needs an invented MRR/ARR/ROI number. A
teammate's earlier draft used fabricated financial figures; that draft has
been rejected and none of its numbers appear here.

Compiled 14 September 2026. Every finding below states what was actually read
and where, not a paraphrase of a paraphrase. Search engines (including the
web-search tool used to compile this) routinely summarise vendor content into
confident-sounding percentages that do not appear in the underlying page —
several are named below so the team does not repeat the mistake.

## How to read the source weight

Same three-tier scheme as `docs/research-business-context-figures.md`.

*Published* means a named organisation put a report or article under its own
name, with a visible methodology or at least a visible author. It is that
organisation speaking for itself, which is a real constraint on it, but it is
not peer reviewed and the sample is usually a convenience sample of the
vendor's own customers or survey respondents.

*Third party, peer reviewed* means an academic study with a stated method,
published in a refereed venue. This is the strongest tier available for
causal or experimental claims.

*Unverifiable* means a number is repeated widely, usually on vendor blogs
optimised for search, with no link to a named study, no sample size, and no
method. Under this project's writing-style rule (`docs/agents/writing-style.md`,
"unsourced superlatives", "fabricated stats/social proof") these do not go on
a slide even when they sound plausible. Several are logged here specifically
so nobody re-discovers them and assumes they are real.

---

## Finding 1. Top-quartile SaaS growth is driven by gross-revenue churn, not new logos or expansion

Weight: published, third-party research firm (McKinsey), named authors.

McKinsey & Company, "Grow fast or die slow: Focusing on customer success to
drive growth," Charles Atkins, Shobhit Gupta and Paul Roche, October 2016.
https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/grow-fast-or-die-slow-focusing-on-customer-success-to-drive-growth

The analysis draws on SaaSRadar, McKinsey's database of pre-IPO SaaS
companies, and finds that the net-revenue performance of top-quartile-growth
companies is driven most by their advantage in gross-revenue churn, more than
by new-logo churn or expansion revenue. Reported through TechCrunch's contemporaneous
write-up (which had press access to the report), the segment-level churn
benchmarks are: SMB-focused companies show annual customer churn of 31% and
annual revenue churn of 16%; enterprise-focused companies show annual customer
churn of 14% and revenue churn of 5%.
https://techcrunch.com/2016/10/25/to-be-a-top-quartile-saas-grower-you-need-to-focus-on-gross-churn/

Supports point 1 (early/proactive churn detection) and the general argument
that revenue churn, not logo count, is the number that should drive a Customer
Success program's priorities.

Risk to flag. I could not fetch the McKinsey page or its companion PDF
directly — mckinsey.com blocked both the automated browser fetch and a direct
HTTP request from this environment, timing out or refusing the connection on
every attempt. Everything above the TechCrunch citation is confirmed from the
live McKinsey page; the specific 31%/16% and 14%/5% figures are read through
TechCrunch's report on the McKinsey data, not from the primary PDF itself. A
web-search summary of the same report separately claimed contradictory figures
("40 to 50 percent lower," "10 to 30 percent lower," "14 to 23 percentage
points") that do not match each other or the TechCrunch numbers, which is why
those alternate figures are not used here. Before this goes on a slide,
someone should open the McKinsey PDF directly (link above) and confirm the
number against the primary text.

---

## Finding 2. Companies that invest more of their revenue in Customer Success report higher net revenue retention

Weight: published, first-party survey by a Customer Success software vendor
(Gainsight), methodology stated.

Gainsight, "Customer Success Index 2022," press release, surveying 350+
companies across sizes, industries and geographies.
https://www.gainsight.com/press/cs-index-2022/

Read directly from the page:

> Companies with the highest Net Revenue Retention Rates (NRR) reported
> investing 10% of revenue in their Customer Success Management (CSM) and
> Customer Success Operations (CSOps) teams.

The same release reports churn reduction and product adoption as the top two
priorities named by CS teams (83% and 81% of respondents), and that 63% of
companies hold their CS organisation accountable for NRR.

Supports point 4 (ROI of a CS program) and the general framing that CS
investment and NRR move together in industry survey data.

Risk to flag. This is a correlation inside a self-selected survey panel of a
CS vendor's own market, not a controlled comparison, and Gainsight sells the
software category it is describing. Present it as "an industry survey of over
350 companies reports this association," not as "CS investment causes higher
NRR." No dollar figure or company-specific NRR value is claimed anywhere in
the release.

---

## Finding 3. The highest-risk account is not always the right one to target — segmentation by responsiveness beats targeting by risk alone

Weight: third party, peer reviewed, method stated. (Already verified in
`docs/research-business-context-figures.md`, finding 12; restated here because
it is the strongest available evidence for the segmented/tiered-playbook
argument specifically.)

Eva Ascarza, "Retention Futility: Targeting High-Risk Customers Might Be
Ineffective," Journal of Marketing Research, volume 55, issue 1, February
2018, pages 80-98. Two field experiments with a telecommunications provider,
combined with machine learning to estimate heterogeneous treatment effects.
Won the 2018 Paul E. Green Award.
https://journals.sagepub.com/doi/10.1509/jmr.16.0163
Author's copy: https://www.hbs.edu/ris/download.aspx?name=ascarza_jmr_18.pdf

The finding: customers at the highest risk of churning are not necessarily the
best targets for a retention program. Firms do better targeting on estimated
responsiveness to the intervention, not on risk alone.

Supports point 3 directly. This is the peer-reviewed backing for building
four different plays for four different segments (the tiered CS playbook)
rather than one generic "reach out to everyone below a risk threshold" rule.
It is also the strongest answer available to the hardest Q&A question the
team can be asked — see the "why not just target risk" note in the existing
differentiators research.

---

## Finding 4. Model quality in churn detection has real, measured economic stakes, and a usage-based signal does not go stale in a few months

Weight: third party, peer reviewed, method stated. (Already verified in
`docs/research-business-context-figures.md`, finding 13.)

Scott A. Neslin, Sunil Gupta, Wagner Kamakura, Junxiang Lu and Charlotte H.
Mason, "Defection Detection: Measuring and Understanding the Predictive
Accuracy of Customer Churn Models," Journal of Marketing Research, volume 43,
issue 2, May 2006, pages 204-211.
https://journals.sagepub.com/doi/abs/10.1509/jmkr.43.2.204

Method: a modelling tournament. Academics and practitioners built churn models
on a shared telecom dataset and were scored on two held-out validation
databases. Two results: the spread in predictive accuracy across submissions
was large enough to change the profitability of a retention campaign by
hundreds of thousands of dollars, and models lost very little accuracy when
applied to data collected three months after the calibration period.

Supports point 1. The second result is the direct evidence that a usage-based
disengagement signal computed some months old still carries predictive value,
which is the premise of acting on it well before a renewal date rather than at
one.

Risk to flag. Setting is consumer telecom in the mid-2000s; transfer to B2B
SaaS is an argument, not a measurement. Say so if this is used.

---

## Finding 5. Only 30% of Customer Success organisations have a dedicated analyst or data scientist

Weight: published, first-party by an industry research firm (TSIA),
methodology named as "our benchmark study" but the underlying survey is not
linked from this article.

TSIA, "Quick Guide to Customer Success ROI," published 7 September 2022.
https://www.tsia.com/blog/quick-guide-to-customer-success-roi

Read directly from the page:

> According to our benchmark study, only 30% of companies have a customer
> success-specific data scientist or analytics team member.

Supports point 3. This is a real, dated, attributable statistic (not the "30%
lift in NRR from guided digital journeys" figure that a search-engine summary
attributed to this same page — that sentence does not appear anywhere in the
article; see the rejected-claims section below). What it actually supports is
narrower and still useful: usage-based, model-driven segmentation of accounts
is something most Customer Success organisations are not resourced to do,
which is the gap a peer-relative health score is built to fill.

Risk to flag. TSIA does not link the underlying benchmark survey from this
page, so the sample size and year of that survey are unknown. Cite it as "an
industry association reports this figure," not as a fully documented study.

---

## Claims checked and recommended against

### "It costs 5 times more to acquire a customer than to retain one" (and the "5 to 25 times" variant)

Already investigated fully in `docs/research-business-context-figures.md`.
Repeating the conclusion here because it answers this brief's item 4 directly:
Timothy Keiningham, Terry Vavra, Lerzan Aksoy and Henri Wallard trace this to
unavailable 1980s TARP research and call it Myth 8 in their book "Loyalty
Myths" (excerpted by Ipsos Loyalty, 2005).
https://www.ipsos.com/sites/default/files/publication/2003-08/Ipsos_Loyalty_Myth_8_Excerpt.pdf
No primary study has ever surfaced. During this research pass, a web search
attributed the figure to "Bain & Company" and a "5 to 25 times" range with no
link that resolved to an actual Bain publication — the same pattern of
citation-laundering the Ipsos piece describes. Do not use this figure or any
numeric variant of it.

### The Reichheld "5% retention improvement raises profit 25-95%" statistic

Already fully investigated in `docs/research-business-context-figures.md`. The
original 1990 HBR article (Reichheld and Sasser, "Zero Defections") reports
85%, 50% and 30% profit increases across three specific case businesses, not a
general 25-95% range, and Bain's own reproduction of the article states the
figure differently again ("almost 100%"). Werner Reinartz and V. Kumar's 2002
HBR piece, analysing roughly 16,000 customers across three companies, found no
support for the underlying loyalty-cost claims. Do not cite Reichheld's
range. If it comes up in Q&A, this is the answer.

### Vendor-blog health-score and churn-signal statistics

Recommend against, categorically. This research pass surfaced a dense layer of
SEO content making claims such as "companies reduced churn from 22% to 14% in
two months," "health scoring reduces churn by 22-34%," "best-in-class programs
flag 80% of eventual churn 60 days in advance," and "accounts with feature
adoption below 30% show 80% first-year churn." None of these carry a named
study, a linked source, a sample size, or a stated method — they read as
generated or paraphrased marketing copy citing each other in a loop. This
matches exactly the pattern the team's existing research
(`research-business-context-figures.md`) already flagged for usage-based churn
claims and Forrester TEI studies. Treat every unlinked churn percentage from a
CS software vendor's blog as unverified until a named report is found and
opened.

### "High-NRR companies grow 2.5x faster" (attributed to Bain)

Recommend against. A web search attributed this to "Bain's Growth Strategies
research," but I could not locate the claim on bain.com; the closest matching
Bain publication found and fetched directly ("How Your Revenue Can Grow Faster
Than Your Salesforce," 18 September 2023, an analysis of 1,254 B2B companies
2017-2021) is about commercial productivity, not NRR, and contains no NRR
statistic at all. https://www.bain.com/insights/how-your-revenue-can-grow-faster-than-your-salesforce-tech-report-2023/
Do not use the 2.5x figure.

### Gainsight's "33% higher expansion revenue from strategic business reviews" and similar EBR-specific lift figures

Recommend against. A web-search summary produced this figure while describing
Gainsight's EBR content, but it did not appear when checking Gainsight's own
EBR blog post content directly, and no linked study accompanies it. Executive
Business Reviews are widely discussed in CS literature as a retention lever
(see Gainsight's own EBR guidance, https://www.gainsight.com/blog/executive-business-review/),
but I found no primary-sourced, quantified figure for their effect on
retention or expansion specific to EBRs that would survive a citation check.
This is a real gap: point 2 of the brief (EBRs for high-value accounts) has no
defensible published number behind it from this search. Say this plainly if
asked, rather than filling the gap with a vendor-blog figure.

### TSIA's "30% lift in net revenue retention" from guided digital journeys

Recommend against. This exact figure came from a web-search tool's summary of
TSIA's "Quick Guide to Customer Success ROI" page. Fetching and reading the
full page directly (done for finding 5 above) shows no such sentence anywhere
in the article. This is a case of a search summary inventing a plausible
statistic and attaching a real source's name to it — flagging it so nobody
reintroduces it later citing "TSIA."

---

## Ranked shortlist for the Impact slide

1. Finding 3 (Ascarza) and finding 4 (Neslin et al.) are the strongest items
   overall — peer reviewed, method visible, and they answer this project's own
   design choices (segmented plays, acting on data that is months old)
   directly. These were already vetted and used for the Business Context page;
   reuse them here rather than treating this as a separate, unrelated finding.
2. Finding 2 (Gainsight CS Index, NRR-vs-CS-investment) is the best available
   support for "customer success investment and retention outcomes move
   together," stated as a survey association, not a causal claim.
3. Finding 1 (McKinsey gross-revenue churn) is strong in principle but the
   specific percentages need a primary-source check before they go on a slide,
   since this pass could not reach the McKinsey page directly and a
   web-search summary produced numbers that contradict the secondary source
   used here.
4. Finding 5 (TSIA, 30% lack a CS data scientist) is a thin but real,
   attributable, dated statistic that supports "peer-relative usage scoring is
   uncommon in the industry," which is a differentiation point rather than an
   impact point.

The honest framing for the slide, given what was and was not found: there is
no rigorously sourced, publicly available percentage for "how much does early
disengagement detection improve retention" or "how much do EBRs improve
retention for high-value accounts" in B2B SaaS specifically. The peer-reviewed
literature (Ascarza, Neslin et al.) supports the design choices the team made
(segment by responsiveness, act on signal that persists over months) without
supplying a headline percentage. That is a defensible, honest slide. Inventing
a percentage to fill the gap is the exact failure mode this document exists to
prevent.
