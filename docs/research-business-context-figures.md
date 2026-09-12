# Additional business-context figures, with sources

Research only. Nothing here has been added to the app. Compiled 13 September 2026
for the UNSW DataSoc x Atlassian Datathon deck.

Every figure below was read directly from the source named, not from a summary of
it. Where I could not reach a primary source I say so and recommend leaving the
claim out.

## How to read the source weight

Each finding is tagged with one of three weights.

*Filed* means Atlassian submitted it to the SEC. A 10-K is signed and audited in
part. A shareholder letter attached to a Form 8-K is filed but not audited, and
it is written by the company for investors. Both carry legal exposure if wrong.

*Published* means Atlassian put it on its own website, blog, or community forum.
No regulator sees it. It is still Atlassian speaking about Atlassian, which is
the point, but it can be stale and the methodology is usually absent.

*Third party* means someone else produced it. Weight depends entirely on whether
the method is visible.

The five argument links, numbered as in the deck outline:

1. Revenue is concentrated in a minority of accounts.
2. Support is low-touch by design, so tickets are a thin and late signal.
3. Usage telemetry therefore has to carry the load.
4. Integration depth predicts stickiness, which validates the embeddedness score.
5. So detect disengagement early and route to a tiered Customer Success play.

Primary source documents:

- FY26 Form 10-K, filed 14 August 2026:
  https://www.sec.gov/Archives/edgar/data/1650372/000165037226000036/team-20260630.htm
- Q4 FY26 shareholder letter, Exhibit 99.2 to Form 8-K filed 6 August 2026:
  https://www.sec.gov/Archives/edgar/data/1650372/000165037226000031/teamq42026shareholderlet.htm
- Q4 FY26 earnings press release, Exhibit 99.1 to the same 8-K:
  https://www.sec.gov/Archives/edgar/data/1650372/000165037226000031/ex991q4fy26.htm
- Q3 FY26 shareholder letter, Exhibit 99.2 to Form 8-K filed 30 April 2026:
  https://www.sec.gov/Archives/edgar/data/1650372/000165037226000024/teamq32026shareholderlet.htm

---

## Finding 1. Atlassian's Customer Success team weights monthly active usage at 40 percent and inverts it to find disengaged accounts

Weight: published, first-party, written by a named Atlassian employee.

Jaclyn Ruby, an Enterprise Customer Success Manager at Atlassian, published a
walkthrough of how her team prioritises its book of business. The weighted impact
score she describes is:

> Monthly Active Usage: 40%, Potential CSM Impact: 20%, Months Until Renewal: 20%,
> Customer Readiness: 20%

She then explains how the usage term is signed:

> Atlassian CSMs are focused on increasing adoption so I wanted customers with
> lower MAU to have a higher impact on the Impact Score. To do this, put a
> negative in front of the MAU number, which helps prioritize customers with low
> adoption

Source: "How Atlassian's Customer Success team uses Jira Product Discovery for
account prioritization", Atlassian Community, 12 June 2025.
https://community.atlassian.com/forums/Jira-Product-Discovery-articles/How-Atlassian-s-Customer-Success-team-uses-Jira-Product/ba-p/3033606

Supports links 3 and 5, and is the best single item found for link 5.

Why it matters here. This is Atlassian's own Customer Success function saying that
product usage is the heaviest input to deciding which account to work next, and
that low usage is the thing that should pull an account up the queue. That is the
model the team built, described by the customer it was built for. Two further
details are worth naming on the slide. First, no support ticket count and no
satisfaction score appears anywhere in her four fields, which corroborates the
decision to drop the ticket data on independent grounds rather than only because
this dataset's ticket columns turned out to be random. Second, the field
"Potential CSM Impact" is a second axis beside risk, which is exactly what the
retention literature in finding 12 says a targeting rule should have.

Risk to flag. This is one CSM describing her own team's setup, not a corporate
policy statement. Present it as "an Atlassian CSM's published prioritisation
method", not as "Atlassian's customer health score". Said the second way it would
be overclaiming and an Atlassian judge would correct it.

---

## Finding 2. Advantages compound with the number of applications a customer connects

Weight: filed.

From the Q4 FY26 shareholder letter, on the Teamwork Graph:

> It's baked into our platform and those advantages compound the more applications
> and contexts a customer connects.

Supports link 4. This is the sentence that most directly licenses the
embeddedness score.

Why it matters here. The team's embeddedness score is a function of Integrations
Used. The existing MCP quote establishes that integration adopters are stickier.
This one goes further and states the mechanism as monotonic in count of connected
applications, which is the shape of the score itself. It is one clause in a filed
document, and it does the most work per word of anything found.

---

## Finding 3. Rovo adopters produce more work in the product and grow ARR faster

Weight: filed.

From the Q4 FY26 shareholder letter:

> Customers that adopt Rovo are completing 20% more Jira work items and
> creating/editing 25% more Confluence pages versus non-adopters.

> Rovo adopters continue to grow their ARR more than 2x faster than non-adopters.

> Over 80% of Fortune 500 companies now use Rovo.

Supports links 3 and 4.

Why it matters here. Atlassian measures the value of an adoption event in units
of product activity, specifically work items completed and pages edited. Those
are the same class of variable as the dataset's usage columns. It is direct
evidence that Atlassian itself treats counts of things done in the product as the
readout for account health, which is the assumption the whole model rests on.

Risk to flag. These are correlations across a self-selected group. Customers who
adopt Rovo were probably already more engaged. Say "adopters and non-adopters
differ by 20 percent on work items completed", not "Rovo causes a 20 percent
lift". An Atlassian judge will know this and asking about it is the obvious
follow-up question.

---

## Finding 4. MCP users are not a separate population from ordinary product users

Weight: filed.

From the Q4 FY26 shareholder letter:

> 98% of MCP users are also active in Jira UI in the same month.

> Monthly active users (MAU) of our MCP Server and the Teamwork Graph CLI more
> than doubled during the quarter, to surpass 1 million MAUs, with overall MCP
> calls up more than 400% over the prior quarter.

Supports link 4.

Why it matters here. The 98 percent figure answers the obvious objection to using
integration count as an engagement proxy, which is that integration traffic might
be robots rather than people. Atlassian's own measurement says integration users
are almost all also humans in the UI in the same month. Integration depth and
human engagement move together rather than substituting for each other.

---

## Finding 5. Multi-product customers use more and deploy more than single-product customers

Weight: filed.

From the Q4 FY26 shareholder letter:

> Teamwork Collection customers continue to use >2x more AI credits per user and
> deploy 2x more active agents than standalone customers.

Supports link 4.

Why it matters here. This is the same stickiness-with-breadth claim as finding 2,
measured on a different axis and against a clean comparison group, which is
customers on a bundle against customers on a standalone product. It is a
reasonable second data point if one is needed, though it is weaker than finding 2
because bundle customers self-select.

---

## Finding 6. Gross margin rose partly because customer support got cheaper to run

Weight: filed.

From the Q4 FY26 shareholder letter, on the quarter:

> GAAP gross margin of 87% and non-GAAP gross margin of 89% increased by more than
> three ppts from the prior year, driven by continued optimization of our
> infrastructure and greater efficiency in our customer support operations.

The full-year picture in the FY26 10-K points the same way. Cost of revenues rose
$102.0 million, or 11 percent, against revenue growth of 26 percent. Inside that,
hosting fees paid to third parties rose $87.0 million and amortisation rose
$38.4 million, while employee compensation fell $56.2 million and fees paid for
consulting and other professional services fell $19.6 million. GAAP gross margin
for the year was 85 percent against 83 percent in FY25.

Supports link 2, and is the strongest quantitative item found for it.

Why it matters here. The existing R&D against marketing-and-sales comparison shows
where Atlassian chooses to spend. This shows the direction of travel inside the
support function itself. Customer numbers grew, and the people cost of serving
them fell. A support organisation being deliberately made cheaper per customer is
a support organisation producing thinner and later signal per customer. That is
the argument for not building the risk model on tickets, stated in Atlassian's
own reported numbers rather than as an opinion.

Note on which margin to quote. The quarter figure is 87 percent GAAP and the year
figure is 85 percent GAAP. Quote one, say which period it is, and do not mix them.

---

## Finding 7. Support scale is named as a risk, and the response is vendors and self-service

Weight: filed.

From the FY26 10-K risk factors:

> The number of our customers has grown significantly, and that has put additional
> pressure on our product support function. End customers may also reach out to us
> requesting support for third-party apps sold on the Atlassian Marketplace. To
> supplement our customer support teams, we have relied in the past, and will
> continue to rely on third-party vendors to fulfill requests to resolve common or
> frequently asked questions for Atlassian offerings. If we are unable to provide
> efficient product support globally at scale, including through the use of
> third-party vendors and self-service support, our ability to grow our business
> could be harmed.

Separately, the 10-K places support inside cost of revenues, describing that line
as including "consulting and contractors costs associated with our customer
support and infrastructure service teams".

Supports link 2.

Why it matters here. This is more specific than the "automated and low-touch"
quote the deck already has. It names outsourced vendors and self-service as the
mechanism, and it puts support in cost of goods sold rather than in a customer
success budget. A ticket in that system is generated by a customer who has already
failed to self-serve and has been routed to a contractor. It is a late event and a
sparse one, and it is not a channel anyone is using to monitor account health.

---

## Finding 8. Most users never convert, and the base is deliberately shaped that way

Weight: filed.

From the FY26 10-K:

> Our business model for low-touch customers is based in part on attracting a high
> volume of customers through free trials, limited free versions, and affordable
> starter licenses.

> Historically, a majority of users do not convert from free trials or limited free
> versions to paid apps or products, and our strategy also relies on these users
> influencing broader adoption within their organizations.

And on the sales model:

> ... we do not have to solely rely on a traditional, commissioned direct sales
> force until a customer reaches a specific size, thanks to the automation and
> efficiency built into our sales model.

Supports links 2 and 3.

Why it matters here. Below the enterprise threshold there is no assigned human
watching the account at all. Nobody is having a quarterly conversation with a
small Standard-plan customer, so there is no relationship channel through which
disengagement would surface. If the signal is not in the telemetry it does not
exist anywhere. This is the cleanest filed justification for building a detector
that runs on usage data with no human in the loop, and it also explains why the
model needs to work at the scale of tens of thousands of accounts rather than
hundreds.

---

## Finding 9. Atlassian says predicting retention is hard, and names adoption as a driver of it

Weight: filed.

The fuller version of the risk factor the deck already quotes one line of:

> Our customers have no obligation to renew their licenses or subscriptions, and
> our customers may not renew licenses or subscriptions with a similar contract
> duration or with the same or greater number of users. The majority of our
> customer base is on annual or monthly terms. Some of our customers have elected
> not to renew their agreements with us in the past, and it is difficult to
> accurately predict long-term customer retention. Our customer retention and
> expansion may decline or fluctuate as a result of a number of factors, including
> but not limited to our customers' satisfaction with our offerings, releases,
> support and pricing, customer awareness and adoption of the benefits and features
> of our offerings ... Additionally, we may be unable to timely address any
> retention issues with specific customers, which could harm our results of
> operations.

Supports links 3 and 5.

Why it matters here. Three things in this passage are worth more than the single
line currently on the page. Atlassian names adoption of features as a retention
driver, which is the variable the model measures. It says most of the base is on
annual or monthly terms, so the renewal window comes round often and the detection
has to be continuous rather than tied to an annual review. And it says in a signed
filing that predicting long-term retention is difficult, which is a better framing
for the team's model than claiming the problem is easy and nobody had noticed.

---

## Finding 10. The concentration is in a cohort, not in a handful of whales

Weight: filed.

From the FY26 10-K:

> No single customer contributed more than 5% of our total revenues during fiscal
> year 2026.

> Customers with greater than $10,000 in Cloud ARR represent the majority of our
> Cloud revenue.

And on how a customer is counted:

> We define the number of total customers at the end of any particular period as
> the number of organizations with unique domains with an active subscription for
> two or more seats.

> If we include single-user accounts and organizations that have only adopted our
> free or starter offerings, the active use of our offerings extends well beyond
> our total customer base.

Supports link 1.

Why it matters here. This is the defensive companion to the 85 percent figure the
page already carries. If a judge hears "over 85 percent of Cloud ARR sits in
57,334 accounts" and reaches for "so it is really a handful of giant customers and
a salesperson already knows all of them", the answer is that no single customer is
over 5 percent of revenue. The concentration is spread across tens of thousands of
accounts, which is precisely the range where a person cannot watch each one and a
model can. The customer definition is also worth having ready as the reason one
row in the dataset stands in for one organisation rather than one seat.

---

## Finding 11. The very large accounts are the fastest growing part of the base

Weight: filed.

From the Q4 FY26 shareholder letter:

> We had an all time record quarter in $1M+, $3M+, and $5M+ ACV deals.

> Our $3M+ ARR customers grew more than 50% y/y, and our $5M+ ARR customers grew
> more than 70% y/y.

The "Atlassian at-a-glance" page of the same letter states ">700 customers with
$1M+ in ARR". The equivalent page of the Q3 FY26 letter, four months earlier,
states ">600".

Supports link 1, and specifically the High-Value Disengaged category.

Why it matters here. The team's fourth category exists because a large account
going quiet is the most expensive kind of miss. This says the large-account tier
is both small and growing fast, so the number of accounts where that miss is
possible is rising. Roughly 700 accounts out of more than 350,000 is about 0.2
percent of the base.

Risk to flag. The ">700" number sits on a graphic whose footnote is rendered as an
image and did not survive text extraction, so I could not read its as-of date. Two
mitigations. First, the revenue-by-geography split on that same page reads
48 percent Americas, 41 percent EMEA and 11 percent Asia Pacific, and the FY26
10-K income statement gives $3,166,368k, $2,692,588k and $713,352k against total
revenue of $6,572,308k, which is 48.2, 41.0 and 10.9 percent. The page is
therefore carrying FY26 figures on that row at least. Second, prefer the $3M+ and
$5M+ growth rates from the letter body, which have no such ambiguity. If ">700" is
used, open the PDF page and read the footnote first.

---

## Finding 12. Targeting the highest-risk accounts is not automatically the right rule

Weight: third party, peer reviewed, method stated.

Eva Ascarza, "Retention Futility: Targeting High-Risk Customers Might Be
Ineffective", Journal of Marketing Research, volume 55, issue 1, February 2018,
pages 80 to 98. Two field experiments run with a telecommunications provider,
combined with machine learning to estimate heterogeneous treatment effects. Won
the 2018 Paul E. Green Award.
https://journals.sagepub.com/doi/10.1509/jmr.16.0163
Author's copy: https://www.hbs.edu/ris/download.aspx?name=ascarza_jmr_18.pdf

The finding is that customers at the highest risk of churning are not necessarily
the best targets for a proactive retention programme, and that firms should target
on estimated sensitivity to the intervention rather than on risk alone.

Related review: Ascarza, Neslin, Netzer, Anderson, Fader, Gupta and others, "In
Pursuit of Enhanced Customer Retention Management: Review, Key Issues, and Future
Directions", Customer Needs and Solutions, volume 5, 2018, pages 65 to 81.
https://doi.org/10.1007/s40547-017-0080-0
Its argument is that the field has over-invested in predicting churn relative to
deciding what to do about it.

Supports link 5, and is the best answer available to the hardest question a judge
can ask.

Why it matters here. Someone will ask why flagging the bottom quartile is the
right thing to do rather than just the easy thing. The honest answer, which is
also the strong one, is that risk ranking is half the problem and the published
experimental evidence says so. The team's response is that the four categories are
not a single risk ranking, they are a risk-by-responsiveness split, and each one
is mapped to a different play precisely because the same intervention does not suit
every at-risk account. Finding 1 shows Atlassian's own CSM reaching the same
conclusion independently, with "Potential CSM Impact" sitting beside usage in her
weighting.

Use this proactively rather than defensively. Raising the limitation yourself and
showing the design already accounts for it reads far better than being caught by it.

---

## Finding 13. Better churn models are worth real money, and they do not go stale quickly

Weight: third party, peer reviewed, method stated.

Neslin, Gupta, Kamakura, Lu and Mason, "Defection Detection: Measuring and
Understanding the Predictive Accuracy of Customer Churn Models", Journal of
Marketing Research, volume 43, issue 2, May 2006, pages 204 to 211.
https://journals.sagepub.com/doi/abs/10.1509/jmkr.43.2.204

Method is a modelling tournament. Academics and practitioners downloaded a common
telecom dataset, built models and submitted predictions scored on two held-out
validation databases. Two results are relevant. The spread in predictive accuracy
across submissions was large enough to change the profitability of a churn
management campaign by hundreds of thousands of dollars. And models lost very
little accuracy when applied to a database compiled three months after the
calibration data.

Supports link 5 and the early-intervention claim.

Why it matters here. The second result is the one to use. It is published evidence
that a churn signal computed from data some months old still carries, which is the
premise of acting on disengagement well before a renewal date rather than at it.
The first result gives a defensible reason to care about model quality at all,
without needing a fabricated dollar figure of the team's own.

Risk to flag. The setting is consumer telecom in the mid 2000s. Transfer to B2B
SaaS is an argument, not a measurement. Say that out loud if the figure is used.

---

## Claims checked and recommended against

### The Reichheld retention statistics

The claim that a 5 percent improvement in retention raises profit by 25 to 95
percent does not appear in that form in the original publication, and I recommend
leaving it out entirely.

The original is Frederick F. Reichheld and W. Earl Sasser Jr., "Zero Defections:
Quality Comes to Services", Harvard Business Review, September to October 1990,
pages 105 to 111. https://hbr.org/1990/09/zero-defections-quality-comes-to-services

What the article actually reports is that reducing the defection rate by 5 percent
generated 85 percent more profit in one bank's branch system, 50 percent more in an
insurance brokerage and 30 percent more in an auto-service business. Bain's own
page reproducing the article summarises it differently again, as "companies can
boost profits by almost 100% by retaining just 5% more of their customers".
https://www.bain.com/insights/zero-defections-quality-comes-to-services-harvard-business-review-hbr/

Three problems. The widely quoted 25 to 95 percent range is a later paraphrase,
usually attributed to Reichheld's 1996 book "The Loyalty Effect", and I could not
verify it against the book text. Two renderings of the same 1990 article disagree
with each other, which is on its own a reason not to put it on a slide. And the
settings studied are consumer retail banking, insurance broking, auto servicing and
credit cards, where a customer defects individually and silently. Atlassian sells
annual and monthly contracted subscriptions to organisations. Nothing in the 1990
study speaks to that.

There is also direct published pushback. Werner Reinartz and V. Kumar, "The
Mismanagement of Customer Loyalty", Harvard Business Review, July 2002, analysed
the transaction records of roughly 16,000 customers across company databases
including a large US mail-order firm, a French food retailer and a German direct
brokerage, and found no support for the claims that loyal customers cost less to
serve, pay more, or market the firm by word of mouth.
https://hbr.org/2002/07/the-mismanagement-of-customer-loyalty

Recommendation: do not cite Reichheld. If someone in the audience raises it, the
above is a good answer and makes the team look like it did the reading.

### "It costs five times more to acquire a customer than to retain one"

Recommend against. I could not find a primary study behind it, and a named source
says there is not one. Timothy Keiningham, Terry Vavra, Lerzan Aksoy and Henri
Wallard set it out as Myth 8 in their book "Loyalty Myths", excerpted by Ipsos
Loyalty in 2005: "Although it is difficult to determine the exact origins of this
platitude, the earliest sources that we can find attribute it to research conducted
by the Technical Assistance Research Project (TARP) in Washington, D.C. in the late
1980s." They note the underlying TARP research is not available, that the claim
spread through secondary citation, and that it conflates average with marginal
cost.
https://www.ipsos.com/sites/default/files/publication/2003-08/Ipsos_Loyalty_Myth_8_Excerpt.pdf

### The "76 percent of Jira customers shipped projects faster after adding Confluence" statistic

Recommend against. It is real and it is first-party, from "Two great products, now
even better together: Jira and Confluence", Atlassian blog, 6 June 2018.
https://www.atlassian.com/blog/software-teams/two-great-products-now-even-better-together-jira-confluence
But the post is eight years old, predates Cloud becoming the primary offering, and
discloses no sample size or survey method. An Atlassian employee judging the event
would place it immediately as old marketing copy. The multi-product argument is
better made with findings 2 and 5, which are current and filed.

### The Forrester Total Economic Impact studies

Recommend against, or appendix only with the method spelled out. These are
commissioned by Atlassian, and the Atlassian Cloud study is built from interviews
with four customers aggregated into a hypothetical composite organisation.
https://www.atlassian.com/enterprise/forrester-cee-total-economic-impact
The ROI headline is a modelled output of a vendor-funded exercise with a sample of
four. Presenting it next to audited filings would drag down the credibility of the
filed numbers.

### Churn statistics circulating on vendor blogs

Recommend against. Searching for rigorous work on usage-based churn prediction in
B2B SaaS surfaces a dense layer of content-marketing pages carrying figures such as
"a 40 percent drop in weekly logins predicts churn with 78 percent accuracy" and
"accounts with feature adoption below 30 percent show 80 percent first-year churn".
None of these carry a linked study, a sample size, or a named dataset. They should
be treated as fabricated until proven otherwise. This is worth one line in the
appendix: the team looked for published benchmarks on usage-based churn detection
in B2B SaaS and found none with a visible method, which is part of why the model is
validated on this dataset rather than against an external number.

### Net revenue retention, revisited and confirmed

The earlier conclusion holds and can be stated more strongly than "not disclosed".
Atlassian defines net revenue retention in the glossary of its shareholder letters,
including the Q3 and Q4 FY26 letters: "We calculate net revenue retention rate
(NRR) at a point in time by dividing monthly recurring revenue (MRR) at the end of
a reporting period (Current Period MRR) by the MRR for the same group of customers
at the end of the prior 12-month period." No value accompanies the definition in
either letter, and the term does not appear in the FY26 10-K at all. So Atlassian
maintains the metric and has chosen not to publish it. Any NRR number attributed to
Atlassian came from somewhere else.

### The "at-a-glance" market opportunity and user-diversity figures

Do not use. The Q4 FY26 at-a-glance page shows a $140B market opportunity growing
at 14 percent CAGR. The Q3 FY26 version of the same page, four months earlier,
shows $67B growing at 13 percent annually. The definition changed between quarters.
The Q3 page also carries a footnote stating that "customer data is as of December
31, 2025, financial data reflected is as of or for the fiscal year ending June 30,
2025, and market opportunity data is as of or for the fiscal year ending June 30,
2024", and that the user diversity breakdown rests on a sample of Jira and
Confluence Cloud users as of 31 March 2024. Those slides mix vintages by design.
An Atlassian judge would know it.

### Per-collection customer counts

The Q4 FY26 at-a-glance page does carry customer counts by collection, which is the
closest thing to a customer-count-by-product disclosure that exists. The figures
visible in the extracted text are 150K, more than 100K and more than 65K, but the
page is a graphic and the text extraction does not reliably tie each count to its
collection. Do not use any of these until someone opens the PDF and reads the
mapping off the page.

---

## Ranked shortlist

### Put on the Business Context page

1. Finding 1, the Atlassian CSM's 40 percent usage weight with the sign inverted.
   It is the closest thing to Atlassian validating the team's design, it is
   first-party and attributable, and it lands the whole argument in one slide.
2. Finding 2, advantages compound with the number of connected applications. One
   filed clause that justifies the embeddedness score directly.
3. Finding 6, gross margin up partly on greater efficiency in customer support
   operations. Converts the low-touch claim from a quoted intention into a
   reported financial outcome, and does the work the R&D against sales comparison
   is currently doing alone.
4. Finding 10, no single customer over 5 percent of revenue. Short, filed, and it
   closes the most likely hole in the concentration argument.
5. Finding 3, Rovo adopters completing 20 percent more Jira work items. Use it to
   show Atlassian measuring account value in units of product activity, with the
   correlation caveat stated on the slide.

### Keep in the deck if there is room

6. Finding 11, $3M+ ARR customers up more than 50 percent and $5M+ up more than
   70 percent. Good support for the High-Value Disengaged category.
7. Finding 8, most users never convert and there is no assigned salesperson below
   a size threshold. The clearest reason the detector has to be automatic.

### Appendix and Q&A backup only

8. Finding 12, Ascarza on targeting. Prepare this one properly. It is the best
   answer to the hardest question and it is better raised by the team than by a
   judge.
9. Finding 9, the full retention risk factor. Useful when someone asks whether
   Atlassian actually considers this a problem.
10. Finding 7, support scale risk and reliance on vendors and self-service.
11. Finding 4, 98 percent of MCP users also active in the Jira UI. Holds in
    reserve for an objection about integration traffic not being human activity.
12. Finding 13, Neslin and colleagues on churn model accuracy holding up three
    months out. Supports the early-intervention timing claim if challenged.
13. Finding 5, Teamwork Collection customers using more than twice the AI credits.
14. The rejected claims above, especially the Reichheld trace and the five-times
    acquisition myth. Being able to say why a famous number was left out is worth
    more in a Q&A than the number would have been on a slide.
