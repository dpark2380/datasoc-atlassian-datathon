"""
Rerun this the moment the real dataset drops. It answers one question fast:
does anything in the data actually explain the outcome variable, or is it
noise (like Customer Satisfaction Rating turned out to be in the placeholder
Kaggle dataset)?

Run: .venv/bin/python analysis/sanity_check.py [csv_path] [outcome_column]
Defaults to the cleaned placeholder dataset and Customer Satisfaction Rating.
"""
import sys
from pathlib import Path

import pandas as pd

DEFAULT_CSV = Path(__file__).parent / "cleaned_tickets.csv"
DEFAULT_OUTCOME = "Customer Satisfaction Rating"


def check(csv_path: Path, outcome: str) -> None:
    df = pd.read_csv(csv_path)
    if outcome not in df.columns:
        print(f"Column '{outcome}' not found. Available columns:\n{list(df.columns)}")
        return

    print(f"=== Outcome distribution: {outcome} ===")
    print(df[outcome].value_counts(normalize=True, dropna=False).sort_index())
    print()

    numeric_cols = df.select_dtypes("number").columns.drop(outcome, errors="ignore")
    if len(numeric_cols):
        print("=== Correlation with numeric columns ===")
        print(df[numeric_cols].corrwith(df[outcome]).sort_values(key=abs, ascending=False))
        print()

    categorical_cols = [
        c for c in df.select_dtypes(exclude="number").columns
        if df[c].nunique() <= 20 and c != outcome
    ]
    for col in categorical_cols:
        group_means = df.groupby(col)[outcome].mean()
        spread = group_means.max() - group_means.min()
        flag = "  <-- near-zero spread, likely no real relationship" if spread < 0.15 * df[outcome].std() else ""
        print(f"{col}: group-mean spread = {spread:.3f}{flag}")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    outcome = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTCOME
    check(csv_path, outcome)
