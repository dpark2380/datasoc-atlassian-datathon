# Deck outline (structure only — fill in once tomorrow's prompt/rubric lands)

Challenge statement (given): "How can Atlassian better leverage raw support
ticket data to understand customer experiences and sentiment, and ultimately
protect business value?"

1. **Title / problem framing** — the challenge statement, one line on why it matters (support tickets = leading indicator of churn/expansion risk).
2. **Approach** — data → structured cuts + sentiment layer → risk scoring → recommendations. One slide, not a methodology essay.
3. **Data reality check** (own this, don't hide it) — what the data can and can't tell us. If CSAT turns out uncorrelated with anything (as in the placeholder dataset), that's a finding, not a failure: "Atlassian can't triage what it doesn't correlate."
4. **Findings — operational** — volume/resolution-time patterns by ticket type, priority, channel, product. Where is time/effort actually going.
5. **Findings — sentiment/experience** — what the text signal adds beyond the structured fields (caveated: directional, not validated ground truth in the placeholder data).
6. **The at-risk lens** — the risk-scorer tool (workstream C) as the "so what": here's a ticket, here's why it's flagged, here's the suggested action.
7. **Business impact** — translate #4-6 into $ / retention / effort terms. This is the slide judges actually remember — needs real rubric-informed framing tomorrow.
8. **Recommendations** — 2-3 concrete, checkable actions (not "leverage AI to unlock insights" — see references/vibe-coded-tells.docx, say the specific thing).
9. **Demo** — live walkthrough of the risk-scorer tool + dashboard.

## Style rule for every slide
See `docs/agents/writing-style.md`. Say the specific, checkable thing. E.g.
not "sentiment analysis reveals hidden customer pain points" but "14% of
Critical tickets carry negative sentiment and take 2x longer to close."
