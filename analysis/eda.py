"""
Build the customer engagement/risk view from the official datathon dataset.

Full audit of what's real vs. noise in this dataset lives in
docs/findings-data-quality.md (plain-language version) -- summary:

REAL, used here:
  - product_usage.csv has genuine per-customer persistence (Jan-May 2023
    Active Days correlation = 0.82) and usage level tracks Plan Type
    cleanly (Free 5.3 -> Enterprise 11.5 avg active days/month).
  - Product also shows a real, moderate difference (Jira ~10.0 vs Loom
    ~6.7 avg active days) -- kept as a secondary cut.

NOT REAL, not used as a signal (kept only as descriptive/operational
context where shown at all):
  - Customer Satisfaction Rating: statistically random.
  - Ticket Type / Priority / Channel: near-uniform distributions --
    independently randomly assigned per ticket.
  - Resolution Hours: mean ~0, often negative -- timestamps are not
    coherent, not usable as a duration.
  - Ticket volume per customer: flat across every segment (~1.0-1.02
    tickets/customer everywhere) -- tickets are not linked to who the
    customer is.
  - No free-text field exists in this dataset at all (no Ticket
    Description; Resolution is synthetic filler, not real language).
  - Industry / Region / Company Size: flat, no relationship to usage.

Run: .venv/bin/python analysis/eda.py
Writes: analysis/cleaned_tickets.csv   (ticket-level, descriptive only)
        analysis/customer_engagement.csv  (customer-level, the real signal)
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "references" / "Dataset"
OUT_TICKETS = Path(__file__).parent / "cleaned_tickets.csv"
OUT_CUSTOMER_ENGAGEMENT = Path(__file__).parent / "customer_engagement.csv"

USAGE_METRICS = ["Active Days", "Sessions", "Product Actions", "Collaborators", "Integrations Used"]


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tickets = pd.read_csv(DATA_DIR / "customer_support_tickets.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    usage = pd.read_csv(DATA_DIR / "product_usage.csv")
    return tickets, customers, usage


def clean_tickets(tickets: pd.DataFrame) -> pd.DataFrame:
    """Descriptive/operational cleaning only -- see module docstring for why
    none of these fields are used as a predictive signal."""
    df = tickets.copy()
    df["Date of Purchase"] = pd.to_datetime(df["Date of Purchase"], format="%d-%m-%Y", errors="coerce")
    df["First Response Time"] = pd.to_datetime(df["First Response Time"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["Time to Resolution"] = pd.to_datetime(df["Time to Resolution"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["Ticket Priority"] = pd.Categorical(
        df["Ticket Priority"], categories=["Low", "Medium", "High", "Critical"], ordered=True
    )
    return df


def join_customer_id(tickets: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Tickets carry no Customer ID -- join on email (verified 1:1, 100% match)."""
    return tickets.merge(customers[["Customer ID", "Customer Email"]], on="Customer Email", how="left")


def ticket_count_per_customer(tickets: pd.DataFrame) -> pd.DataFrame:
    """Descriptive only -- confirmed flat across every segment, not a risk signal."""
    return tickets.groupby("Customer ID").size().rename("Ticket Count").reset_index()


def customer_usage_summary(usage: pd.DataFrame) -> pd.DataFrame:
    """Average usage metrics per customer across their 5-month history."""
    return usage.groupby("Customer ID")[USAGE_METRICS].mean().reset_index()


def build_customer_engagement(customers: pd.DataFrame, usage_summary: pd.DataFrame, ticket_counts: pd.DataFrame) -> pd.DataFrame:
    df = customers.merge(usage_summary, on="Customer ID", how="left")
    df = df.merge(ticket_counts, on="Customer ID", how="left")
    df["Ticket Count"] = df["Ticket Count"].fillna(0)

    # Underengaged = bottom quartile of Active Days within the customer's
    # OWN plan-tier peer group. This is the one real, defensible risk signal
    # in the dataset: usage genuinely tracks plan tier, so a customer well
    # below their tier's norm is anomalous relative to real peers, not
    # relative to a global average that mixes tiers with very different
    # baselines.
    tier_cutoff = df.groupby("Plan Type")["Active Days"].transform(lambda s: s.quantile(0.25))
    df["Underengaged"] = df["Active Days"] < tier_cutoff

    return df


def main() -> None:
    tickets_raw, customers, usage = load_raw()

    tickets = clean_tickets(tickets_raw)
    tickets = join_customer_id(tickets, customers)
    tickets.to_csv(OUT_TICKETS, index=False)

    usage_summary = customer_usage_summary(usage)
    ticket_counts = ticket_count_per_customer(tickets)
    engagement = build_customer_engagement(customers, usage_summary, ticket_counts)
    engagement.to_csv(OUT_CUSTOMER_ENGAGEMENT, index=False)

    print(f"Tickets (descriptive only): {len(tickets)} rows -> {OUT_TICKETS}")
    print(f"Customer engagement: {len(engagement)} rows -> {OUT_CUSTOMER_ENGAGEMENT}")
    print()
    print("Active Days by Plan Type:")
    print(engagement.groupby("Plan Type")["Active Days"].mean().sort_values())
    print()
    n_under = engagement["Underengaged"].sum()
    print(f"Underengaged customers (bottom quartile within their plan tier): {n_under} / {len(engagement)} ({n_under/len(engagement):.1%})")


if __name__ == "__main__":
    main()
