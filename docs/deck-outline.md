# Deck outline

Challenge statement (given): "How can Atlassian better leverage raw support
ticket data to understand customer experiences and sentiment, and ultimately
protect business value?"

Story: support ticket data in this dataset turns out to carry no real
signal (see `findings-data-quality.md`), so the risk model is built on the
part of the data that is real: how much a customer actually uses Jira,
Confluence, Trello, Bitbucket, or Loom, compared to their own peers.
Framing: flag accounts at risk before they churn, not after.

## 1. Title and problem framing

State the challenge statement, then one line on why it matters: support
usage is a leading indicator of renewal and expansion risk, and Atlassian
can act on it months before a renewal conversation happens.

## 2. The data reality check

Own this early, since it's the credibility foundation for everything after
it. We tested every ticket field (satisfaction rating, type, priority,
channel, resolution time, ticket subject, customer age and gender) against
every other field in the dataset. All of it is flat. There's also no
customer-written text in this dataset to score sentiment from. We're
telling Atlassian this directly rather than presenting a correlation that
doesn't hold up. Source: `findings-data-quality.md` and
`findings-additional-signals.md`.

## 3. The headline finding

Usage is real, stable, and scales with what a customer pays for: Free
customers average 5.3 active days a month, Enterprise customers average
11.5. It also scales with which product they use, from about 6.7 active
days on Loom to about 10.0 on Jira. Show both cuts as the headline chart
pair.

## 4. The risk model

A customer is at risk when their usage sits in the bottom quarter compared
to peers on the same plan and the same product, so a Free/Loom customer
isn't unfairly flagged against an Enterprise/Jira baseline. Each at-risk
customer gets a risk score from 0 to 100 (higher for higher-value, more
embedded accounts) and one of four categories:

| Category | Count |
|----|----|
| Monitor Only | 6,248 |
| New & Struggling | 519 |
| Established & Low Engagement | 893 |
| High-Value Disengaged | 660 |

## 5. The recommendation

One specific, sourced action per category, not a generic email:

- New & Struggling gets a milestone-tracked onboarding review, reusing
  Atlassian's own published Jira Adoption Guide as session material.
- High-Value Disengaged gets a quarterly executive business review, logged
  through Jira Product Discovery, which Atlassian's own Customer Success
  team already uses for account prioritization.
- Established & Low Engagement gets an automated, feature-specific play (name
  the unused feature, email, in-app nudge, then a short training offer),
  costing no CSM time unless it fails to move usage.

Source and citations: `research-cs-playbook-actions.md`.

## 6. The tool

Live demo: pick a customer, see their risk score, their category, and the
recommended action in one screen. Built in Streamlit, not part of the
graded submission, but ready to show live if this reaches heats.

## 7. The honest gap, and the close

Real customer health scores (Gainsight, ChurnZero) combine usage with
support ticket sentiment and survey data. Ours only has usage, because the
ticket data here can't support a sentiment signal honestly. Close on what
Atlassian would need to capture (real timestamps, actual customer text,
tickets linked to account context) for that gap to close, which is itself
a concrete, actionable recommendation.

## Style rule for every slide

See `docs/agents/writing-style.md`. Say the specific, checkable thing. For
example, not "sentiment analysis reveals hidden customer pain points" but
"the ticket data in this dataset is statistically random, and here's what
we built instead."
