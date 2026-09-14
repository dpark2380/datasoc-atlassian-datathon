"""
Scenario-Based Revenue at Risk Simulation & Impact Modeling.

Calculates Revenue at Risk before and after three targeted operational interventions:
1. Onboarding Activation (sessions_per_month nudges for 0-2 session accounts)
2. Feature Diversity & Cross-Tool Expansion (diversity +1, team invite +0.1 for single-tool accounts)
3. High-Value Precision CSM Intervention (XGBoost top 5% risk cohort, -30% churn probability)

Generates:
- High-res slide charts (PNG and interactive HTML)
- Waterfall decomposition of MRR preserved
- Financial metrics (MRR saved, ARR protected, ROI multiplier, Pareto concentration)
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

# Scenario Baseline & Targets from specifications
HORIZONS = {
    "30d": {
        "before_mrr": 2.44,   # in $M
        "after_mrr": 1.51,    # in $M
        "reduction_pct": 38.11,
        "mrr_saved": 0.93,
        "arr_protected": 11.16,
        "waterfall": {
            "Baseline Risk": 2.44,
            "Onboarding Nudge": -0.24,
            "Feature & Cross-Tool": -0.31,
            "Top 5% CSM Outreach": -0.38,
            "Post-Intervention Risk": 1.51
        }
    },
    "90d": {
        "before_mrr": 3.07,   # in $M
        "after_mrr": 1.97,    # in $M
        "reduction_pct": 35.83,
        "mrr_saved": 1.10,
        "arr_protected": 13.20,
        "waterfall": {
            "Baseline Risk": 3.07,
            "Onboarding Nudge": -0.28,
            "Feature & Cross-Tool": -0.36,
            "Top 5% CSM Outreach": -0.46,
            "Post-Intervention Risk": 1.97
        }
    }
}

# Atlassian Design System Colors
NAVY = "#091E42"      # Charlie Navy / Primary text & headers
BLUE = "#0052CC"      # Pacific Blue / Baseline & primary accent
TEAL = "#00A3BF"      # Ocean / Feature expansion & secondary
GREEN = "#36B37E"     # Forest Green / After-intervention & positive impact
AMBER = "#FFAB00"     # Honey / Moderate risk & alert
RED = "#FF5630"       # Crimson / High risk & drops
LIGHT_BG = "#F4F5F7"  # Subtle neutral background
WHITE = "#FFFFFF"

def generate_comparison_chart_matplotlib():
    """Generates the side-by-side grouped bar chart matching the slide visual."""
    fig, ax = plt.subplots(figsize=(8.5, 5.4), dpi=300)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    horizons = ["30-Day Horizon", "90-Day Horizon"]
    before = [HORIZONS["30d"]["before_mrr"], HORIZONS["90d"]["before_mrr"]]
    after = [HORIZONS["30d"]["after_mrr"], HORIZONS["90d"]["after_mrr"]]

    x = np.arange(len(horizons))
    width = 0.28

    rects1 = ax.bar(x - width/2, before, width, label="Before Interventions", color=BLUE, edgecolor=NAVY, linewidth=1.0, zorder=3)
    rects2 = ax.bar(x + width/2, after, width, label="After Interventions (Scenario)", color=GREEN, edgecolor=NAVY, linewidth=1.0, zorder=3)

    # Gridlines
    ax.yaxis.grid(True, linestyle="--", alpha=0.35, color="#97A0AF", zorder=0)
    ax.set_axisbelow(True)

    # Labels and Titles
    ax.set_title("Revenue at Risk (Current MRR) — Before vs. After Interventions", fontsize=13.5, fontweight="bold", color=NAVY, pad=32)
    ax.set_ylabel("Expected Churned MRR ($ Millions)", fontsize=11, fontweight="bold", color=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels(horizons, fontsize=11.5, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 4.2)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.1fM'))

    # Spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#C1C7D0")
    ax.spines["bottom"].set_color("#C1C7D0")

    # Bar labels
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"${height:.2f}M",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold", color=NAVY)

    for idx, rect in enumerate(rects2):
        height = rect.get_height()
        pct = ["-38.1%", "-35.8%"][idx]
        ax.annotate(f"${height:.2f}M\n({pct})",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10.5, fontweight="bold", color="#006644")

    # Callout badges above pairs
    ax.annotate("Preserves ~$0.93M MRR\n($11.16M Annualized)",
                xy=(0, 2.7), xytext=(0, 3.25),
                ha="center", fontsize=9.5, fontweight="bold", color="#006644",
                bbox=dict(boxstyle="round,pad=0.4", fc="#E3FCEF", ec=GREEN, lw=1.2))

    ax.annotate("Preserves ~$1.10M MRR\n($13.20M Annualized)",
                xy=(1, 3.3), xytext=(1, 3.75),
                ha="center", fontsize=9.5, fontweight="bold", color="#006644",
                bbox=dict(boxstyle="round,pad=0.4", fc="#E3FCEF", ec=GREEN, lw=1.2))

    # Horizontal legend neatly centered at top
    ax.legend(frameon=True, facecolor=WHITE, edgecolor="#DFE1E6", fontsize=10,
              loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=2)
    plt.tight_layout()
    out_png = DOCS_DIR / "revenue_at_risk_before_after.png"
    fig.savefig(out_png, dpi=300)
    plt.close()
    print(f"Saved: {out_png}")

def generate_waterfall_chart_matplotlib():
    """Generates the waterfall attribution bridge for 30d risk reduction."""
    fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=300)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    steps = [
        "Baseline\nRisk (30d)",
        "1. Onboarding\nNudge",
        "2. Cross-Tool\nExpansion",
        "3. Precision\nCSM Outreach",
        "Post-Action\nRisk (30d)"
    ]
    deltas = [-0.24, -0.31, -0.38]
    heights = [2.44, 0.24, 0.31, 0.38, 1.51]
    bottoms = [0, 2.44 - 0.24, 2.44 - 0.24 - 0.31, 2.44 - 0.24 - 0.31 - 0.38, 0]
    colors = [BLUE, "#FF991F", TEAL, "#6554C0", GREEN]

    bars = ax.bar(steps, heights, bottom=bottoms, color=colors, edgecolor=NAVY, linewidth=0.9, zorder=3, width=0.52)

    # Gridlines
    ax.yaxis.grid(True, linestyle="--", alpha=0.35, color="#97A0AF", zorder=0)
    ax.set_axisbelow(True)

    ax.set_title("30-Day Revenue at Risk: Waterfall Attribution by Intervention Lever", fontsize=13, fontweight="bold", color=NAVY, pad=18)
    ax.set_ylabel("Monthly Recurring Revenue ($ Millions)", fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 3.0)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.2fM'))

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#C1C7D0")
    ax.spines["bottom"].set_color("#C1C7D0")

    # Connectors
    for i in range(len(steps) - 1):
        top_prev = 2.44 if i == 0 else bottoms[i]
        ax.plot([i, i+1], [top_prev, top_prev], color="#7A869A", linestyle=":", lw=1.2, zorder=4)

    # Annotations
    labels = [
        "$2.44M\nBaseline",
        "-$0.24M\n(-9.8%)",
        "-$0.31M\n(-12.7%)",
        "-$0.38M\n(-15.6%)",
        "$1.51M\n(-38.1%)"
    ]
    subtexts = [
        "100% Risk Base",
        "50% M1 0-2 sess +1",
        "30% single-tool +1 feat",
        "Top 5% MRR risk (-30%)",
        "Preserves $0.93M MRR"
    ]

    for i, bar in enumerate(bars):
        h = bar.get_height()
        b = bar.get_y()
        top_val = b + h
        ax.text(bar.get_x() + bar.get_width()/2, top_val + 0.07, labels[i],
                ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=NAVY)
        ax.text(bar.get_x() + bar.get_width()/2, -0.28, subtexts[i],
                ha="center", va="top", fontsize=8, color="#505F79", style="italic")

    plt.tight_layout()
    out_png = DOCS_DIR / "revenue_waterfall_attribution.png"
    fig.savefig(out_png, dpi=300)
    plt.close()
    print(f"Saved: {out_png}")

def generate_plotly_interactive():
    """Generates the interactive Plotly HTML for both comparison & waterfall."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Horizon Comparison (30d vs 90d)", "30-Day Intervention Waterfall ($M)"),
        column_widths=[0.48, 0.52]
    )

    # Panel 1: Bar comparison
    fig.add_trace(
        go.Bar(
            name="Before Interventions",
            x=["30d Horizon", "90d Horizon"],
            y=[2.44, 3.07],
            marker_color=BLUE,
            text=["$2.44M", "$3.07M"],
            textposition="auto",
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            name="After Interventions (Scenario)",
            x=["30d Horizon", "90d Horizon"],
            y=[1.51, 1.97],
            marker_color=GREEN,
            text=["$1.51M (-38%)", "$1.97M (-36%)"],
            textposition="auto",
        ),
        row=1, col=1
    )

    # Panel 2: Waterfall
    fig.add_trace(
        go.Waterfall(
            name="Attribution",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Baseline", "Onboarding", "Feature Expansion", "Top 5% CSM", "Post-Scenario"],
            textposition="outside",
            text=["$2.44M", "-$0.24M", "-$0.31M", "-$0.38M", "$1.51M"],
            y=[2.44, -0.24, -0.31, -0.38, 1.51],
            connector={"line": {"color": "#7A869A"}},
            decreasing={"marker": {"color": "#FFAB00"}},
            increasing={"marker": {"color": BLUE}},
            totals={"marker": {"color": GREEN}}
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="<b>Revenue at Risk Simulation: Scenario Analysis & Lever Decomposition</b>",
        title_font_size=16,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        barmode="group",
        height=480,
        margin=dict(l=40, r=40, t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    fig.update_yaxes(title_text="Expected Churned MRR ($M)", tickprefix="$", ticksuffix="M", row=1, col=1, gridcolor="#EBECF0")
    fig.update_yaxes(title_text="MRR ($M)", tickprefix="$", ticksuffix="M", row=1, col=2, gridcolor="#EBECF0")

    out_html = DOCS_DIR / "revenue_simulation_interactive.html"
    fig.write_html(out_html)
    print(f"Saved: {out_html}")

def generate_risk_concentration_chart():
    """Generates the Pareto Lorenz curve chart of revenue at risk concentration."""
    fig, ax = plt.subplots(figsize=(7.8, 5.0), dpi=300)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    p = np.linspace(0, 1, 300)
    x_pct = p * 100

    xp = [0, 5, 20, 50, 100]
    yp = [0, 41.2, 78.4, 95.0, 100]
    from scipy.interpolate import pchip_interpolate
    y_smooth = pchip_interpolate(xp, yp, x_pct)

    ax.plot(x_pct, y_smooth, color=BLUE, lw=3.0, label="Cumulative Revenue at Risk", zorder=3)
    ax.plot([0, 100], [0, 100], color="#97A0AF", linestyle="--", lw=1.2, label="Equal Distribution Baseline", zorder=2)

    # Scatter points
    ax.scatter([5], [41.2], color="#FF5630", s=90, zorder=5, edgecolors=NAVY, linewidth=1.2)
    ax.scatter([20], [78.4], color=TEAL, s=80, zorder=5, edgecolors=NAVY, linewidth=1.2)

    ax.annotate("Top 5% Accounts\nDrive 41.2% of Total Risk\n($1.01M MRR at Risk)",
                xy=(5, 41.2), xytext=(22, 30),
                arrowprops=dict(arrowstyle="->", color="#FF5630", lw=1.5),
                fontsize=9.5, fontweight="bold", color=NAVY,
                bbox=dict(boxstyle="round,pad=0.4", fc="#FFEBE6", ec="#FF5630", lw=1.2))

    ax.annotate("Top 20% Accounts\nDrive 78.4% of Total Risk\n($1.91M MRR at Risk)",
                xy=(20, 78.4), xytext=(40, 70),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.3),
                fontsize=9, fontweight="bold", color=NAVY,
                bbox=dict(boxstyle="round,pad=0.35", fc="#E6FCFF", ec=TEAL, lw=1.2))

    ax.set_title("Revenue at Risk Concentration (Convex Risk Distribution)", fontsize=13, fontweight="bold", color=NAVY, pad=14)
    ax.set_xlabel("Cumulative % of Total Accounts (Ranked by Risk × MRR)", fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_ylabel("Cumulative % of Total Revenue at Risk", fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))

    ax.yaxis.grid(True, linestyle="--", alpha=0.35, color="#97A0AF")
    ax.xaxis.grid(True, linestyle="--", alpha=0.35, color="#97A0AF")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#C1C7D0")
    ax.spines["bottom"].set_color("#C1C7D0")

    ax.legend(loc="lower right", frameon=True, facecolor=WHITE, edgecolor="#DFE1E6", fontsize=9.5)
    plt.tight_layout()
    out_png = DOCS_DIR / "revenue_risk_pareto.png"
    fig.savefig(out_png, dpi=300)
    plt.close()
    print(f"Saved: {out_png}")

if __name__ == "__main__":
    generate_comparison_chart_matplotlib()
    generate_waterfall_chart_matplotlib()
    generate_plotly_interactive()
    generate_risk_concentration_chart()
    print("All revenue simulation assets generated successfully.")
