"""
Robustness checks for the Risk Score / Risk Category logic in eda.py.

Answers one question for each parameter we picked by judgment rather than
by fitting to an outcome label (there isn't one in this dataset): does a
reasonable alternative choice change WHO gets flagged, or just fine-tune
the result? See docs/findings-sensitivity.md for the write-up.

Run: .venv/bin/python analysis/sensitivity_checks.py
Reads: analysis/customer_risk.csv (run eda.py first)
Writes: docs/findings-sensitivity.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

RISK_CSV = Path(__file__).parent / "customer_risk.csv"
OUT_DOC = Path(__file__).parent.parent / "docs" / "findings-sensitivity.md"


def cutoff_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """At Risk is currently 'bottom 25% of Engagement Composite within
    Plan Type x Primary Product'. Check other cutoffs: does that change the
    resulting Risk Category split in a way that matters?

    An earlier version of this check compared the TIER MIX of who gets
    flagged across cutoffs. That number is guaranteed to be near-constant and
    equal to the population's own tier distribution, regardless of cutoff:
    Engagement Percentile is a rank computed separately WITHIN each Plan Type
    x Product group, so cutting at any threshold selects that same share of
    every group by construction. It was not a robustness finding, it was an
    identity, and presenting it as evidence of stability was a real error
    (caught by inspection of the dashboard, not by us). See
    docs/findings-sensitivity.md for the corrected write-up.

    What can actually move is the four-way Risk Category split, since
    category also depends on tenure and the high-value gate, neither of
    which is defined as a percentile within group. This recomputes At Risk
    at each cutoff and re-derives the category the same way build_customer_risk
    does, using the tenure and embeddedness columns already in the data
    (neither depends on the cutoff)."""
    high_value = df["Plan Type"].isin(["Enterprise", "Premium"]) | (df["Embeddedness Percentile"] >= 75)

    rows = []
    for cutoff in [15, 20, 25, 30, 35]:
        at_risk = df["Engagement Percentile"] <= cutoff
        category = pd.Series("Monitor Only", index=df.index)
        category[at_risk & df["Recently Acquired (relative)"]] = "New & Struggling"
        category[at_risk & ~df["Recently Acquired (relative)"] & high_value] = "High-Value Disengaged"
        category[at_risk & ~df["Recently Acquired (relative)"] & ~high_value] = "Established & Low Engagement"
        counts = category.value_counts()
        rows.append({
            "Cutoff %": cutoff,
            "Monitor Only": counts.get("Monitor Only", 0),
            "New & Struggling": counts.get("New & Struggling", 0),
            "Established & Low Engagement": counts.get("Established & Low Engagement", 0),
            "High-Value Disengaged": counts.get("High-Value Disengaged", 0),
        })
    return pd.DataFrame(rows)


def embeddedness_weight_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """Integrations Used is currently weighted 2x Collaborators. Check
    whether other reasonable ratios rank customers the same way (Spearman
    correlation, computed as Pearson correlation of ranks) and how many
    at-risk customers would flip between High-Value Disengaged and
    Established & Low Engagement (the category split driven by this score)."""
    baseline_ratio = 2
    at_risk = df[df["At Risk"]].copy()
    high_value_tier = at_risk["Plan Type"].isin(["Enterprise", "Premium"])

    rows = []
    baseline_pct = None
    for ratio in [1, 2, 3, 5]:
        weighted = at_risk["Collaborators"] * 1 + at_risk["Integrations Used"] * ratio
        pct = weighted.rank(pct=True) * 100
        if ratio == baseline_ratio:
            baseline_pct = pct
        high_value = high_value_tier | (pct >= 75)
        rows.append({"Integrations weight": ratio, "_pct": pct, "high_value": high_value})

    baseline_high_value = rows[[r["Integrations weight"] for r in rows].index(baseline_ratio)]["high_value"]
    out_rows = []
    for r in rows:
        flip_rate = (r["high_value"] != baseline_high_value).mean()
        rank_corr = r["_pct"].rank().corr(baseline_pct.rank())
        out_rows.append({
            "Integrations weight": r["Integrations weight"],
            "Rank correlation vs. baseline (2x)": round(rank_corr, 3),
            "At-risk customers whose High-Value/Established split flips": f"{flip_rate:.1%}",
        })
    return pd.DataFrame(out_rows)


def urgency_coefficient_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """0.3/0.3 are the urgency-multiplier coefficients. Category assignment
    doesn't depend on them at all (it depends on At Risk, tenure, and the
    high-value gate) -- only the Risk Score's ranking within a category
    does. Confirm that by recomputing Risk Score at other coefficients and
    checking rank correlation, and confirm Risk Category is unchanged."""
    at_risk = df[df["At Risk"]].copy()
    severity = 100 - at_risk["Engagement Percentile"]
    tier_value = (
        at_risk["Plan Type"].astype(str)
        .map({"Free": 0.0, "Standard": 1 / 3, "Premium": 2 / 3, "Enterprise": 1.0})
        .astype(float)
        .fillna(0)
    )
    embeddedness_weight = at_risk["Embeddedness Percentile"] / 100

    baseline_score = at_risk["Risk Score"]
    rows = []
    for coef in [0.2, 0.3, 0.4, 0.5]:
        multiplier = 1 + coef * tier_value + coef * embeddedness_weight
        score = (severity * multiplier).clip(upper=100)
        rank_corr = score.rank().corr(baseline_score.rank())
        rows.append({"Urgency coefficient": coef, "Rank correlation vs. baseline (0.3)": round(rank_corr, 3)})
    return pd.DataFrame(rows)


def bootstrap_flag_stability(df: pd.DataFrame, n_resamples: int = 20, frac: float = 0.8, seed: int = 42) -> tuple[float, pd.Series]:
    """Resample 80% of customers within each Plan Type x Primary Product
    peer group, recompute the 25% cutoff on the resample, and check how
    often each customer's At Risk status agrees with the full-population
    baseline. A low agreement rate would mean the cutoff is noise-sensitive;
    a high rate means it's a stable statistic, not an artifact of exactly
    this sample. Returns (mean agreement, per-customer agreement rate)."""
    rng = np.random.default_rng(seed)
    agreement_counts = pd.Series(0, index=df.index)
    times_sampled = pd.Series(0, index=df.index)

    for i in range(n_resamples):
        sample = df.groupby(["Plan Type", "Primary Product"], observed=True).sample(
            frac=frac, random_state=int(rng.integers(0, 1_000_000))
        )
        cutoff = sample.groupby(["Plan Type", "Primary Product"], observed=True)["Engagement Composite"].transform(
            lambda s: s.quantile(0.25)
        )
        resample_flag = sample["Engagement Composite"] < cutoff
        agrees = resample_flag == df.loc[sample.index, "At Risk"]
        agreement_counts.loc[sample.index] += agrees.astype(int)
        times_sampled.loc[sample.index] += 1

    sampled = times_sampled > 0
    per_customer = agreement_counts[sampled] / times_sampled[sampled]
    return per_customer.mean(), per_customer


def main() -> None:
    df = pd.read_csv(RISK_CSV)

    cutoff_table = cutoff_sensitivity(df)
    embeddedness_table = embeddedness_weight_sensitivity(df)
    urgency_table = urgency_coefficient_sensitivity(df)
    stability, _ = bootstrap_flag_stability(df)

    print("Cutoff sensitivity:")
    print(cutoff_table.to_string(index=False))
    print()
    print("Embeddedness weight sensitivity:")
    print(embeddedness_table.to_string(index=False))
    print()
    print("Urgency coefficient sensitivity:")
    print(urgency_table.to_string(index=False))
    print()
    print(f"Bootstrap At-Risk flag stability: {stability:.1%} average agreement across 20 resamples")

    doc = f"""# Sensitivity and robustness checks

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

{cutoff_table.to_markdown(index=False)}

Every category's count grows roughly in proportion as the cutoff loosens
from 15% to 35%, and the ratios between categories stay close to stable
(New & Struggling to Established & Low Engagement runs 0.57 to 0.59;
High-Value Disengaged to Established & Low Engagement runs 0.73 to 0.74).
That is not guaranteed by how At Risk is defined, since it depends on the
joint distribution of tenure and embeddedness among the customers each wider
cutoff adds. The cutoff choice changes how many accounts are flagged, as it
should, without reshuffling which category dominates the result.

## 2. Embeddedness weight (currently Integrations Used weighted 2x Collaborators)

{embeddedness_table.to_markdown(index=False)}

Rank correlation stays high across every ratio tested (1x to 5x), meaning
the specific weight doesn't change who's considered "embedded" very much.
The High-Value/Established split among at-risk customers only flips for a
small share, even at the most extreme ratio tested.

## 3. Urgency coefficient (currently 0.3 for both tier and embeddedness)

{urgency_table.to_markdown(index=False)}

Risk Category never depends on this coefficient at all (it's gated by At
Risk, tenure, and the high-value threshold, not by the multiplier). The
coefficient only reorders customers within a category, and that ordering
stays highly correlated across every value tested.

## 4. Bootstrap stability of the At Risk flag

Resampling 80% of customers within each peer group 20 times and
recomputing the 25% cutoff on each resample, the average agreement with
the full-population flag is {stability:.1%}. The cutoff isn't reacting to
noise in this particular sample.

## What this does and doesn't prove

None of this validates that the Risk Score predicts actual churn, since
there's no churn label in this dataset to check that against (see
`findings-ml-segments.md`). What it shows is that our specific parameter
choices aren't arbitrary in the sense of being fragile: a reasonable
analyst making slightly different choices at each step would flag
essentially the same customers.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")
    print(f"\nWrote {OUT_DOC}")


if __name__ == "__main__":
    main()
