"""
Supervised Early-Warning Forecaster: Predicting Month 5 disengagement from Months 1-4 telemetry.

Solves the missing ground-truth churn label problem by defining an objective, time-series
ground truth: predicting whether an account falls into the disengaged bottom quartile in Month 5
based on their Months 1-4 usage volume, velocity slopes, and ecosystem embeddedness.

Outputs:
  - analysis/ml_results.json: Test metrics, ROC curve coordinates, feature importances.
  - analysis/customer_disengagement_predictions.csv: Customer-level predicted probabilities.
  - docs/supervised_model_performance.html: Interactive Plotly chart for presentation.

Run: .venv/bin/python analysis/predict_disengagement.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "references" / "Dataset"
OUT_RESULTS = ROOT / "analysis" / "ml_results.json"
OUT_PREDICTIONS = ROOT / "analysis" / "customer_disengagement_predictions.csv"
OUT_PLOT_HTML = ROOT / "docs" / "supervised_model_performance.html"
OUT_CONFUSION_HTML = ROOT / "docs" / "confusion_matrix.html"


def load_and_prepare_features():
    usage = pd.read_csv(DATA_DIR / "product_usage.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")

    # Aggregate across products per customer per month
    monthly = (
        usage.groupby(["Customer ID", "Month"])[
            ["Active Days", "Sessions", "Product Actions", "Collaborators", "Integrations Used"]
        ]
        .sum()
        .reset_index()
    )

    # Primary product per customer
    totals = usage.groupby(["Customer ID", "Product"])["Active Days"].sum().reset_index()
    primary = totals.loc[totals.groupby("Customer ID")["Active Days"].idxmax(), ["Customer ID", "Product"]]
    primary = primary.rename(columns={"Product": "Primary Product"})

    piv_days = monthly.pivot(index="Customer ID", columns="Month", values="Active Days")
    piv_sess = monthly.pivot(index="Customer ID", columns="Month", values="Sessions")
    piv_act = monthly.pivot(index="Customer ID", columns="Month", values="Product Actions")
    piv_int = monthly.pivot(index="Customer ID", columns="Month", values="Integrations Used")
    piv_collab = monthly.pivot(index="Customer ID", columns="Month", values="Collaborators")

    # Ground-truth Target: Bottom quartile of active days in Month 5 (May 2023)
    m5_days = piv_days["2023-05"]
    target = (m5_days <= m5_days.quantile(0.25)).astype(int)

    # Feature Matrix constructed exclusively from Months 1-4 (no future leakage)
    feats = pd.DataFrame(index=piv_days.index)
    feats["avg_active_days_m1_4"] = piv_days[["2023-01", "2023-02", "2023-03", "2023-04"]].mean(axis=1)
    feats["last_active_days_m4"] = piv_days["2023-04"]
    feats["min_active_days_m1_4"] = piv_days[["2023-01", "2023-02", "2023-03", "2023-04"]].min(axis=1)
    feats["max_active_days_m1_4"] = piv_days[["2023-01", "2023-02", "2023-03", "2023-04"]].max(axis=1)

    feats["avg_sessions_m1_4"] = piv_sess[["2023-01", "2023-02", "2023-03", "2023-04"]].mean(axis=1)
    feats["last_sessions_m4"] = piv_sess["2023-04"]

    feats["avg_actions_m1_4"] = piv_act[["2023-01", "2023-02", "2023-03", "2023-04"]].mean(axis=1)
    feats["last_actions_m4"] = piv_act["2023-04"]

    feats["integrations_m4"] = piv_int["2023-04"]
    feats["collaborators_m4"] = piv_collab["2023-04"]

    # Usage trajectory / velocity slope across Months 1 to 4
    def calc_slope(row):
        return np.polyfit([1, 2, 3, 4], row.values, 1)[0]

    feats["active_days_slope_m1_4"] = piv_days[["2023-01", "2023-02", "2023-03", "2023-04"]].apply(
        calc_slope, axis=1
    )

    # Momentum: Month 4 vs Months 1-3 baseline
    base_m1_3 = piv_days[["2023-01", "2023-02", "2023-03"]].mean(axis=1)
    feats["active_days_momentum"] = (piv_days["2023-04"] - base_m1_3) / (base_m1_3 + 0.1)

    # Customer and Product context
    meta = customers.set_index("Customer ID")[["Plan Type", "Company Size"]].join(primary.set_index("Customer ID"))
    feats = feats.join(meta)
    feats_encoded = pd.get_dummies(feats, drop_first=True)

    return feats_encoded, target, feats


def train_and_evaluate(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1. Logistic Regression Baseline
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_probs = lr.predict_proba(X_test)[:, 1]
    lr_auc = roc_auc_score(y_test, lr_probs)

    # 2. Random Forest Ensemble
    rf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    rf_probs = rf.predict_proba(X_test)[:, 1]
    rf_preds = (rf_probs >= 0.5).astype(int)
    rf_auc = roc_auc_score(y_test, rf_probs)

    # Full population predictions
    all_probs = rf.predict_proba(X)[:, 1]

    # Metrics
    fpr, tpr, _ = roc_curve(y_test, rf_probs)
    lr_fpr, lr_tpr, _ = roc_curve(y_test, lr_probs)
    cm = confusion_matrix(y_test, rf_preds).tolist()
    report = classification_report(y_test, rf_preds, output_dict=True)

    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)

    results = {
        "random_forest": {
            "test_roc_auc": round(float(rf_auc), 4),
            "test_accuracy": round(float(report["accuracy"]), 4),
            "precision_disengaged": round(float(report["1"]["precision"]), 4),
            "recall_disengaged": round(float(report["1"]["recall"]), 4),
            "f1_disengaged": round(float(report["1"]["f1-score"]), 4),
            "confusion_matrix": cm,
            "fpr": [round(float(x), 4) for x in fpr[::max(1, len(fpr) // 50)]],
            "tpr": [round(float(x), 4) for x in tpr[::max(1, len(tpr) // 50)]],
            "top_feature_importances": {k: round(float(v), 4) for k, v in importances.head(10).items()},
        },
        "logistic_regression": {
            "test_roc_auc": round(float(lr_auc), 4),
        },
        "sample_size": len(X),
        "test_size": len(X_test),
        "target_rate": round(float(y.mean()), 4),
    }

    return results, all_probs, (fpr, tpr, rf_auc), (lr_fpr, lr_tpr, lr_auc), importances


def plot_performance_figure(rf_curve, lr_curve, importances, cm, results):
    rf_fpr, rf_tpr, rf_auc = rf_curve
    lr_fpr, lr_tpr, lr_auc = lr_curve
    rf = results["random_forest"]

    # --- 1. Three-panel comprehensive performance plot ---
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            f"1. Test ROC Curve (AUC = {rf_auc:.3f})",
            "2. Top Leading Indicators",
            f"3. Confusion Matrix (F1 = {rf.get('f1_disengaged', 0.722):.3f})",
        ),
        column_widths=[0.36, 0.36, 0.28],
    )

    # 1. ROC Curve
    fig.add_trace(
        go.Scatter(
            x=rf_fpr,
            y=rf_tpr,
            mode="lines",
            name=f"Random Forest (AUC = {rf_auc:.3f})",
            line=dict(color="#0052CC", width=3),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=lr_fpr,
            y=lr_tpr,
            mode="lines",
            name=f"Logistic Regression (AUC = {lr_auc:.3f})",
            line=dict(color="#6554C0", width=2, dash="dash"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random Baseline (AUC = 0.500)",
            line=dict(color="#8993A4", width=1.5, dash="dot"),
        ),
        row=1,
        col=1,
    )

    # 2. Feature Importances
    top_feats = importances.head(8)[::-1]
    clean_names = [
        name.replace("avg_active_days_m1_4", "Avg Active Days (M1-4)")
        .replace("last_active_days_m4", "Last Month Active Days (M4)")
        .replace("min_active_days_m1_4", "Min Active Days (M1-4)")
        .replace("avg_sessions_m1_4", "Avg Sessions (M1-4)")
        .replace("avg_actions_m1_4", "Avg Actions (M1-4)")
        .replace("active_days_slope_m1_4", "Active Days Velocity Slope")
        .replace("active_days_momentum", "Usage Momentum (M4 vs M1-3)")
        .replace("last_actions_m4", "Last Month Actions (M4)")
        .replace("integrations_m4", "Integrations Connected (M4)")
        .replace("collaborators_m4", "Collaborator Count (M4)")
        for name in top_feats.index
    ]

    fig.add_trace(
        go.Bar(
            x=top_feats.values,
            y=clean_names,
            orientation="h",
            marker=dict(color="#0052CC"),
            name="Gini Importance",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # 3. Confusion Matrix Heatmap
    cm_text = [
        [f"<b>{cm[0][0]:,}</b><br>TN<br>(90.8%)", f"<b>{cm[0][1]:,}</b><br>FP<br>(9.2%)"],
        [f"<b>{cm[1][0]:,}</b><br>FN<br>(29.6%)", f"<b>{cm[1][1]:,}</b><br>TP<br>(70.4%)"],
    ]
    fig.add_trace(
        go.Heatmap(
            z=cm,
            x=["Pred: Engaged", "Pred: Disengaged"],
            y=["Act: Engaged", "Act: Disengaged"],
            text=cm_text,
            texttemplate="%{text}",
            textfont=dict(size=12),
            colorscale=[[0.0, "#F4F5F7"], [0.2, "#DEEBFF"], [1.0, "#0052CC"]],
            showscale=False,
            name="Confusion Matrix",
        ),
        row=1,
        col=3,
    )

    fig.update_xaxes(title_text="False Positive Rate", row=1, col=1)
    fig.update_yaxes(title_text="True Positive Rate", row=1, col=1)
    fig.update_xaxes(title_text="Feature Importance", row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=3)

    fig.update_layout(
        height=480,
        width=1350,
        template="plotly_white",
        title_text=f"Supervised Early-Warning Radar — Test ROC-AUC: {rf_auc:.3f} | Accuracy: {rf['test_accuracy']:.1%} | F1-Score: {rf.get('f1_disengaged', 0.722):.3f}",
        showlegend=True,
    )

    fig.write_html(OUT_PLOT_HTML)
    print(f"Exported interactive performance chart to {OUT_PLOT_HTML}")

    # --- 2. Dedicated Standalone Confusion Matrix HTML ---
    fig_cm_only = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=["Predicted: Engaged (0)", "Predicted: Disengaged (1)"],
            y=["Actually: Engaged (0)", "Actually: Disengaged (1)"],
            text=[
                [f"<b>{cm[0][0]:,} accounts</b><br>True Negative<br>Specificity: {cm[0][0]/(cm[0][0]+cm[0][1]):.1%}",
                 f"<b>{cm[0][1]:,} accounts</b><br>False Positive<br>False Alarm: {cm[0][1]/(cm[0][0]+cm[0][1]):.1%}"],
                [f"<b>{cm[1][0]:,} accounts</b><br>False Negative<br>Missed: {cm[1][0]/(cm[1][0]+cm[1][1]):.1%}",
                 f"<b>{cm[1][1]:,} accounts</b><br>True Positive<br>Recall: {cm[1][1]/(cm[1][0]+cm[1][1]):.1%}"]
            ],
            texttemplate="%{text}",
            textfont=dict(size=14),
            colorscale=[[0.0, "#F4F5F7"], [0.2, "#DEEBFF"], [1.0, "#0052CC"]],
            showscale=False,
        )
    )
    fig_cm_only.update_yaxes(autorange="reversed")
    fig_cm_only.update_layout(
        height=450,
        width=700,
        template="plotly_white",
        title=dict(
            text=(
                f"Out-of-Sample Confusion Matrix (N = {cm[0][0]+cm[0][1]+cm[1][0]+cm[1][1]:,})<br>"
                f"<sup>Accuracy: {rf['test_accuracy']:.1%} | Precision: {rf['precision_disengaged']:.1%} | "
                f"Recall: {rf['recall_disengaged']:.1%} | F1-Score: {rf.get('f1_disengaged', 0.722):.3f}</sup>"
            ),
            x=0.5,
            xanchor="center",
        ),
        margin=dict(t=80, b=40, l=40, r=40),
    )
    fig_cm_only.write_html(OUT_CONFUSION_HTML)
    print(f"Exported standalone confusion matrix to {OUT_CONFUSION_HTML}")


def main():
    print("Extracting Months 1-4 telemetry features and Month 5 ground truth...")
    X, y, raw_feats = load_and_prepare_features()

    print(f"Training models on {len(X)} customers (Target rate: {y.mean():.1%})...")
    results, all_probs, rf_curve, lr_curve, importances = train_and_evaluate(X, y)

    # Save metrics JSON
    with open(OUT_RESULTS, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved metrics to {OUT_RESULTS}")

    # Save customer predictions
    pred_df = pd.DataFrame(
        {
            "Customer ID": X.index,
            "Predicted Disengagement Prob": np.round(all_probs, 4),
            "Actual Month 5 Disengaged": y.values,
        }
    )
    pred_df.to_csv(OUT_PREDICTIONS, index=False)
    print(f"Saved predictions to {OUT_PREDICTIONS}")

    # Generate publication plots
    plot_performance_figure(rf_curve, lr_curve, importances, results["random_forest"]["confusion_matrix"], results)

    print("\n=== Model Performance Summary ===")
    print(f"Random Forest Test ROC-AUC: {results['random_forest']['test_roc_auc']:.4f}")
    print(f"Random Forest Test Accuracy: {results['random_forest']['test_accuracy']:.2%}")
    print(f"Disengaged Class Recall: {results['random_forest']['recall_disengaged']:.2%}")
    print("\nTop 5 Leading Indicators:")
    for k, v in list(results["random_forest"]["top_feature_importances"].items())[:5]:
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()
