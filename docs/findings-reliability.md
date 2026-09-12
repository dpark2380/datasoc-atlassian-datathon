# Reliability of the usage metrics, and whether any trend exists

We ran an audit on the support ticket data and found it random. This is the
same audit turned on the data we did build the model on. It cuts against our
own work rather than the organisers', and it changed how the model is
weighted.

Reproduce with `.venv/bin/python analysis/reliability_checks.py`. The
permutation seed is 0.

## 1. How much of each metric is signal

A metric is only useful if it measures something stable about a customer
rather than which month you happened to look. The intraclass correlation
splits each metric's variance into the part that separates customers from
each other and the part that just moves month to month.

| Metric            |   Between-customer variance |   Within-customer variance |   ICC (single month) |   Reliability (5-month average) |
|:------------------|----------------------------:|---------------------------:|---------------------:|--------------------------------:|
| Active Days       |                      20.925 |                      4.573 |                0.821 |                           0.958 |
| Sessions          |                      86.057 |                     10.72  |                0.889 |                           0.976 |
| Product Actions   |                    2986.51  |                   1371.07  |                0.685 |                           0.916 |
| Collaborators     |                       4.187 |                     12.422 |                0.252 |                           0.628 |
| Integrations Used |                       2.686 |                      1.628 |                0.623 |                           0.892 |

The model averages 5 months per customer, so the last column is the figure
that applies to it. Averaging repeated measurements suppresses noise, which
is why a metric with a weak single-month ICC can still be usable once
averaged.

Collaborators is the weakest input by a clear margin. In any single month it
is mostly noise: its within-customer variance is larger than its
between-customer variance, meaning the same customer's collaborator count
moves around more than customers differ from each other. Averaged over 5
months it recovers to a usable but mediocre figure.

What we did about it: every composite in `analysis/eda.py` now weights each
metric by its measured reliability instead of by a hand-picked number.

What this does not do, stated plainly because it would be easy to imply
otherwise: it does not reduce Collaborators' influence. Under the old scheme
the metrics were multiplied as raw values, so the effective split was 38% to
Collaborators and 62% to Integrations Used, driven by raw scale rather than
by intent. Reliability weighting gives Collaborators 41%. The gain is that
the split is now measured and can be explained, not that a noisy variable was
removed. Changing it moved exactly one customer between categories.

## 2. Whether any trend exists in the 5-month panel

The obvious question about a 5-month panel is why there is no trend analysis.
The answer is that we tested for one and there is nothing to analyse.

We fit a least-squares slope through each customer's 5 monthly Active Days
values (8,320 customers with complete months), then did the same
after shuffling each customer's months into a random order. Shuffling destroys
any real time ordering. If customers had real trends, the shuffled slopes
would be visibly flatter.

| Measure | Value |
|---|---|
| Standard deviation of real slopes | 0.6658 |
| Standard deviation of shuffled slopes | 0.6675 |
| Ratio | 0.997 |

A ratio of 1.0 means real slopes are indistinguishable from slopes fitted to
randomly reordered data. At 0.997, that is what we have.

The split-half check says the same thing from a different angle. A real trend
persists, so a customer trending up in the first half should still be trending
up in the second. The actual correlation between first-half and second-half
slopes is -0.492. It is negative, which is mean reversion:
a customer above their own average one month tends to be below it the next.
That is the signature of fluctuation around a stable level, not a trajectory.

Consistent with both: 19.9% of customers look like they are
declining and 18.6% look like they are rising, which is close
to the even split you would expect from noise.

## What this means

Every slope, percent-change, or trend feature derivable from this panel is
measuring noise. That includes any such column in derived datasets built from
these files.

It also settles a naming problem in our own model. A category was previously
called "Established & Declining", which claimed a trajectory this test shows
the data cannot support. It is now "Established & Low Engagement", describing
a level rather than a direction, which is what the model actually measures.

The risk model compares a customer's usage level against their peer group
rather than against their own history, and this is the reason why.
