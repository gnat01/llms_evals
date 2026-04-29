"""Binary classification metrics, plots, and report helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn import metrics


@dataclass(slots=True)
class BinaryClassificationEvaluation:
    """Container for classification metrics and report-oriented artifacts."""

    summary: dict[str, Any]
    confusion: dict[str, int]
    threshold_metrics: pd.DataFrame
    fbeta_metrics: pd.DataFrame
    histogram: pd.DataFrame
    score_distributions: dict[str, np.ndarray]

    def summary_frame(self) -> pd.DataFrame:
        """Return the scalar summary metrics as a single-row DataFrame."""
        return pd.DataFrame([self.summary])

    def operating_points_frame(self, top_k: int = 10) -> pd.DataFrame:
        """Return threshold rows sorted by expected cost then threshold."""
        frame = self.threshold_metrics.sort_values(
            by=["expected_cost_per_example", "threshold"],
            ascending=[True, False],
        )
        return frame.head(top_k).reset_index(drop=True)


def _validate_binary_inputs(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    if y_true.ndim != 1 or y_score.ndim != 1:
        raise ValueError("y_true and y_score must be one-dimensional arrays.")
    if len(y_true) != len(y_score):
        raise ValueError("y_true and y_score must have the same length.")
    if len(y_true) == 0:
        raise ValueError("y_true and y_score must be non-empty.")
    unique_labels = set(np.unique(y_true).tolist())
    if not unique_labels.issubset({0, 1}) or len(unique_labels) < 2:
        raise ValueError("y_true must contain both binary labels 0 and 1.")

    return y_true, np.clip(y_score, 0.0, 1.0)


def _safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _confusion_counts(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, int]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def _compute_histograms(
    negatives: np.ndarray,
    positives: np.ndarray,
    num_bins: int,
    smoothing: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    bins = np.linspace(0.0, 1.0, num_bins + 1)
    hist_0, _ = np.histogram(negatives, bins=bins)
    hist_1, _ = np.histogram(positives, bins=bins)
    prob_0 = hist_0.astype(float) + smoothing
    prob_1 = hist_1.astype(float) + smoothing
    prob_0 /= prob_0.sum()
    prob_1 /= prob_1.sum()
    centers = 0.5 * (bins[:-1] + bins[1:])
    return centers, prob_0, prob_1


def _kl_divergence(prob_p: np.ndarray, prob_q: np.ndarray) -> float:
    return float(np.sum(prob_p * np.log(prob_p / prob_q)))


def _js_divergence(prob_p: np.ndarray, prob_q: np.ndarray) -> float:
    mean_prob = 0.5 * (prob_p + prob_q)
    return 0.5 * (
        _kl_divergence(prob_p, mean_prob) + _kl_divergence(prob_q, mean_prob)
    )


def _threshold_grid(y_score: np.ndarray, grid_size: int) -> np.ndarray:
    unique_scores = np.unique(y_score)
    if len(unique_scores) <= grid_size:
        grid = np.unique(np.concatenate(([0.0], unique_scores, [1.0])))
        return np.sort(grid)
    return np.linspace(0.0, 1.0, grid_size)


def _fbeta_score(precision: float, recall: float, beta: float) -> float:
    beta_sq = beta * beta
    denom = beta_sq * precision + recall
    if denom == 0.0:
        return 0.0
    return float((1.0 + beta_sq) * precision * recall / denom)


def evaluate_binary_classification(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: float = 0.5,
    beta_values: np.ndarray | None = None,
    cost_fp: float = 1.0,
    cost_fn: float = 1.0,
    num_bins: int = 20,
    smoothing: float = 1e-6,
    threshold_grid_size: int = 201,
) -> BinaryClassificationEvaluation:
    """Evaluate binary classification scores with threshold, cost, and divergence views."""

    y_true, y_score = _validate_binary_inputs(y_true, y_score)
    beta_values = (
        np.round(np.linspace(0.1, 2.0, 20), 2)
        if beta_values is None
        else np.asarray(beta_values, dtype=float)
    )

    negatives = y_score[y_true == 0]
    positives = y_score[y_true == 1]
    hist_centers, prob_0, prob_1 = _compute_histograms(
        negatives,
        positives,
        num_bins=num_bins,
        smoothing=smoothing,
    )

    roc_auc = metrics.roc_auc_score(y_true, y_score)
    pr_auc = metrics.average_precision_score(y_true, y_score)
    prevalence = float(np.mean(y_true))
    js_divergence = _js_divergence(prob_0, prob_1)
    kl_0_to_1 = _kl_divergence(prob_0, prob_1)
    kl_1_to_0 = _kl_divergence(prob_1, prob_0)

    y_pred = (y_score >= threshold).astype(int)
    confusion = _confusion_counts(y_true, y_pred)
    precision = _safe_divide(
        confusion["tp"],
        confusion["tp"] + confusion["fp"],
    )
    recall = _safe_divide(
        confusion["tp"],
        confusion["tp"] + confusion["fn"],
    )
    specificity = _safe_divide(
        confusion["tn"],
        confusion["tn"] + confusion["fp"],
    )
    accuracy = _safe_divide(confusion["tp"] + confusion["tn"], len(y_true))
    expected_cost = cost_fp * confusion["fp"] + cost_fn * confusion["fn"]
    expected_cost_per_example = expected_cost / len(y_true)

    threshold_rows: list[dict[str, float]] = []
    for current_threshold in _threshold_grid(y_score, threshold_grid_size):
        current_pred = (y_score >= current_threshold).astype(int)
        counts = _confusion_counts(y_true, current_pred)
        current_precision = _safe_divide(
            counts["tp"],
            counts["tp"] + counts["fp"],
        )
        current_recall = _safe_divide(
            counts["tp"],
            counts["tp"] + counts["fn"],
        )
        current_specificity = _safe_divide(
            counts["tn"],
            counts["tn"] + counts["fp"],
        )
        current_f1 = _fbeta_score(current_precision, current_recall, beta=1.0)
        current_cost = cost_fp * counts["fp"] + cost_fn * counts["fn"]
        threshold_rows.append(
            {
                "threshold": float(current_threshold),
                "precision": current_precision,
                "recall": current_recall,
                "specificity": current_specificity,
                "f1": current_f1,
                "tp": counts["tp"],
                "fp": counts["fp"],
                "tn": counts["tn"],
                "fn": counts["fn"],
                "expected_cost": float(current_cost),
                "expected_cost_per_example": float(current_cost / len(y_true)),
            }
        )
    threshold_metrics = pd.DataFrame(threshold_rows)
    best_cost_row = threshold_metrics.sort_values(
        by=["expected_cost_per_example", "threshold"],
        ascending=[True, False],
    ).iloc[0]

    fbeta_rows = []
    for beta in beta_values:
        fbeta_rows.append(
            {
                "beta": float(beta),
                "f_beta": _fbeta_score(precision, recall, beta=float(beta)),
            }
        )
    fbeta_metrics = pd.DataFrame(fbeta_rows)

    summary = {
        "threshold": float(threshold),
        "n_samples": int(len(y_true)),
        "positive_rate": prevalence,
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "precision": float(precision),
        "recall": float(recall),
        "specificity": float(specificity),
        "accuracy": float(accuracy),
        "js_divergence": float(js_divergence),
        "kl_divergence_0_to_1": float(kl_0_to_1),
        "kl_divergence_1_to_0": float(kl_1_to_0),
        "expected_cost": float(expected_cost),
        "expected_cost_per_example": float(expected_cost_per_example),
        "best_cost_threshold": float(best_cost_row["threshold"]),
        "best_cost_per_example": float(best_cost_row["expected_cost_per_example"]),
        "cost_fp": float(cost_fp),
        "cost_fn": float(cost_fn),
    }

    histogram = pd.DataFrame(
        {
            "bin_center": hist_centers,
            "class_0_probability": prob_0,
            "class_1_probability": prob_1,
        }
    )

    return BinaryClassificationEvaluation(
        summary=summary,
        confusion=confusion,
        threshold_metrics=threshold_metrics,
        fbeta_metrics=fbeta_metrics,
        histogram=histogram,
        score_distributions={"class_0": negatives, "class_1": positives},
    )


def render_narrative_summary(
    evaluation: BinaryClassificationEvaluation,
    *,
    label: str,
) -> str:
    """Render a compact narrative that explains the metric story."""

    summary = evaluation.summary
    if summary["roc_auc"] >= 0.9:
        ranking_assessment = "excellent ranking separation"
    elif summary["roc_auc"] >= 0.8:
        ranking_assessment = "strong ranking separation"
    elif summary["roc_auc"] >= 0.7:
        ranking_assessment = "usable but imperfect ranking separation"
    else:
        ranking_assessment = "weak ranking separation"

    if summary["js_divergence"] >= 0.35:
        distribution_story = "class score distributions are clearly separated"
    elif summary["js_divergence"] >= 0.15:
        distribution_story = "class score distributions are only moderately separated"
    else:
        distribution_story = "class score distributions overlap heavily"

    threshold_metrics = evaluation.threshold_metrics
    chosen_row = threshold_metrics.iloc[
        (threshold_metrics["threshold"] - summary["threshold"]).abs().argmin()
    ]
    best_cost_delta = summary["expected_cost_per_example"] - summary["best_cost_per_example"]

    if best_cost_delta <= 1e-12:
        cost_story = "the chosen threshold is already cost-optimal on this sample."
    else:
        cost_story = (
            "the chosen threshold leaves measurable cost on the table; "
            f"switching to {summary['best_cost_threshold']:.3f} would reduce "
            f"cost per example by {best_cost_delta:.4f}."
        )

    return (
        f"{label}: ROC-AUC={summary['roc_auc']:.3f}, PR-AUC={summary['pr_auc']:.3f}, "
        f"JSD={summary['js_divergence']:.3f}. The model shows {ranking_assessment}, and "
        f"{distribution_story}. At threshold {chosen_row['threshold']:.3f}, precision="
        f"{chosen_row['precision']:.3f} and recall={chosen_row['recall']:.3f}; {cost_story}"
    )


def plot_binary_classification_report(
    evaluation: BinaryClassificationEvaluation,
    *,
    title: str,
    output_path: Path,
) -> Path:
    """Write a multi-panel visualization summarizing the evaluation."""

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = evaluation.summary
    threshold_metrics = evaluation.threshold_metrics
    fbeta_metrics = evaluation.fbeta_metrics
    class_0_scores = evaluation.score_distributions["class_0"]
    class_1_scores = evaluation.score_distributions["class_1"]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    fig.suptitle(title, fontsize=16)

    fpr, tpr, _ = metrics.roc_curve(
        np.concatenate([np.zeros_like(class_0_scores), np.ones_like(class_1_scores)]),
        np.concatenate([class_0_scores, class_1_scores]),
    )
    axes[0, 0].plot(fpr, tpr, label=f"ROC-AUC={summary['roc_auc']:.3f}", color="#1f77b4")
    axes[0, 0].plot([0, 1], [0, 1], linestyle="--", color="grey")
    axes[0, 0].set_title("ROC Curve")
    axes[0, 0].set_xlabel("False Positive Rate")
    axes[0, 0].set_ylabel("True Positive Rate")
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(
        threshold_metrics["threshold"],
        threshold_metrics["precision"],
        color="blue",
        label="Precision",
    )
    axes[0, 1].plot(
        threshold_metrics["threshold"],
        threshold_metrics["recall"],
        color="red",
        label="Recall",
    )
    axes[0, 1].axvline(summary["threshold"], linestyle="--", color="black")
    axes[0, 1].set_title(f"Precision/Recall vs Threshold (PR-AUC={summary['pr_auc']:.3f})")
    axes[0, 1].set_xlabel("Threshold")
    axes[0, 1].set_ylabel("Score")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(
        threshold_metrics["threshold"],
        threshold_metrics["precision"],
        label="Precision",
        color="#d62728",
    )
    axes[0, 2].plot(
        threshold_metrics["threshold"],
        threshold_metrics["recall"],
        label="Recall",
        color="#2ca02c",
    )
    axes[0, 2].plot(
        threshold_metrics["threshold"],
        threshold_metrics["specificity"],
        label="Specificity",
        color="#9467bd",
    )
    axes[0, 2].axvline(summary["threshold"], linestyle="--", color="black")
    axes[0, 2].set_title("Metrics Across Thresholds")
    axes[0, 2].set_xlabel("Threshold")
    axes[0, 2].set_ylabel("Score")
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    bins = np.linspace(0.0, 1.0, len(evaluation.histogram) + 1)
    axes[1, 0].hist(
        class_0_scores,
        bins=bins,
        density=True,
        alpha=0.55,
        color="#1f77b4",
        label="Class 0",
    )
    axes[1, 0].hist(
        class_1_scores,
        bins=bins,
        density=True,
        alpha=0.55,
        color="#ff7f0e",
        label="Class 1",
    )
    axes[1, 0].set_title(f"Score Distributions (JSD={summary['js_divergence']:.3f})")
    axes[1, 0].set_xlabel("Predicted Probability")
    axes[1, 0].set_ylabel("Density")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(
        threshold_metrics["threshold"],
        threshold_metrics["expected_cost_per_example"],
        color="#8c564b",
    )
    axes[1, 1].axvline(summary["best_cost_threshold"], linestyle="--", color="black")
    axes[1, 1].set_title("Expected Cost Per Example")
    axes[1, 1].set_xlabel("Threshold")
    axes[1, 1].set_ylabel("Cost")
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(
        fbeta_metrics["beta"],
        fbeta_metrics["f_beta"],
        marker="o",
        color="#17becf",
    )
    axes[1, 2].set_title("F-Beta Sweep")
    axes[1, 2].set_xlabel("Beta")
    axes[1, 2].set_ylabel("F-Beta")
    axes[1, 2].grid(alpha=0.3)

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path
