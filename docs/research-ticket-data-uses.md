# What the ticket file can still legitimately do

Research note, 13 September 2026. No code was changed to produce this. Every
number below was recomputed from `references/Dataset/` during the research and
is reproducible with the commands noted in each section.

The question this answers: we proved the ticket file is random, so what work
can it still do in the submission without overclaiming? Eight ideas are
assessed. Two are worth building, three are worth one slide each, three should
be dropped.

---

## 1. The ticket file as a negative control for our own method

### What it is

Run the risk pipeline on features derived from the ticket file, show it
produces nothing, and claim that the pipeline does not manufacture signal from
noise.

### The name for it

Not a negative control in the causal-inference sense. Lipsitch, Tchetgen
Tchetgen and Cohen define a negative control outcome as one that shares the
unobserved confounders U of the real exposure-outcome pair but cannot be
caused by the exposure, a property they call U-comparability: "a negative
control outcome (N) should be an outcome such that the set of common causes of
exposure A and outcome Y should be as identical as possible to the set of
common causes of A and N"
([Epidemiology 2010;21(3):383-388](https://pubmed.ncbi.nlm.nih.gov/20335814/),
[full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3053408/)). A field drawn
from a random number generator has no common causes with anything, so it fails
U-comparability by construction. If a judge who knows this literature hears
"negative control" they will ask what the shared confounding structure is, and
there is no answer.

The correct name is a placebo input, or a negative control in the laboratory
sense of a specimen known to contain none of the analyte. The two citable
analogues are:

Bertrand, Duflo and Mullainathan randomly generated placebo laws in CPS state
wage data, ran their estimator on data where the true effect was zero by
construction, and reported how often it fired: "we find an 'effect'
significant at the 5 percent level for up to 45 percent of the placebo
interventions"
([QJE 2004;119(1):249-275](https://academic.oup.com/qje/article-abstract/119/1/249/1876068),
[NBER w8841 PDF](https://www.nber.org/system/files/working_papers/w8841/w8841.pdf)).
This is exactly the move: known-null input, count the false positives.

Adebayo and co-authors formalise the same idea for ML methods as the data
randomization test, in which training labels are shuffled and a method that
returns an unchanged output is shown to be independent of the data-generating
process ([NeurIPS 2018, arXiv:1810.03292](https://arxiv.org/abs/1810.03292)).

Ojala and Garriga give the permutation framing we already use on the usage
trend, and also the sentence that limits it: when the data contain no real
dependency "all classifiers tend to have a high p-value. However, as a nature
of statistical tests, about alpha of the results will be incorrectly regarded
as significant"
([JMLR 2010;11:1833-1863](https://www.jmlr.org/papers/v11/ojala10a.html)).

### The problem specific to our pipeline

`analysis/eda.py` scores risk with `percentile_within_group`, a rank within
plan and product, and flags the bottom quartile. A ranking always returns a
quartile. Feed it noise and it flags 25 percent of customers with complete
confidence. So the naive version of this idea does not produce the clean null
it promises, and a judge who reads the code will see that in ten seconds.

The repair is to state the null at the level of a claim that can actually
fail. Two candidates, both cheap:

Agreement. If the ticket-derived flag and the usage-derived flag are
independent, the expected overlap is 0.25 x 0.25 = 6.25 percent of customers,
a Jaccard index of 0.143. Predict the number in advance and report what came
back.

Separation. The usage flag separates customers on quantities it was not built
from, such as plan tier composition and the reliability-weighted embeddedness
composite. Ask the same of the ticket flag and show it separates nothing.

### What it licenses

A specificity statement about one run: on an input where the answer is known
to be nothing, our procedure reported nothing beyond what its own construction
forces. Paired with the existing permutation test on usage slopes, it is a
reasonable answer to "how do you know you did not fit noise?".

### What it does not license

It says nothing about power. A null result is not evidence of no effect:
"usually all that has been shown is an absence of evidence of a difference"
(Altman and Bland, [BMJ 1995;311:485](https://pmc.ncbi.nlm.nih.gov/articles/PMC2550545/)).

One run on one dataset is one draw, not a false-positive rate. Bertrand,
Duflo and Mullainathan ran hundreds of placebo laws to get 45 percent. If
anyone asks "what is your type I error rate", the honest answer is that we did
not estimate one.

It does not validate the model, only the absence of one failure mode. A
pipeline can pass a placebo test and still be wrong about real customers.

It does not make the ticket data useful. The negative control is a use of the
file's randomness, not of its content.

### Effort

Two to three hours. Build four per-customer ticket features (ticket count,
mean CSAT where present, priority as an ordinal, the first-response to
resolution gap), push them through `percentile_within_group` with the same
peer groups, and report overlap against the usage flag with the 6.25 percent
prediction stated first. Reuses `analysis/reliability_checks.py` structure.

One constraint to design around: 8,181 of 8,320 customers have exactly one
ticket and only 2,769 have a CSAT rating at all, so any ticket-derived feature
either covers a third of the customer base or is a constant. That fact is
itself worth a line on the slide.

---

## 2. The gap against Atlassian's own Service Management data model

This is the strongest idea in this document. The closing recommendation stops
being an outsider's wishlist and becomes a list of fields Atlassian's own
product already writes.

### What a real Jira Service Management request carries

All field names below are from the official Cloud REST API definitions
(`https://developer.atlassian.com/cloud/jira/service-desk/swagger.v3.json`,
rendered at
[the JSM Cloud REST API reference](https://developer.atlassian.com/cloud/jira/service-desk/rest/intro/))
and from the published Atlassian Analytics warehouse schema
([Schema for Jira Service Management](https://support.atlassian.com/analytics/docs/schema-for-jira-service-management/)).

| Concept | Where it lives | Exact fields |
|---|---|---|
| The request object | `GET /rest/servicedeskapi/request/{issueIdOrKey}` | `CustomerRequestDTO`: `issueId`, `issueKey`, `summary`, `requestTypeId`, `serviceDeskId`, `createdDate`, `reporter`, `requestFieldValues`, `currentStatus`, plus expands for `sla`, `status`, `comment`, `attachment`, `participant`, `action` |
| SLA | `GET /rest/servicedeskapi/request/{issueIdOrKey}/sla` | `SlaInformationDTO`: `id`, `name`, `ongoingCycle`, `completedCycles`. Each cycle carries `startTime`, `stopTime`, `breachTime`, `breached`, `paused`, `withinCalendarHours`, `goalDuration`, `elapsedTime`, `remainingTime`, each duration as `{millis, friendly}` |
| CSAT | `GET`/`POST`/`DELETE /rest/servicedeskapi/request/{requestIdOrKey}/feedback` | `CSATFeedbackFullDTO`: `type` ("csat"), `rating` ("an integer value between 1 and 5"), `comment` ("the comment provided with this feedback") |
| CSAT in the warehouse | `jsm_issue` table | `satisfaction_rating`, `satisfaction_submitted_at` |
| Status and its history | `GET /rest/servicedeskapi/request/{issueIdOrKey}/status`, and `GET /rest/api/3/issue/{issueIdOrKey}/changelog` | `CustomerRequestStatusDTO`: `status`, `statusCategory`, `statusDate`. `ChangeDetails`: `field`, `fieldId`, `fieldtype`, `from`, `fromString`, `to`, `toString`, with `Changelog.author` and `Changelog.created` |
| Customer text | `GET /rest/servicedeskapi/request/{issueIdOrKey}/comment` | `CommentDTO`: `body`, `renderedBody`, `author`, `created`, `public` (true for customer-visible, false for internal) |
| Request types | `GET /rest/servicedeskapi/servicedesk/{serviceDeskId}/requesttype` and `/requesttype/{id}/field` | `RequestTypeDTO`: `id`, `name`, `description`, `issueTypeId`, `groupIds`, `practice`. `RequestTypeFieldDTO`: `fieldId`, `name`, `required`, `jiraSchema`, `validValues`, `defaultValues` |
| Organizations | `GET /rest/servicedeskapi/organization`, `/organization/{id}/user`, `/servicedesk/{id}/organization` | `OrganizationDTO`: `id`, `uuid`, `name`, `created`, `scimManaged`. Warehouse: `jsm_organization` and `jsm_issue_organization_mapping` (`issue_id`, `organization_id`) |
| Approvals | `GET /rest/servicedeskapi/request/{issueIdOrKey}/approval` | `ApprovalDTO`: `id`, `name`, `approvers`, `createdDate`, `completedDate`, `finalDecision` |
| Work logged | `GET /rest/api/3/issue/{issueIdOrKey}/worklog` | `Worklog`: `timeSpent`, `timeSpentSeconds`, `started`, `created`, `author`, `comment`. Issue-level `TimeTrackingDetails`: `originalEstimateSeconds`, `remainingEstimateSeconds`, `timeSpentSeconds` |
| Links and hierarchy | `GET /rest/api/3/issueLink/{linkId}`, `GET /rest/api/3/issue/{issueIdOrKey}/remotelink` | `IssueLink`: `id`, `type`, `inwardIssue`, `outwardIssue` |
| Service and incident context | Warehouse tables `jsm_affected_service_mapping`, `service`, `jsm_incident` | `service_id`, `tier`, `type`; `is_major_incident`, `severity`, `urgency`, `impact`, `source` |
| Channel | `request-channel-type` issue property | Values are fixed by Atlassian: "jira", "portal", "anonymousportal", "email", "API", "deployment" ([KB article](https://support.atlassian.com/jira/kb/using-the-request-channel-type-property-on-filters/), [What are request channels?](https://support.atlassian.com/jira-service-management-cloud/docs/what-are-request-channels/)) |
| Routing | `GET /rest/servicedeskapi/servicedesk/{serviceDeskId}/queue/{queueId}/issue` | Queues per service desk |

### The count

The dataset has 16 columns. Three of them (`Customer Age`, `Customer Gender`,
`Date of Purchase`) are requester demographics that the JSM request object does
not model at all, and two of those would be a privacy question if they were
real. Of the 13 support-relevant columns, 11 correspond to something JSM
models, but every one of them is a flattened version of a richer object:

- `First Response Time` and `Time to Resolution` are two bare timestamps where
  JSM writes two SLA cycles with a goal, an elapsed duration, a breach flag, a
  pause flag and a working-hours flag.
- `Customer Satisfaction Rating` is a bare 1 to 5 integer where JSM writes a
  rating plus the optional free-text comment plus a submission time. The rating
  half is exactly what we were given and the comment half is exactly the field
  the challenge question needs.
- `Ticket Status` is a single current value where JSM keeps the full transition
  history in the changelog.
- `Customer Email` identifies a person where JSM maps a request to an
  organization through `jsm_issue_organization_mapping`.
- `Ticket Channel` uses the values Email, Phone, Social media and Chat. Only
  Email is a JSM channel value. Phone and Social media are not in the fixed
  vocabulary at all, and chat-created requests are recorded as "API".
- `Ticket Type` uses Refund request, Cancellation request, Billing inquiry,
  Product inquiry and Technical issue, which is a retail vocabulary rather than
  a JSM request type drawn from a configured `RequestTypeDTO` with a
  `practice` and a field schema.

Objects JSM models that have no column in the file at all: CSAT free-text
comment, comment threads with the public and internal flag, SLA goals and
breach state, status transition history, organization mapping, request type
field schema, work logs and time tracking, approvals, issue links, affected
service, incident severity and major-incident flag, participants, attachments,
queue.

### What it licenses

A closing slide of the form: this extract carries 11 of the concepts your own
Service Management product models, each one flattened, and omits at least 12
more that your API already returns. Every field we would need to answer the
challenge question is already in `CSATFeedbackFullDTO.comment`,
`CommentDTO.body`, `SlaInformationOngoingCycleDTO` and
`jsm_issue_organization_mapping`. It also licenses a concrete statement about
what we would build with a real export, endpoint by endpoint.

### What it does not license

It does not tell us how Atlassian actually provisions or exports support data
internally, only what the public Cloud API and the published Analytics schema
contain. Say "your public API models this", not "your systems contain this".

It does not tell us the dataset was derived from JSM. The channel and ticket
type vocabularies say it was not.

It does not license any claim about Data Center or Server deployments, or
about Customer Service Management, which has its own docs.

Do not claim the counts to more precision than the table supports. The honest
phrasing is "11 of 13 support-relevant columns map to a JSM concept, all
flattened" with the table on the appendix slide so the count can be checked.

### Effort

Two hours of slide and appendix work. No code. The table above is the artifact.

---

## 3. How the file was actually assembled

### What it is

A forensic account that replaces "it is random" with a specific, checkable
statement about how the three files were generated and in what order. This is
the answer to "so you ignored the data we gave you?", because it demonstrates
the opposite: we characterised it precisely enough to reconstruct its
provenance.

### The evidence

Recomputed today from `references/Dataset/`:

8,469 tickets carry 8,320 distinct customer emails, and `customers.csv` has
exactly 8,320 rows. Every ticket email matches a customer row, and no customer
has zero tickets. If 8,469 tickets had been assigned to 8,320 customers at
random, the count per customer would be approximately Poisson with mean 1.018
and about 3,006 customers would have no ticket at all. Observing zero such
customers is not a near miss, it is impossible under random assignment. The
customer table was built by deduplicating the ticket file, not sampled
alongside it.

The per-customer ticket counts are 1 for 8,181 customers, 2 for 131, 3 for 6
and 4 for 2.

`product_usage.csv` holds exactly 5 monthly rows (2023-01 to 2023-05) per
customer per product, and the number of distinct products a customer has in
usage matches the number of distinct products in that customer's tickets:
8,202 customers with one product, 114 with two, 4 with three. The 139
customers with more than one ticket account for the difference, and the 21
whose repeat tickets name the same product have one product in usage. The
usage panel was generated from the ticket products.

Of the 2,769 closed tickets, 1,365 have a resolution timestamp earlier than
the first response timestamp. That is 49.3 percent, and a binomial test
against a fair coin gives p = 0.47. The two timestamps were drawn
independently.

The 2,769 satisfaction ratings are distributed 553, 549, 580, 543, 544 across
ratings 1 to 5. A chi-square goodness of fit against uniform gives
chi-square = 1.67 on 4 degrees of freedom, p = 0.80.

### What it licenses

A precise provenance claim: the ticket file is the root of this dataset, the
customer table is its deduplicated identity projection, and the usage panel was
generated per customer and ticket product. Every behavioural column in the
ticket file was drawn independently of every other column.

It also licenses a much better line than "it was random", which is that we can
state the generating procedure and reproduce its signatures.

### What it does not license

It does not identify who generated the file or from what source. A public
dataset with the same shape and column list circulates on Kaggle, but the
description page did not load for verification, so the claim "this is the
Kaggle customer support ticket dataset" is unverified and should not be made
on a slide.

It does not make the usage data suspect. Usage being generated per ticket
product says nothing about whether the usage values themselves carry
structure, and the reliability work in `docs/findings-reliability.md` tested
that separately.

### Effort

One hour. The numbers are computed above. It needs a short script in
`analysis/` if the team wants it reproducible on stage, or a slide with the
five figures and the command to regenerate them.

---

## 4. The Product Purchased match, reinterpreted

### What it is

The 100 percent agreement between a ticket's `Product Purchased` and the
customer's rows in `product_usage.csv` currently reads as a validity finding.

### What the evidence actually shows

The agreement is a consequence of the generation order established in section
3, not independent corroboration. Usage rows exist for a customer and product
pair precisely when that customer has a ticket naming that product. The match
rate could not have been anything other than 100 percent.

### What it licenses

One narrow and still useful claim: the identity and linkage columns of the
ticket file are internally consistent, so the customer-to-product join used
downstream is sound. Paired with the 100 percent email join and with the fact
that a satisfaction rating, a resolution text and both timestamps are present
for all 2,769 Closed tickets and for no Open or Pending ticket, the shape of
the statement is that the file's keys and conditional structure hold while its
measures do not. The CSAT-on-close pattern is exactly the behaviour JSM has,
where the survey goes out when a request reaches a Done status category, which
makes it a nice bridge into section 2.

### What it does not license

It is not evidence that the product field is correct in any external sense.
It is not evidence that the file describes real customers. Presenting the 100
percent match as validation would be the one claim in the deck that a careful
judge could show is circular, so the current framing needs to change before
Monday whatever else is done.

### Effort

Fifteen minutes. It is a rewording of an existing slide line.

---

## 5. The ticket file as a schema harness

### What it is

Use the file as a shape-compatible stand-in that proves the pipeline would
consume a real support export, without claiming its values mean anything. The
tool reads it, joins it, derives features from it and produces output, so the
interface is demonstrated even though the content is noise.

### What it licenses

A statement that the work is not blocked on the data problem: point the same
code at a JSM extract carrying the fields in section 2 and it runs. That is
the difference between a team that stopped and a team that built the thing that
is waiting for real input.

### What it does not license

Nothing quantitative. No accuracy, no lift, no validation. It is a claim about
software, not about customers, and it should be phrased as one sentence rather
than a section, because a demo that consumes noise proves only that it parses
noise.

### Effort

Zero to one hour, since the existing pipeline already loads and joins the
ticket file. It is a framing change.

---

## 6. Cost to serve, and other operational framings

### What it is

The hope that ticket volume, priority mix or handling time could support an
operational story that does not require the fields to be predictive.

### Verdict

Drop it. Cost to serve needs handling effort, and the file has no agent, no
assignee, no worklog and no reopen count. Its two duration fields are
independent draws, so any derived handling time is noise, and 49.3 percent of
them are negative. Volume per customer cannot segment anything, because the
mapping is a cover by construction: every customer has at least one ticket and
93 percent have exactly one, so the variable is nearly a constant.

The priority and type mixes are close to uniform (Medium 2,192, Critical
2,129, High 2,085, Low 2,063) and are independent of every customer attribute,
so a mix-shift or triage-load story has nothing to shift.

What a real version would need is in section 2: `Worklog.timeSpentSeconds`,
the SLA cycle durations with `paused` and `withinCalendarHours` so that
waiting on the customer is separated from waiting on the agent, approval
`createdDate` to `completedDate` gaps, and `jsm_issue_organization_mapping` so
cost can be attributed to an account rather than an individual.

### Effort

Not applicable. Recommending against.

---

## 7. The audit as a reusable data quality artifact

### What it is

Package the checks we ran as a check suite that Atlassian, or anyone, could
run on a support extract before trusting it. This turns a negative finding into
a deliverable.

### Primary sources

The practice has a literature and a name. Schelter and co-authors describe a
declarative system for "unit tests for data" that combines quality constraints
with user-defined validation and runs them at scale
([Automating Large-Scale Data Quality Verification, PVLDB 2018;11(12)](https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf),
implementation at [awslabs/deequ](https://github.com/awslabs/deequ)).
Polyzotis, Zinkevich, Roy, Breck and Whang describe the data validation system
deployed inside Google's TFX to detect anomalies in data entering ML pipelines
([Data Validation for Machine Learning, MLSys 2019](https://proceedings.mlsys.org/paper_files/paper/2019/hash/928f1160e52192e3e0017fb63ab65391-Abstract.html),
[PDF](https://mlsys.org/Conferences/2019/doc/2019/167.pdf)). Sculley and
co-authors give the reason it matters, describing unstable and underutilised
data dependencies as a principal source of hidden technical debt in production
ML systems
([NeurIPS 2015](https://papers.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf)).

### The suite, stated as constraints

Each line is a check we actually ran, with the result on this file:

| Check | Expected | This file |
|---|---|---|
| Event timestamps are ordered within a record | 0 inversions | 49.3 percent inverted |
| Outcome distribution is not uniform across its levels | rejects uniform | chi-square 1.67, p = 0.80 |
| Per-entity event counts are overdispersed rather than a cover | some entities with zero events | 0 of 8,320 with zero |
| Categorical fields are associated with entity attributes | some association | none detected |
| Outcome varies with handling severity | varies | flat |
| Free text exists and is not templated | exists | no customer text field |
| Repeated measures of the same entity correlate over time | positive | tested on usage, holds at 0.82 |

### What it licenses

A slide saying that the audit is portable: these are seven constraints any
team can run on a support extract in an afternoon, and this extract fails five
of them. It is an honest framing of the work we already did rather than new
work.

### What it does not license

We did not build a library, and we must not imply we did. We ran a set of
checks in `analysis/`. Calling it a framework or a product would be the kind of
claim `docs/agents/writing-style.md` rules out.

The thresholds are ours, not a standard. Real support data can legitimately
fail some of these, for instance a genuinely uniform CSAT distribution is
possible in a small sample.

### Effort

Two hours to turn the table into a slide and to make sure each row points at
the script that produced it. More if the team wants a single runnable check
script, which is not necessary for Monday.

---

## 8. What it would mean if a production dataset looked like this

### What it is

The business framing. Each failure has a real-world cause that a support
organisation would want to catch.

A per-customer event count with no zeros is the signature of a broken join,
typically an inner join against a table derived from the events themselves,
which is precisely what happened here. In production this is how a churn model
ends up trained only on customers who contacted support.

Resolution before first response is the signature of two fields populated from
different systems with no shared clock or no ordering constraint. In
production this inflates or deflates every SLA metric computed from them.

A perfectly uniform satisfaction distribution is the signature of a survey
pipeline that has lost its join to the request, since real CSAT distributions
are strongly bimodal.

A rating field with no accompanying comment field is a collection design
choice, not a data bug, and it is the specific choice that makes sentiment
analysis impossible. JSM collects both, so the loss happened in the export.

### What it licenses

A closing argument that is actually about business value: if a dataset in this
shape reached a real analytics team, the models built on it would be
confidently wrong, and the checks in section 7 would have caught it in an
afternoon. The recommendation then lands as capture the fields your product
already models, and run the checks before you trust the extract.

### What it does not license

These are diagnoses of plausible causes, not established ones for this file.
Phrase them as what this pattern usually means, not as what happened at
Atlassian. We have no evidence about any Atlassian production system.

### Effort

One hour. It is the closing slide and it reuses sections 2, 3 and 7.

---

## Ranked recommendation

1. Section 2, the Jira Service Management field gap. Build it. It converts the
   weakest part of the submission into the part that only a team that read the
   API docs could produce, and it costs two hours with no code.

2. Section 3, how the file was assembled. Build it. The zero-customers-with-no-
   tickets result against 3,006 expected is the single most convincing number
   available for the audit, and it answers "you ignored our data" directly.

3. Section 4, the Product Purchased reinterpretation. Do it regardless of
   everything else, because the current framing is circular and a judge can
   show that in one question. Fifteen minutes.

4. Section 8, what this would mean in production. One slide, and it is the
   bridge from the audit to the recommendation.

5. Section 7, the audit as a check suite. One slide if there is room. The table
   is already written.

6. Section 1, the placebo run. Only if sections 2 to 5 are finished and there
   are three clear hours left. It is defensible if framed as a placebo input
   with a pre-stated overlap prediction, and indefensible if called a negative
   control in the Lipsitch sense or presented as validation of the model. The
   ranking pipeline flags a quartile whatever it is fed, so the claim has to be
   about agreement or separation rather than about the flag itself.

7. Section 5, the schema harness. One sentence inside another slide, not a
   slide of its own.

8. Section 6, cost to serve. Drop.
