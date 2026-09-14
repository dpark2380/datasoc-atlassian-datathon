"""
Longitudinal Engagement Trajectory Utilities.
Visualizes month-over-month engagement paths across Months 1 to 5 for cohorts and specific customer accounts.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "references" / "Dataset"

RAW_MONTHS = ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"]
MONTH_LABELS = ["Month 1 (Jan)", "Month 2 (Feb)", "Month 3 (Mar)", "Month 4 (Apr)", "Month 5 (May)"]

CURATED_ARCHETYPES = {
    "CUST00446": {
        "label": "Steep Churn Dropper (10d → 2d)",
        "color": "#DE350B",
        "dash": "solid",
        "desc": "Maintained 7-10 active days through Month 4, then suffered a sudden 71% crash to 2 days in Month 5.",
    },
    "CUST00123": {
        "label": "Early Decelerator (9d → 4d in M4)",
        "color": "#FF7452",
        "dash": "solid",
        "desc": "Deceleration started 30 days early in Month 4 (from 9 to 4 active days), signaling impending disengagement.",
    },
    "CUST00197": {
        "label": "Spike & Reversion / False Dawn (4d → 6d → 2d)",
        "color": "#FFAB00",
        "dash": "dash",
        "desc": "High M4 momentum (+80%) caused by an episodic burst, followed by an immediate collapse to 2 days in Month 5.",
    },
    "CUST00001": {
        "label": "Chronic Low Engagement (3-5d flat)",
        "color": "#6554C0",
        "dash": "dot",
        "desc": "Never achieved structural workflow habituation; flatlined between 3 and 5 active days throughout.",
    },
    "CUST00004": {
        "label": "Healthy Habituated User (17-23d)",
        "color": "#36B37E",
        "dash": "solid",
        "desc": "Consistently active 17–23 days and 35–46 sessions every single month without disruption.",
    },
}

_TRAJECTORY_CACHE = {}


def load_trajectory_data():
    """Load and cache monthly aggregated telemetry matrices."""
    if "piv_days" not in _TRAJECTORY_CACHE:
        usage = pd.read_csv(DATA_DIR / "product_usage.csv")
        monthly = (
            usage.groupby(["Customer ID", "Month"])[["Active Days", "Sessions", "Product Actions"]]
            .sum()
            .reset_index()
        )
        piv_days = monthly.pivot(index="Customer ID", columns="Month", values="Active Days")
        piv_sess = monthly.pivot(index="Customer ID", columns="Month", values="Sessions")
        piv_act = monthly.pivot(index="Customer ID", columns="Month", values="Product Actions")

        m5_cutoff = float(piv_days["2023-05"].quantile(0.25))
        dis_mask = piv_days["2023-05"] <= m5_cutoff

        _TRAJECTORY_CACHE["piv_days"] = piv_days
        _TRAJECTORY_CACHE["piv_sess"] = piv_sess
        _TRAJECTORY_CACHE["piv_act"] = piv_act
        _TRAJECTORY_CACHE["m5_cutoff"] = m5_cutoff
        _TRAJECTORY_CACHE["dis_mask"] = dis_mask

    return (
        _TRAJECTORY_CACHE["piv_days"],
        _TRAJECTORY_CACHE["piv_sess"],
        _TRAJECTORY_CACHE["piv_act"],
        _TRAJECTORY_CACHE["m5_cutoff"],
        _TRAJECTORY_CACHE["dis_mask"],
    )


def build_trajectory_plot(
    metric: str = "Active Days",
    selected_customers: list = None,
    show_cohort_means: bool = True,
) -> go.Figure:
    """Generate an interactive Plotly line chart comparing monthly engagement trajectories."""
    piv_days, piv_sess, piv_act, m5_cutoff, dis_mask = load_trajectory_data()

    if metric == "Sessions":
        piv = piv_sess
        y_title = "Total Sessions per Month"
        cutoff_val = float(piv_sess["2023-05"].quantile(0.25))
    elif metric == "Product Actions":
        piv = piv_act
        y_title = "Product Actions per Month"
        cutoff_val = float(piv_act["2023-05"].quantile(0.25))
    else:
        metric = "Active Days"
        piv = piv_days
        y_title = "Active Days per Month"
        cutoff_val = m5_cutoff

    fig = go.Figure()

    # 1. Cohort benchmark lines
    if show_cohort_means:
        healthy_means = piv.loc[~dis_mask, RAW_MONTHS].mean().values
        dis_means = piv.loc[dis_mask, RAW_MONTHS].mean().values

        fig.add_trace(
            go.Scatter(
                x=MONTH_LABELS,
                y=healthy_means,
                name=f"Healthy Cohort Mean (N={int((~dis_mask).sum()):,})",
                line=dict(color="#0052CC", width=3, dash="dash"),
                mode="lines+markers",
                marker=dict(size=6),
                opacity=0.75,
                hoverinfo="x+y+name",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=MONTH_LABELS,
                y=dis_means,
                name=f"Disengaged Cohort Mean (N={int(dis_mask.sum()):,})",
                line=dict(color="#BF2600", width=3, dash="dash"),
                mode="lines+markers",
                marker=dict(size=6),
                opacity=0.75,
                hoverinfo="x+y+name",
            )
        )

    # 2. Selected customer traces
    if selected_customers is None:
        selected_customers = list(CURATED_ARCHETYPES.keys())

    palette = ["#DE350B", "#FF7452", "#FFAB00", "#6554C0", "#36B37E", "#00B8D9", "#403294"]
    for i, cid in enumerate(selected_customers):
        if cid in piv.index:
            vals = piv.loc[cid, RAW_MONTHS].values
            if cid in CURATED_ARCHETYPES:
                meta = CURATED_ARCHETYPES[cid]
                trace_name = f"{cid}: {meta['label']}"
                color = meta["color"]
                dash = meta["dash"]
            else:
                trace_name = f"Customer {cid}"
                color = palette[i % len(palette)]
                dash = "solid"

            hover_text = [
                f"<b>{trace_name}</b><br>{m}: {v:,.1f} {metric}"
                for m, v in zip(MONTH_LABELS, vals)
            ]

            fig.add_trace(
                go.Scatter(
                    x=MONTH_LABELS,
                    y=vals,
                    name=trace_name,
                    line=dict(color=color, width=3, dash=dash),
                    mode="lines+markers",
                    marker=dict(size=8),
                    text=hover_text,
                    hoverinfo="text",
                )
            )

    # 3. Disengagement threshold reference line
    fig.add_hline(
        y=cutoff_val,
        line_dash="dot",
        line_color="#FF5630",
        line_width=2,
        annotation_text=f"M5 Disengagement Cutoff ({cutoff_val:.1f} {metric})",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title=dict(
            text=(
                f"<b>Longitudinal Telemetry: Monthly {metric} (Months 1–5)</b><br>"
                f"<sup>Tracking month-over-month adoption trajectories vs. disengagement cutoff</sup>"
            ),
            x=0.0,
            xanchor="left",
        ),
        xaxis=dict(title="Month", gridcolor="#EBECF0"),
        yaxis=dict(title=y_title, gridcolor="#EBECF0"),
        template="plotly_white",
        height=520,
        legend=dict(orientation="h", y=-0.22, x=0.0),
        margin=dict(l=60, r=40, t=75, b=100),
    )
    return fig


def get_archetype_summary_df(metric: str = "Active Days") -> pd.DataFrame:
    """Return a formatted DataFrame of archetype metrics across Months 1-5."""
    piv_days, piv_sess, piv_act, _, _ = load_trajectory_data()
    piv = piv_sess if metric == "Sessions" else (piv_act if metric == "Product Actions" else piv_days)

    rows = []
    for cid, meta in CURATED_ARCHETYPES.items():
        vals = piv.loc[cid, RAW_MONTHS].tolist()
        m1_3 = float(np.mean(vals[:3]))
        m4 = float(vals[3])
        m5 = float(vals[4])
        m4_drop = m4 - m1_3
        m5_drop = m5 - m4
        rows.append({
            "Customer ID": cid,
            "Archetype": meta["label"],
            "M1 (Jan)": vals[0],
            "M2 (Feb)": vals[1],
            "M3 (Mar)": vals[2],
            "M4 (Apr)": vals[3],
            "M5 (May)": vals[4],
            "M4 Delta": f"{m4_drop:+.1f}",
            "M5 Delta": f"{m5_drop:+.1f}",
            "Key Observation": meta["desc"],
        })
    return pd.DataFrame(rows)
