# Sensitivity and robustness checks

These check whether the Risk Score / Risk Category parameters we chose by
judgment (there's no outcome label to fit them against) meaningfully
change who gets flagged, or just fine-tune the result. See
`docs/build-plan.md` section 4 for why these parameters exist in the first
place.

## 1. At Risk cutoff (currently bottom 25% within Plan Type x Product)

|   Cutoff % |   Customers flagged |   Share of base |   % Enterprise |   % Premium |   % Standard |   % Free |
|-----------:|--------------------:|----------------:|---------------:|------------:|-------------:|---------:|
|         15 |                1239 |           0.149 |          0.144 |       0.282 |        0.398 |    0.177 |
|         20 |                1656 |           0.199 |          0.144 |       0.281 |        0.399 |    0.177 |
|         25 |                2072 |           0.249 |          0.144 |       0.281 |        0.398 |    0.177 |
|         30 |                2487 |           0.299 |          0.144 |       0.281 |        0.398 |    0.177 |
|         35 |                2904 |           0.349 |          0.144 |       0.281 |        0.398 |    0.177 |

The tier mix of who's flagged stays close to stable across cutoffs from
15% to 35%: this isn't a knife-edge choice where a slightly different
percentage would flag a completely different population.

## 2. Embeddedness weight (currently Integrations Used weighted 2x Collaborators)

|   Integrations weight |   Rank correlation vs. baseline (2x) | At-risk customers whose High-Value/Established split flips   |
|----------------------:|-------------------------------------:|:-------------------------------------------------------------|
|                     1 |                                0.973 | 1.4%                                                         |
|                     2 |                                1     | 0.0%                                                         |
|                     3 |                                0.994 | 0.6%                                                         |
|                     5 |                                0.978 | 0.7%                                                         |

Rank correlation stays high across every ratio tested (1x to 5x), meaning
the specific weight doesn't change who's considered "embedded" very much.
The High-Value/Established split among at-risk customers only flips for a
small share, even at the most extreme ratio tested.

## 3. Urgency coefficient (currently 0.3 for both tier and embeddedness)

|   Urgency coefficient |   Rank correlation vs. baseline (0.3) |
|----------------------:|--------------------------------------:|
|                   0.2 |                                 0.878 |
|                   0.3 |                                 1     |
|                   0.4 |                                 0.914 |
|                   0.5 |                                 0.818 |

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
