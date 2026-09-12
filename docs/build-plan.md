# What we're building, step by step, and why

This is the working plan behind the pitch: what each piece is, why it
exists, and how it fits together. `findings-summary.md` is the one-page
version of the results; this document is the reasoning that got us there.

## 1. Why this isn't a straightforward sentiment analysis

The challenge asks us to use support ticket data to understand customer
sentiment and protect business value. Our first attempt was exactly that:
score ticket text for sentiment, link it to a satisfaction outcome,
segment by ticket priority and channel.

We tested that approach before building on it and it failed every check.
`Customer Satisfaction Rating` is statistically random. Ticket Type,
Priority, Channel, and Ticket Subject are all near-uniform, independently
assigned per ticket. There's no free-text field in this dataset to score
sentiment from at all. Full detail: `findings-data-quality.md` and
`findings-additional-signals.md`.

We built the pitch around this finding instead of hiding it, for two
reasons. First, it's true, and presenting a correlation we know doesn't
hold up would be worse than admitting the data can't support it. Second,
it's a real, checkable insight in its own right: if Atlassian wants
ticket-level sentiment analysis to work, this tells them exactly what
needs to change in how tickets are captured.

## 2. Why usage data became the foundation instead

`product_usage.csv` and `customers.csv` are the parts of the dataset that
hold up under the same tests. A customer's usage level persists month to
month (0.82 correlation between January and May), and it scales cleanly
with plan tier (Free averages 5.3 active days a month, Enterprise 11.5)
and with which product they use (Loom around 6.7, Jira around 10.0).

That gave us a real outcome to build on: how much a customer is actually
using the product, compared to real peers, instead of a ticket-based
signal that doesn't exist.

## 3. Why "at risk" is a peer-group comparison, not a fixed threshold

A Free-plan customer naturally uses the product less than an Enterprise
customer, and a Loom user naturally logs fewer active days than a Jira
user. A single company-wide usage threshold would just re-flag "is on the
Free plan" or "uses Loom," not real disengagement.

So a customer is flagged at risk only when their usage sits in the bottom
quarter compared to customers on the same plan and the same product. This
is the one point in the pipeline where getting the comparison group wrong
would quietly break everything downstream, so it's worth stating plainly:
peer group = Plan Type x Primary Product.

## 4. Why the risk score adds tenure and embeddedness, not just usage

Two customers can both be "at risk" and mean very different things. We
add three refinements, each answering a specific question:

Relative tenure answers whether this looks like an onboarding problem or
a churn problem. Since every customer in this dataset is already 1.5 to
4.5 years old by the time the usage window starts, there's no real "new
customer" cohort to compare against an absolute cutoff, so tenure is
measured as a quartile relative to the rest of the customer base, not a
claim about real-world onboarding dates.

Embeddedness (Collaborators and Integrations Used, weighted toward
Integrations Used because it shows a sharper tier signal: about a 5x
spread from Free to Enterprise versus about 2x for Active Days) answers
how much it would cost to lose this account. It's kept separate from the
usage composite deliberately: folding it into the same score would let a
well-integrated account's high collaborator count cancel out a real usage
decline, which is the opposite of what we want.

Plan tier answers the same question at the account level: a disengaging
Enterprise account is worth protecting harder than a disengaging Free
account.

## 5. Why there are four named categories, not a raw score

A 0-100 risk score alone doesn't tell a Customer Success team what to do.
Four categories translate the score, tenure, and embeddedness into a
decision:

Monitor Only means not at risk, no action needed. New & Struggling means
at risk and newer relative to the customer base, which reads as an
onboarding problem. Established & Declining means at risk, longer-tenured,
and lower value or lower embeddedness, a real but lower-stakes churn risk.
High-Value Disengaged means at risk, longer-tenured, and either high plan
tier or heavily integrated, the account most worth protecting.

## 6. Why each category has a specific, sourced action

The first draft of the recommendation was generic: send an email, schedule
a check-in. That's not defensible as a "solution," which is 35% of the
judging criteria, the single largest share.

We researched what real customer success teams and health-scoring
platforms (Gainsight, ChurnZero, HubSpot) actually do for each situation,
and what Atlassian itself already publishes and practices, and matched an
action to each category:

New & Struggling gets a milestone-tracked onboarding review, using
Atlassian's own published Jira Adoption Guide as the session material.
High-Value Disengaged gets a quarterly executive business review, logged
through Jira Product Discovery, a tool Atlassian's own Customer Success
team already uses for account prioritization. Established & Declining
gets an automated, feature-specific play (name the unused feature, email,
in-app nudge, then a training offer), costing no CSM time unless it fails.

Full sources: `research-cs-playbook-actions.md`.

## 7. Why there's a small interactive tool, not a full application

The brief is explicit that a working build isn't required; the submission
is a deck or PDF, and the judging criteria reward a clear recommendation
tied to the analysis, not software. A live tool only matters if we're
selected for heats and choose to demo it, so the deck has to stand on its
own regardless of how the tool turns out.

Given that, the tool is intentionally small: a single-customer lookup that
shows one customer's risk score, category, and recommended action on one
screen. It exists to make the recommendation feel concrete and already
built in an 8-minute pitch, not to be a product.

## 8. What's built right now

`analysis/eda.py` runs the full pipeline: loads the three source files,
computes the engagement composite, the peer-group comparison, the risk
score, the tenure and embeddedness modifiers, and the four categories, and
writes `analysis/customer_risk.csv` and `analysis/cleaned_tickets.csv`.

`streamlit_app.py` runs the combined app (`app_pages/dashboard.py` for
exploration, `app_pages/risk_scorer.py` for the live-demo single-customer
lookup). The dashboard exports charts for the deck and is never demoed live;
the risk scorer is built to be presentable.

`docs/findings-data-quality.md`, `docs/findings-additional-signals.md`,
`docs/research-cs-playbook-actions.md`, and `docs/findings-summary.md` are
the audit trail and sources behind every claim above.

## What's not built yet

The actual slide deck. The business-impact framing that ties the category counts to what's at stake
for Atlassian.
