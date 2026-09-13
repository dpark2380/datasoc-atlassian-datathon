"""Small, testable summaries used by the Streamlit results dashboard."""

import pandas as pd


PLAN_ORDER = ["Free", "Standard", "Premium", "Enterprise"]
PRODUCT_ORDER = ["Loom", "Confluence", "Trello", "Bitbucket", "Jira"]


def _ordered_means(
    data: pd.DataFrame,
    group: str,
    order: list[str],
) -> pd.DataFrame:
    present = [value for value in order if value in data[group].unique()]
    return (
        data.groupby(group, observed=True)[["Active Days", "Integrations Used"]]
        .mean()
        .reindex(present)
        .reset_index()
    )


def build_eda_metrics(
    customers: pd.DataFrame,
    tickets: pd.DataFrame,
    usage: pd.DataFrame,
) -> dict[str, object]:
    """Calculate the compact evidence used in the dashboard's EDA pitch view."""
    first_month, last_month = usage["Month"].min(), usage["Month"].max()
    monthly_active_days = usage.groupby(["Customer ID", "Month"])["Active Days"].mean().unstack()
    complete_endpoints = monthly_active_days[[first_month, last_month]].dropna()

    ticket_times = tickets[["First Response Time", "Time to Resolution"]].apply(
        pd.to_datetime, errors="coerce", dayfirst=True
    )
    resolved = ticket_times.dropna()

    usage_with_plan = usage.merge(
        customers[["Customer ID", "Plan Type"]], on="Customer ID", how="left", validate="many_to_one"
    )
    usage_by_plan = _ordered_means(usage_with_plan, "Plan Type", PLAN_ORDER)
    usage_by_product = _ordered_means(usage, "Product", PRODUCT_ORDER)
    plan_integrations = usage_by_plan.set_index("Plan Type")["Integrations Used"]

    return {
        "first_month": first_month,
        "last_month": last_month,
        "month_count": int(usage["Month"].nunique()),
        "active_days_persistence": complete_endpoints[first_month].corr(complete_endpoints[last_month]),
        "resolved_ticket_count": len(resolved),
        "impossible_order_rate": (resolved["Time to Resolution"] < resolved["First Response Time"]).mean(),
        "integration_tier_ratio": plan_integrations["Enterprise"] / plan_integrations["Free"],
        "usage_by_plan": usage_by_plan,
        "usage_by_product": usage_by_product,
    }
