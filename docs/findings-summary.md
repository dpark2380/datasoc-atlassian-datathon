# Findings summary

One page covering what we found in the data, what we built from it, and what
we recommend. Full detail and sources are in the linked docs.

## In short

- `customers.csv` and `product_usage.csv` are real. `customer_support_tickets.csv`
  is mostly random and can't support the sentiment analysis the brief asks for.
- Usage level scales cleanly with plan tier (Free to Enterprise) and with
  which product a customer uses, and it's stable month to month. That's the
  one real signal in this dataset, so it's what we built on.
- We flag a customer as at risk when their usage sits in the bottom quarter
  compared to peers on the same plan and product, then score and categorize
  them by how much it would cost Atlassian to lose that account.
- Each category gets a specific, sourced action, not a generic email.

## The data has two halves

We tested every ticket field against every other field in the dataset:
satisfaction rating, ticket type, priority, channel, resolution time, ticket
subject, customer age, customer gender, and ticket count. All of them come
back flat. A Critical ticket scores the same average satisfaction as a Low
one. A ticket's priority has no relationship to how long it actually took to
resolve. None of it connects to anything, including the real usage data.
There's also no customer-written text anywhere in the dataset to run
sentiment analysis on.

Usage data tells a different story. A customer's usage level is stable
month to month (correlation of 0.82 between January and May), and it scales
cleanly with what they pay for:

| Plan | Avg active days/month |
|------|----|
| Free | 5.3 |
| Standard | 8.2 |
| Premium | 10.1 |
| Enterprise | 11.5 |

Integrations used follows the same pattern even more sharply: 1.1 on Free
versus 6.0 on Enterprise, a 5x spread. Product also matters: Jira sees about
10.0 active days/month on average, Loom about 6.7.

Full detail: [`findings-data-quality.md`](findings-data-quality.md) and
[`findings-additional-signals.md`](findings-additional-signals.md).

## Why this matters for the brief

The brief asks us to use support ticket data to understand customer
experience and protect business value. The ticket data can't do that here,
and we're telling Atlassian this directly rather than presenting a
correlation that doesn't hold up. What we built instead uses the part of
the data that's real: how much a customer is actually using the product,
compared to their own peers.

## What we built: a risk model based on usage, not tickets

A customer is flagged at risk if their usage sits in the bottom quarter
compared to customers on the same plan and using the same product. Comparing
within the same plan and product matters: a Loom user on the Free plan
naturally shows fewer active days than a Jira user on Enterprise, and that
difference isn't a warning sign on its own.

Each at-risk customer also gets a risk score from 0 to 100, which climbs
when the account is more valuable (higher plan tier) or more embedded (more
integrations and collaborators), since those accounts cost more to lose.
On top of the score, each customer falls into one of four categories, based
on how long they've been a customer and how embedded they are:

| Category | Meaning | Count |
|----|----|----|
| Monitor Only | Not at risk | 6,248 |
| New & Struggling | At risk, recently joined relative to our customer base | 519 |
| Established & Low Engagement | At risk, longer-tenured, lower stakes | 893 |
| High-Value Disengaged | At risk, longer-tenured, high plan tier or heavily integrated | 660 |

## What we recommend for each category

Grounded in how real customer success teams operate (Gainsight, ChurnZero,
and Atlassian's own published practices), not generic advice.

For New & Struggling accounts, a named CSM runs a structured onboarding
session around one product-specific milestone, tracked against a 30/60/90-day
checklist. Examples include launching a Jira production project, a Confluence
team space, a Trello board with Butler automation, a Bitbucket pull request
with Pipelines, or a Loom async update embedded in Jira or Confluence.

For High-Value Disengaged accounts, a quarterly executive business review,
run jointly by the CSM and account leadership, uses product-relevant adoption
evidence: for example Jira issue throughput, Confluence contribution,
Bitbucket pull-request and Pipelines adoption, Trello collaboration and
automation, or Loom creation and viewer reach.

For Established & Low Engagement accounts, an automated sequence recommends
a product-specific workflow to reactivate, followed by an in-product nudge
and a short training offer if usage does not recover. No CSM time is needed
unless the automated play fails.

These are recommended workflow checks, not detected feature gaps. The
supplied file identifies a primary product and aggregate usage measures, but
does not contain feature-level event telemetry. Confirm the precise gap
before acting.

Full detail and sources: [`research-cs-playbook-actions.md`](research-cs-playbook-actions.md).

## One honest gap

Real customer health scores at Gainsight and ChurnZero combine usage with
support ticket sentiment and survey data like NPS. Ours only has usage,
because the ticket data here can't support a sentiment signal. We're
flagging this as a known limitation, not something we're papering over, and
part of our recommendation to Atlassian is what would need to be captured
differently so this gap can close in the future.
