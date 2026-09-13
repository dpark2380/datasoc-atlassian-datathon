# Sensitivity and robustness checks

These check whether the Risk Score / Risk Category parameters we chose by
judgment (there's no outcome label to fit them against) meaningfully
change who gets flagged, or just fine-tune the result. See
`docs/build-plan.md` section 4 for why these parameters exist in the first
place.

## 1. At Risk cutoff (currently bottom 25% within Plan Type x Product)

An earlier version of this check compared the tier mix of who gets flagged
across cutoffs and reported it as stable evidence of robustness. That was
wrong, not in the arithmetic but in what the arithmetic could show: Engagement
Percentile is a rank computed separately within each Plan Type x Product
group, so cutting at any threshold selects that same share of every group by
construction. The tier mix of the flagged population is guaranteed to equal
the tier mix of the whole population at every cutoff. It was an identity
presented as a finding, caught on inspection of the dashboard rather than by
us, and it has been replaced with the check below.

What can actually move with the cutoff is the four-way Risk Category split,
since category also depends on tenure and the high-value gate, neither of
which is a percentile within group:

|   Cutoff % |   Monitor Only |   New & Struggling |   Established & Low Engagement |   High-Value Disengaged |
|-----------:|---------------:|-------------------:|-------------------------------:|------------------------:|
|         15 |           7081 |                306 |                            538 |                     395 |
|         20 |           6664 |                407 |                            722 |                     527 |
|         25 |           6248 |                518 |                            893 |                     661 |
|         30 |           5833 |                630 |                           1069 |                     788 |
|         35 |           5416 |                737 |                           1249 |                     918 |

Every category's count grows roughly in proportion as the cutoff loosens
from 15% to 35%, and the ratios between categories stay close to stable
(New & Struggling to Established & Low Engagement runs 0.57 to 0.59;
High-Value Disengaged to Established & Low Engagement runs 0.73 to 0.74).
That is not guaranteed by how At Risk is defined, since it depends on the
joint distribution of tenure and embeddedness among the customers each wider
cutoff adds. The cutoff choice changes how many accounts are flagged, as it
should, without reshuffling which category dominates the result.

## 2. Embeddedness weight (currently Integrations Used weighted 2x Collaborators)

|   Integrations weight |   Rank correlation vs. baseline (2x) | At-risk customers whose High-Value/Established split flips   |
|----------------------:|-------------------------------------:|:-------------------------------------------------------------|
|                     1 |                                0.973 | 1.6%                                                         |
|                     2 |                                1     | 0.0%                                                         |
|                     3 |                                0.994 | 0.6%                                                         |
|                     5 |                                0.978 | 0.6%                                                         |

Rank correlation stays high across every ratio tested (1x to 5x), meaning
the specific weight doesn't change who's considered "embedded" very much.
The High-Value/Established split among at-risk customers only flips for a
small share, even at the most extreme ratio tested.

## 3. Urgency coefficient (currently 0.3 for both tier and embeddedness)

|   Urgency coefficient |   Rank correlation vs. baseline (0.3) |
|----------------------:|--------------------------------------:|
|                   0.2 |                                 0.874 |
|                   0.3 |                                 0.997 |
|                   0.4 |                                 0.915 |
|                   0.5 |                                 0.823 |

Risk Category never depends on this coefficient at all (it's gated by At
Risk, tenure, and the high-value threshold, not by the multiplier). The
coefficient only reorders customers within a category, and that ordering
stays highly correlated across every value tested.

## 4. Bootstrap stability of the At Risk flag

Resampling 80% of customers within each peer group 20 times and
recomputing the 25% cutoff on each resample, the average agreement with
the full-population flag is 99.1%. The cutoff isn't reacting to
noise in this particular sample.

## What this does and doesn't prove

None of this validates that the Risk Score predicts actual churn, since
there's no churn label in this dataset to check that against (see
`findings-ml-segments.md`). What it shows is that our specific parameter
choices aren't arbitrary in the sense of being fragile: a reasonable
analyst making slightly different choices at each step would flag
essentially the same customers.
