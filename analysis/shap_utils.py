"""
SHAP explainability utilities for the Supervised Disengagement Forecaster.
Provides real-time SHAP waterfall charts for single customer risk attribution.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shap
from sklearn.ensemble import RandomForestClassifier

from analysis.predict_disengagement import load_and_prepare_features

ROOT = Path(__file__).parent.parent

FEATURE_DISPLAY_NAMES = {
    "avg_sessions_m1_4": "Avg Sessions (M1-4)",
    "avg_active_days_m1_4": "Avg Active Days (M1-4)",
    "avg_actions_m1_4": "Avg Product Actions (M1-4)",
    "min_active_days_m1_4": "Min Active Days (M1-4)",
    "max_active_days_m1_4": "Max Active Days (M1-4)",
    "last_sessions_m4": "Recent Sessions (Month 4)",
    "last_active_days_m4": "Recent Active Days (Month 4)",
    "last_actions_m4": "Recent Actions (Month 4)",
    "active_days_slope_m1_4": "Active Days Slope (Trend)",
    "active_days_momentum": "Active Days Momentum (M4 vs M1-3)",
    "integrations_m4": "Integrations Connected (M4)",
    "collaborators_m4": "Collaborators (M4)",
    "Plan Type_Free": "Plan: Free Tier",
    "Plan Type_Standard": "Plan: Standard Tier",
    "Plan Type_Premium": "Plan: Premium Tier",
    "Plan Type_Enterprise": "Plan: Enterprise Tier",
}

_CACHE = {}


def get_model_and_explainer():
    """Train and cache the Random Forest and SHAP TreeExplainer."""
    if "explainer" not in _CACHE:
        X, y, raw_feats = load_and_prepare_features()
        rf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
        rf.fit(X, y)
        explainer = shap.TreeExplainer(rf)
        _CACHE["X"] = X
        _CACHE["y"] = y
        _CACHE["raw_feats"] = raw_feats
        _CACHE["rf"] = rf
        _CACHE["explainer"] = explainer
        _CACHE["base_val"] = float(explainer.expected_value[1])
    return _CACHE["rf"], _CACHE["explainer"], _CACHE["X"], _CACHE["base_val"]


def build_shap_waterfall(customer_id: str, top_n: int = 7) -> go.Figure:
    """Generate an interactive Plotly SHAP waterfall chart for a specific customer."""
    rf, explainer, X, base_val = get_model_and_explainer()

    if customer_id not in X.index:
        raise ValueError(f"Customer ID '{customer_id}' not found in telemetry data.")

    cust_row = X.loc[[customer_id]]
    sv = explainer(cust_row)
    # Extract class 1 (Disengaged) SHAP values
    shap_vals = sv.values[0, :, 1]
    feature_names = X.columns.tolist()

    # Calculate actual predicted probability
    pred_prob = float(rf.predict_proba(cust_row)[0, 1])

    # Series of feature contributions
    series = pd.Series(shap_vals, index=feature_names)
    # Sort by absolute magnitude of contribution
    sorted_series = series.abs().sort_values(ascending=False)
    top_features = sorted_series.head(top_n).index.tolist()

    top_contribs = series.loc[top_features]
    other_contrib = series.drop(top_features).sum()

    # Friendly labels with actual feature values
    labels = []
    values = []
    for feat in top_features:
        friendly = FEATURE_DISPLAY_NAMES.get(feat, feat)
        actual_val = cust_row[feat].iloc[0]
        if isinstance(actual_val, float):
            val_str = f"{actual_val:.1f}" if abs(actual_val) >= 0.1 else f"{actual_val:.2f}"
        else:
            val_str = str(actual_val)
        labels.append(f"{friendly} ({val_str})")
        values.append(top_contribs[feat])

    if abs(other_contrib) > 0.001:
        labels.append("Other Attributes Combined")
        values.append(other_contrib)

    # Waterfall elements
    x_labels = ["Baseline Risk"] + labels + ["Final Forecast"]
    measures = ["absolute"] + ["relative"] * len(values) + ["total"]
    text_labels = (
        [f"{base_val:.1%}"]
        + [f"{v:+.1%}" for v in values]
        + [f"{pred_prob:.1%}"]
    )

    fig = go.Figure(
        go.Waterfall(
            name="SHAP Attribution",
            orientation="v",
            measure=measures,
            x=x_labels,
            textposition="outside",
            text=text_labels,
            y=[base_val] + values + [0],
            increasing=dict(marker=dict(color="#DE350B")),  # Red = Risk Escalation
            decreasing=dict(marker=dict(color="#0052CC")),  # Blue = Protective Retention Factor
            totals=dict(marker=dict(color="#FF991F")),      # Orange = Final Risk
            connector=dict(line=dict(color="#7A869A", dash="dot")),
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                f"<b>SHAP Risk Attribution: Customer {customer_id}</b><br>"
                f"<sup>Baseline Population Risk: {base_val:.1%} → Final Predicted Risk: {pred_prob:.1%}</sup>"
            ),
            x=0.0,
            xanchor="left",
        ),
        yaxis=dict(title="Predicted Probability of Disengagement", tickformat=".0%", range=[0, 1.05]),
        xaxis=dict(tickangle=-25),
        template="plotly_white",
        height=420,
        margin=dict(t=60, b=80, l=40, r=20),
    )

    return fig
def build_shap_diverging_bar(customer_id: str, top_n: int = 8) -> go.Figure:
    """Generate a double-sided (diverging) horizontal bar plot showing positive and negative
    SHAP contributions extending left and right from zero for a specific customer."""
    rf, explainer, X, base_val = get_model_and_explainer()

    if customer_id not in X.index:
        raise ValueError(f"Customer ID '{customer_id}' not found in telemetry data.")

    cust_row = X.loc[[customer_id]]
    sv = explainer(cust_row)
    shap_vals = sv.values[0, :, 1]
    feature_names = X.columns.tolist()
    pred_prob = float(rf.predict_proba(cust_row)[0, 1])

    series = pd.Series(shap_vals, index=feature_names)
    sorted_series = series.abs().sort_values(ascending=False)
    top_features = sorted_series.head(top_n).index.tolist()

    top_contribs = series.loc[top_features]

    # Format labels with actual values
    formatted_labels = []
    values = []
    colors = []
    text_labels = []

    for feat in top_features:
        friendly = FEATURE_DISPLAY_NAMES.get(feat, feat)
        actual_val = cust_row[feat].iloc[0]
        if isinstance(actual_val, float):
            val_str = f"{actual_val:.1f}" if abs(actual_val) >= 0.1 else f"{actual_val:.2f}"
        else:
            val_str = str(actual_val)
        val = top_contribs[feat]
        formatted_labels.append(f"{friendly} ({val_str})")
        values.append(val)
        colors.append("#DE350B" if val > 0 else "#0052CC")
        text_labels.append(f"{val:+.1%}")

    plot_df = pd.DataFrame({
        "feature": formatted_labels,
        "shap": values,
        "color": colors,
        "text": text_labels
    }).sort_values("shap", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=plot_df["feature"],
        x=plot_df["shap"],
        orientation="h",
        marker=dict(color=plot_df["color"]),
        text=plot_df["text"],
        textposition="outside",
        name="Feature Impact",
        showlegend=False
    ))

    fig.add_vline(x=0, line_width=1.5, line_color="#172B4D")

    fig.update_layout(
        title=dict(
            text=(
                f"<b>SHAP Bi-Directional Impact: Customer {customer_id}</b><br>"
                f"<sup>← Left (Blue): Reduces Churn Risk (Protective) | Right (Red): Escalates Churn Risk (Driver) → | Forecast: {pred_prob:.1%} (Base: {base_val:.1%})</sup>"
            ),
            x=0.0,
            xanchor="left",
        ),
        xaxis=dict(
            title="Marginal Impact on Disengagement Probability (SHAP Value)",
            tickformat="+.0%",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="#172B4D",
        ),
        yaxis=dict(title="Telemetry Feature (Actual Value)"),
        template="plotly_white",
        height=420,
        margin=dict(l=180, r=60, t=70, b=50),
    )
    return fig


def build_shap_global_bidirectional(n_samples: int = 500) -> go.Figure:
    """Generate a global double-sided impact plot showing average positive (risk-escalating)
    and negative (protective) SHAP values across the customer base."""
    rf, explainer, X, base_val = get_model_and_explainer()
    sample_X = X.iloc[:min(n_samples, len(X))]
    sv = explainer(sample_X)
    shap_vals = sv.values[:, :, 1]

    records = []
    for j, col in enumerate(X.columns):
        vals = shap_vals[:, j]
        pos_mean = float(np.mean(vals[vals > 0])) if np.any(vals > 0) else 0.0
        neg_mean = float(np.mean(vals[vals < 0])) if np.any(vals < 0) else 0.0
        mean_abs = float(np.mean(np.abs(vals)))
        friendly = FEATURE_DISPLAY_NAMES.get(col, col)
        records.append({
            "feature": friendly,
            "pos_impact": pos_mean,
            "neg_impact": neg_mean,
            "mean_abs": mean_abs
        })

    df = pd.DataFrame(records).sort_values("mean_abs", ascending=True).tail(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["feature"],
        x=df["neg_impact"],
        orientation="h",
        name="Protective Effect (Reduces Risk)",
        marker=dict(color="#0052CC"),
        text=[f"{v:.1%}" if abs(v) > 0.005 else "" for v in df["neg_impact"]],
        textposition="inside",
    ))
    fig.add_trace(go.Bar(
        y=df["feature"],
        x=df["pos_impact"],
        orientation="h",
        name="Risk Escalator (Increases Risk)",
        marker=dict(color="#DE350B"),
        text=[f"+{v:.1%}" if abs(v) > 0.005 else "" for v in df["pos_impact"]],
        textposition="inside",
    ))

    fig.add_vline(x=0, line_width=2, line_color="#172B4D")

    fig.update_layout(
        barmode="overlay",
        title=dict(
            text=(
                "<b>Global SHAP Bi-Directional Impact (Company-Wide)</b><br>"
                "<sup>Average feature impact when escalating risk (Right / Red) vs. protecting retention (Left / Blue)</sup>"
            ),
            x=0.0,
            xanchor="left",
        ),
        xaxis=dict(title="Average Marginal Impact on Disengagement Probability", tickformat="+.0%"),
        yaxis=dict(title="Telemetry Feature"),
        template="plotly_white",
        height=450,
        legend=dict(orientation="h", y=1.12, x=0.0),
        margin=dict(l=180, r=40, t=70, b=50),
    )
    return fig


def build_shap_beeswarm_plot(n_samples: int = 600) -> go.Figure:
    """Generate an interactive Plotly beeswarm/strip plot showing every customer as a dot,
    colored by feature value (Red = High, Blue = Low), spread across positive and negative SHAP impact."""
    rf, explainer, X, base_val = get_model_and_explainer()
    sample_X = X.iloc[:min(n_samples, len(X))]
    sv = explainer(sample_X)
    shap_vals = sv.values[:, :, 1]

    mean_abs = np.mean(np.abs(shap_vals), axis=0)
    top_indices = np.argsort(mean_abs)[-10:]

    fig = go.Figure()

    for idx in top_indices:
        col_name = X.columns[idx]
        friendly = FEATURE_DISPLAY_NAMES.get(col_name, col_name)
        s_vals = shap_vals[:, idx]
        raw_vals = sample_X[col_name].values.astype(float)

        vmin, vmax = np.percentile(raw_vals, 5), np.percentile(raw_vals, 95)
        denom = vmax - vmin if vmax > vmin else 1.0
        norm_vals = np.clip((raw_vals - vmin) / denom, 0, 1)

        is_last = bool(idx == top_indices[-1])

        hover = [
            f"<b>{friendly}</b><br>Actual Value: {r:.2f}<br>SHAP Value: {s:+.3f} ({s:+.1%} risk)"
            for r, s in zip(raw_vals, s_vals)
        ]

        fig.add_trace(
            go.Scatter(
                x=s_vals,
                y=[friendly] * len(s_vals),
                mode="markers",
                marker=dict(
                    size=5,
                    color=norm_vals,
                    colorscale=[[0.0, "#0052CC"], [0.5, "#B3D4FF"], [1.0, "#DE350B"]],
                    opacity=0.65,
                    showscale=is_last,
                    colorbar=dict(
                        title="Feature Value",
                        tickvals=[0.05, 0.95],
                        ticktext=["Low (Blue)", "High (Red)"],
                        len=0.7,
                        thickness=15,
                    ) if is_last else None,
                ),
                text=hover,
                hoverinfo="text",
                showlegend=False,
            )
        )

    fig.add_vline(x=0, line_width=1.5, line_color="#172B4D", line_dash="dash")

    fig.update_layout(
        title=dict(
            text=(
                "<b>SHAP Beeswarm Summary: Feature Value vs. Disengagement Impact</b><br>"
                "<sup>← Left: Decreases Churn Risk | Right: Escalates Churn Risk → | Dots: Red = High Feature Value, Blue = Low Feature Value</sup>"
            ),
            x=0.0,
            xanchor="left",
        ),
        xaxis=dict(
            title="SHAP Value (Impact on Model Output: Probability of Disengagement)",
            tickformat="+.0%",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="#172B4D",
        ),
        yaxis=dict(title="Telemetry Metric"),
        template="plotly_white",
        height=480,
        margin=dict(l=180, r=40, t=70, b=50),
    )
    return fig


def save_native_beeswarm_png(out_path: Path = ROOT / "docs" / "shap_beeswarm.png") -> Path:
    """Render and save publication-quality 300 DPI native SHAP beeswarm plot using matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rf, explainer, X, base_val = get_model_and_explainer()
    sample_X = X.iloc[:1000].copy()
    sv = explainer(sample_X)
    sv_class1 = sv[:, :, 1]
    sv_class1.feature_names = [FEATURE_DISPLAY_NAMES.get(col, col) for col in X.columns]

    plt.figure(figsize=(10, 6))
    shap.plots.beeswarm(sv_class1, max_display=12, show=False)
    plt.title("SHAP Summary: Feature Value vs. Disengagement Risk Impact", fontsize=13, pad=15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path
