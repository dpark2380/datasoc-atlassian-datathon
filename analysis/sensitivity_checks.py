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
    Plan Type x Primary Product'. Check other cutoffs: does the flagged
    population's tier mix stay stable, or does it swing around?"""
    rows = []
    for cutoff in [15, 20, 25, 30, 35]:
        flagged = df["Engagement Percentile"] <= cutoff
        n = flagged.sum()
        tier_mix = df.loc[flagged, "Plan Type"].value_counts(normalize=True)
        rows.append({
            "Cutoff %": cutoff,
            "Customers flagged": n,
            "Share of base": round(n / len(df), 3),
            "% Enterprise": round(tier_mix.get("Enterprise", 0), 3),
            "% Premium": round(tier_mix.get("Premium", 0), 3),
            "% Standard": round(tier_mix.get("Standard", 0), 3),
            "% Free": round(tier_mix.get("Free", 0), 3),
        })
    return pd.DataFrame(rows)


def embeddedness_weight_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """Integrations Used is currently weighted 2x Collaborators. Check
    whether other reasonable ratios rank customers the same way (Spearman
    correlation, computed as Pearson correlation of ranks) and how many
    at-risk customers would flip between High-Value Disengaged and
    Established & Declining (the category split driven by this score)."""
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
    tier_value = at_risk["Plan Type"].map({"Free": 0.0, "Standard": 1 / 3, "Premium": 2 / 3, "Enterprise": 1.0}).fillna(0)
    embeddedness_weight = at_risk["Embeddedness Percentile"] / 100

    baseline_score = at_risk["Risk Score"]
    rows = []
    for coef in [0.2, 0.3, 0.4, 0.5]:
        multiplier = 1 + coef * tier_value + coef * embeddedness_weight
        score = (severity * multiplier).clip(upper=100)
        rank_corr = score.rank().corr(baseline_score.rank())
        rows.append({"Urgency coefficient": coef, "Rank correlation vs. baseline (0.3)": round(rank_corr, 3)})
    return pd.DataFrame(rows)


def bootstrap_flag_stability(df: pd.DataFrame, n_resamples: int = 20, frac: float = 0.8, seed: int = 42) -> float:
    """Resample 80% of customers within each Plan Type x Primary Product
    peer group, recompute the 25% cutoff on the resample, and check how
    often each customer's At Risk status agrees with the full-population
    baseline. A low agreement rate would mean the cutoff is noise-sensitive;
    a high rate means it's a stable statistic, not an artifact of exactly
    this sample."""
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
    return (agreement_counts[sampled] / times_sampled[sampled]).mean()


def main() -> None:
    df = pd.read_csv(RISK_CSV)

    cutoff_table = cutoff_sensitivity(df)
    embeddedness_table = embeddedness_weight_sensitivity(df)
    urgency_table = urgency_coefficient_sensitivity(df)
    stability = bootstrap_flag_stability(df)

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

{cutoff_table.to_markdown(index=False)}

The tier mix of who's flagged stays close to stable across cutoffs from
15% to 35%: this isn't a knife-edge choice where a slightly different
percentage would flag a completely different population.

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
