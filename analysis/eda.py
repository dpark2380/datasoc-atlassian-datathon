"""
Clean the raw customer-support-ticket dataset and engineer features for
the EDA dashboard and the risk-scorer prototype.

Run: .venv/bin/python analysis/eda.py
Writes: analysis/cleaned_tickets.csv
"""
import re
from pathlib import Path

import kagglehub
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

OUT_PATH = Path(__file__).parent / "cleaned_tickets.csv"


def load_raw() -> pd.DataFrame:
    dataset_dir = kagglehub.dataset_download("suraj520/customer-support-ticket-dataset")
    csv_path = next(Path(dataset_dir).glob("*.csv"))
    return pd.read_csv(csv_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # The generator dataset never filled in the {product_purchased} template.
    # Strip it so sentiment scoring isn't thrown by literal curly braces.
    df["Ticket Description"] = df["Ticket Description"].str.replace(
        r"\{product_purchased\}", "the product", regex=True
    )

    for col in ("First Response Time", "Time to Resolution", "Date of Purchase"):
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Only meaningful for tickets that actually have both timestamps.
    df["Resolution Hours"] = (
        df["Time to Resolution"] - df["First Response Time"]
    ).dt.total_seconds() / 3600
    df.loc[df["Resolution Hours"] < 0, "Resolution Hours"] = pd.NA

    df["Ticket Priority"] = pd.Categorical(
        df["Ticket Priority"], categories=["Low", "Medium", "High", "Critical"], ordered=True
    )

    return df


def score_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Directional sentiment only. This dataset's free text is templated /
    synthetic filler (see references discussion) -- do not present this as
    ground-truth NLP, present it as a proxy signal layered on top of the
    structured drivers (priority, channel, resolution time, satisfaction).
    """
    df = df.copy()
    analyzer = SentimentIntensityAnalyzer()
    df["Sentiment Compound"] = df["Ticket Description"].fillna("").apply(
        lambda text: analyzer.polarity_scores(text)["compound"]
    )
    df["Sentiment Label"] = pd.cut(
        df["Sentiment Compound"],
        bins=[-1.01, -0.05, 0.05, 1.01],
        labels=["Negative", "Neutral", "Positive"],
    )
    return df


def business_risk_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple, explainable rule-based flag for the prototype tool (workstream C):
    a ticket is "at risk" if it combines high urgency, slow/no resolution,
    and negative sentiment or low satisfaction -- the combination most likely
    to precede churn, not any single field in isolation.
    """
    df = df.copy()
    high_priority = df["Ticket Priority"].isin(["High", "Critical"])
    slow_or_unresolved = (df["Resolution Hours"].isna()) | (df["Resolution Hours"] > df["Resolution Hours"].median())
    unhappy = (df["Sentiment Label"] == "Negative") | (df["Customer Satisfaction Rating"] <= 2)

    df["At Risk"] = high_priority & slow_or_unresolved & unhappy
    return df


def main() -> None:
    raw = load_raw()
    df = clean(raw)
    df = score_sentiment(df)
    df = business_risk_flag(df)
    df.to_csv(OUT_PATH, index=False)

    print(f"Rows: {len(df)}")
    print(f"At-risk tickets: {df['At Risk'].sum()} ({df['At Risk'].mean():.1%})")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
