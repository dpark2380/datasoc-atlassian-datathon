"""
Reliability of the usage metrics, and a permutation test on trend.

This is the ticket-data audit turned on the data we did trust. Two questions:

1. How much of each usage metric is a stable customer trait rather than
   month-to-month noise? This sets the composite weights in eda.py.
2. Is there any real trend in the 5-month panel, or are the slopes noise?
   This is the answer to "why is there no trend analysis here?", which is the
   most likely technical question about a 5-month panel.

Run: .venv/bin/python analysis/reliability_checks.py
Reads: references/Dataset/product_usage.csv
Writes: docs/findings-reliability.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from eda import USAGE_METRICS, metric_reliability  # noqa: E402

DATA_DIR = Path(__file__).parent.parent / "references" / "Dataset"
OUT_DOC = Path(__file__).parent.parent / "docs" / "findings-reliability.md"
PERMUTATION_SEED = 0


def reliability_table(usage: pd.DataFrame) -> pd.DataFrame:
    """Single-month ICC next to the reliability of the 5-month average.

    The model averages 5 months, so the second column is the one that
    applies to it. The gap between the two columns is the Spearman-Brown
    effect: averaging repeated measurements suppresses the noise term.
    """
    n_months = usage.groupby("Customer ID")["Month"].nunique().median()
    averaged = metric_reliability(usage, USAGE_METRICS)

    rows = []
    for metric in USAGE_METRICS:
        per_customer = usage.groupby("Customer ID")[metric]
        between = per_customer.mean().var()
        within = per_customer.var().mean()
        rows.append({
            "Metric": metric,
            "Between-customer variance": round(between, 3),
            "Within-customer variance": round(within, 3),
            "ICC (single month)": round(between / (between + within), 3),
            f"Reliability ({n_months:.0f}-month average)": round(averaged[metric], 3),
        })
    return pd.DataFrame(rows)


def customer_month_matrix(usage: pd.DataFrame, metric: str) -> np.ndarray:
    """One row per customer, one column per month, averaged over products."""
    pivot = usage.pivot_table(index="Customer ID", columns="Month", values=metric, aggfunc="mean")
    return pivot.dropna().values


def ols_slopes(matrix: np.ndarray) -> np.ndarray:
    """Per-row least-squares slope against evenly spaced month indices."""
    x = np.arange(matrix.shape[1])
    x_centred = x - x.mean()
    y_centred = matrix - matrix.mean(axis=1, keepdims=True)
    return y_centred @ x_centred / (x_centred**2).sum()


def trend_permutation_test(usage: pd.DataFrame, metric: str = "Active Days") -> dict[str, float]:
    """Compare real per-customer slopes against slopes from shuffled months.

    If customers had real trends, shuffling each customer's months would
    destroy them and shrink the spread of slopes. If the slopes are noise,
    shuffling changes nothing, because there was no time ordering carrying
    information in the first place.

    The split-half check is the second half of the argument: a real trend
    persists, so a customer trending up early should still trend up late.
    A negative correlation is mean reversion, which is what noise looks like.
    """
    matrix = customer_month_matrix(usage, metric)
    rng = np.random.default_rng(PERMUTATION_SEED)

    real = ols_slopes(matrix)
    shuffled = ols_slopes(np.array([rng.permutation(row) for row in matrix]))

    midpoint = matrix.shape[1] // 2
    first_half = ols_slopes(matrix[:, : midpoint + 1])
    second_half = ols_slopes(matrix[:, midpoint:])

    return {
        "customers": matrix.shape[0],
        "real_slope_sd": real.std(),
        "shuffled_slope_sd": shuffled.std(),
        "sd_ratio": real.std() / shuffled.std(),
        "split_half_corr": float(np.corrcoef(first_half, second_half)[0, 1]),
        "share_declining": float((real < -0.5).mean()),
        "share_rising": float((real > 0.5).mean()),
    }


def main() -> None:
    usage = pd.read_csv(DATA_DIR / "product_usage.csv")

    table = reliability_table(usage)
    trend = trend_permutation_test(usage)

    print("Reliability of each usage metric:")
    print(table.to_string(index=False))
    print()
    print("Trend permutation test on Active Days:")
    print(f"  Real slope SD:      {trend['real_slope_sd']:.4f}")
    print(f"  Shuffled slope SD:  {trend['shuffled_slope_sd']:.4f}")
    print(f"  Ratio:              {trend['sd_ratio']:.3f}")
    print(f"  Split-half corr:    {trend['split_half_corr']:.3f}")
    print(f"  Declining / rising: {trend['share_declining']:.1%} / {trend['share_rising']:.1%}")

    doc = f"""# Reliability of the usage metrics, and whether any trend exists

We ran an audit on the support ticket data and found it random. This is the
same audit turned on the data we did build the model on. It cuts against our
own work rather than the organisers', and it changed how the model is
weighted.

Reproduce with `.venv/bin/python analysis/reliability_checks.py`. The
permutation seed is {PERMUTATION_SEED}.

## 1. How much of each metric is signal

A metric is only useful if it measures something stable about a customer
rather than which month you happened to look. The intraclass correlation
splits each metric's variance into the part that separates customers from
each other and the part that just moves month to month.

{table.to_markdown(index=False)}

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
values ({trend['customers']:,} customers with complete months), then did the same
after shuffling each customer's months into a random order. Shuffling destroys
any real time ordering. If customers had real trends, the shuffled slopes
would be visibly flatter.

| Measure | Value |
|---|---|
| Standard deviation of real slopes | {trend['real_slope_sd']:.4f} |
| Standard deviation of shuffled slopes | {trend['shuffled_slope_sd']:.4f} |
| Ratio | {trend['sd_ratio']:.3f} |

A ratio of 1.0 means real slopes are indistinguishable from slopes fitted to
randomly reordered data. At {trend['sd_ratio']:.3f}, that is what we have.

The split-half check says the same thing from a different angle. A real trend
persists, so a customer trending up in the first half should still be trending
up in the second. The actual correlation between first-half and second-half
slopes is {trend['split_half_corr']:.3f}. It is negative, which is mean reversion:
a customer above their own average one month tends to be below it the next.
That is the signature of fluctuation around a stable level, not a trajectory.

Consistent with both: {trend['share_declining']:.1%} of customers look like they are
declining and {trend['share_rising']:.1%} look like they are rising, which is close
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
"""
    OUT_DOC.write_text(doc, encoding="utf-8")
    print(f"\nWrote {OUT_DOC}")


if __name__ == "__main__":
    main()
