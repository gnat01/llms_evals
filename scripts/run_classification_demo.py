"""Generate a synthetic classification report with tables and plots."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MPL_DIR = ROOT / ".mplconfig"
MPL_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_moons
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from classification import (
    evaluate_binary_classification,
    plot_binary_classification_report,
    render_narrative_summary,
)


OUTPUT_DIR = ROOT / "outputs_classification"
INPUT_DIR = ROOT / "inputs_classification"


def _ensure_matplotlib_cache() -> None:
    MPL_DIR.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))


def _markdown_table(frame: pd.DataFrame, digits: int = 4) -> str:
    formatted = frame.copy()
    for column in formatted.columns:
        if pd.api.types.is_float_dtype(formatted[column]):
            formatted[column] = formatted[column].map(lambda value: f"{value:.{digits}f}")
    return formatted.to_html(index=False, escape=False, border=0)


def _save_dataset_input(
    dataset_name: str,
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> Path:
    feature_names = [f"feature_{index}" for index in range(x_train.shape[1])]
    train_frame = pd.DataFrame(x_train, columns=feature_names)
    train_frame["label"] = y_train
    train_frame["split"] = "train"

    test_frame = pd.DataFrame(x_test, columns=feature_names)
    test_frame["label"] = y_test
    test_frame["split"] = "test"

    dataset_frame = pd.concat([train_frame, test_frame], ignore_index=True)
    output_path = INPUT_DIR / f"{dataset_name}.csv"
    dataset_frame.to_csv(output_path, index=False)
    return output_path


def _project_dataset_for_viz(features: np.ndarray) -> tuple[np.ndarray, str]:
    if features.shape[1] == 2:
        return features.copy(), "raw_2d"

    scaled = StandardScaler().fit_transform(features)
    projection = TSNE(
        n_components=2,
        init="pca",
        learning_rate="auto",
        perplexity=35,
        random_state=17,
    ).fit_transform(scaled)
    return projection, "tsne_2d"


def _save_dataset_visualization(
    dataset_name: str,
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> tuple[Path, Path, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    features = np.vstack([x_train, x_test])
    labels = np.concatenate([y_train, y_test])
    splits = np.array(["train"] * len(x_train) + ["test"] * len(x_test))

    projected, method = _project_dataset_for_viz(features)
    projection_frame = pd.DataFrame(
        {
            "x": projected[:, 0],
            "y": projected[:, 1],
            "label": labels,
            "split": splits,
            "projection_method": method,
        }
    )
    projection_csv_path = INPUT_DIR / f"{dataset_name}_projection.csv"
    projection_frame.to_csv(projection_csv_path, index=False)

    figure_path = INPUT_DIR / f"{dataset_name}_input_viz.png"
    fig, ax = plt.subplots(figsize=(8.5, 6.5), constrained_layout=True)
    class_colors = {0: "#1f77b4", 1: "#d62728"}
    split_markers = {"train": "o", "test": "x"}

    for split_name, marker in split_markers.items():
        for class_label, color in class_colors.items():
            mask = (splits == split_name) & (labels == class_label)
            ax.scatter(
                projected[mask, 0],
                projected[mask, 1],
                c=color,
                marker=marker,
                alpha=0.7 if split_name == "train" else 0.9,
                s=18 if split_name == "train" else 26,
                linewidths=0.8,
                label=f"class {class_label} / {split_name}",
            )

    ax.set_title(f"{dataset_name} input space ({method})")
    ax.set_xlabel("component_1")
    ax.set_ylabel("component_2")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=9)
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)
    return figure_path, projection_csv_path, method


def build_datasets(seed: int = 7) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    datasets: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    datasets["easy_separable"] = make_classification(
        n_samples=2200,
        n_features=12,
        n_informative=10,
        n_redundant=0,
        class_sep=2.2,
        flip_y=0.01,
        random_state=seed,
    )
    datasets["imbalanced_linear"] = make_classification(
        n_samples=3200,
        n_features=16,
        n_informative=8,
        n_redundant=4,
        weights=[0.92, 0.08],
        class_sep=1.1,
        flip_y=0.02,
        random_state=seed + 1,
    )
    datasets["nonlinear_moons"] = make_moons(
        n_samples=2400,
        noise=0.28,
        random_state=seed + 2,
    )
    datasets["hard_overlap"] = make_classification(
        n_samples=2600,
        n_features=20,
        n_informative=4,
        n_redundant=10,
        n_repeated=0,
        class_sep=0.55,
        flip_y=0.12,
        random_state=seed + 3,
    )
    return datasets


def build_models(seed: int = 7) -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", LogisticRegression(max_iter=3000, random_state=seed)),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=4,
            random_state=seed,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_depth=6,
            learning_rate=0.08,
            max_iter=250,
            random_state=seed,
        ),
    }


def run_demo() -> None:
    _ensure_matplotlib_cache()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = build_datasets()
    models = build_models()
    summary_rows: list[dict[str, object]] = []
    per_dataset_sections: list[str] = []

    for dataset_name, (features, labels) in datasets.items():
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            labels,
            test_size=0.35,
            random_state=17,
            stratify=labels,
        )
        dataset_input_path = _save_dataset_input(
            dataset_name,
            x_train,
            x_test,
            y_train,
            y_test,
        )
        dataset_viz_path, dataset_projection_path, projection_method = _save_dataset_visualization(
            dataset_name,
            x_train,
            x_test,
            y_train,
            y_test,
        )

        dataset_rows = []
        dataset_narratives = []
        for model_name, model in models.items():
            model.fit(x_train, y_train)
            probabilities = model.predict_proba(x_test)[:, 1]
            evaluation = evaluate_binary_classification(
                y_test,
                probabilities,
                threshold=0.5,
                cost_fp=1.0,
                cost_fn=5.0 if dataset_name == "imbalanced_linear" else 2.0,
            )

            summary = evaluation.summary.copy()
            summary.update(
                {
                    "dataset": dataset_name,
                    "model": model_name,
                    "brier_score": float(brier_score_loss(y_test, probabilities)),
                }
            )
            summary_rows.append(summary)
            dataset_rows.append(summary)
            dataset_narratives.append(
                render_narrative_summary(
                    evaluation,
                    label=f"{dataset_name} / {model_name}",
                )
            )

            figure_path = OUTPUT_DIR / f"{dataset_name}_{model_name}.png"
            plot_binary_classification_report(
                evaluation,
                title=f"{dataset_name} :: {model_name}",
                output_path=figure_path,
            )

            operating_points_path = OUTPUT_DIR / f"{dataset_name}_{model_name}_operating_points.csv"
            fbeta_path = OUTPUT_DIR / f"{dataset_name}_{model_name}_fbeta.csv"
            evaluation.operating_points_frame(top_k=12).to_csv(operating_points_path, index=False)
            evaluation.fbeta_metrics.to_csv(fbeta_path, index=False)

        dataset_frame = pd.DataFrame(dataset_rows).sort_values(
            by=["pr_auc", "js_divergence", "roc_auc"],
            ascending=[False, False, False],
        )
        top_model = dataset_frame.iloc[0]
        narrative = (
            f"For `{dataset_name}`, the strongest overall story came from "
            f"`{top_model['model']}` with PR-AUC={top_model['pr_auc']:.3f}, "
            f"ROC-AUC={top_model['roc_auc']:.3f}, and JSD={top_model['js_divergence']:.3f}. "
            "The table below shows how the models trade ranking quality, threshold behavior, "
            "and score-distribution separation."
        )
        dataset_section = "\n".join(
            [
                f"## Dataset: {dataset_name}",
                "",
                narrative,
                "",
                f"Input data for this dataset: [`{dataset_name}.csv`](../inputs_classification/{dataset_input_path.name})",
                "",
                f"Input projection: [`{dataset_projection_path.name}`](../inputs_classification/{dataset_projection_path.name})",
                "",
                f"Input visualization method: `{projection_method}`",
                "",
                f"![{dataset_name} input viz](../inputs_classification/{dataset_viz_path.name})",
                "",
                _markdown_table(
                    dataset_frame[
                        [
                            "model",
                            "roc_auc",
                            "pr_auc",
                            "precision",
                            "recall",
                            "js_divergence",
                            "expected_cost_per_example",
                            "best_cost_threshold",
                            "brier_score",
                        ]
                    ]
                ),
                "",
                "### Metric Narratives",
                "",
                *[f"- {line}" for line in dataset_narratives],
                "",
                "### Figures",
                "",
                *[
                    f"![{dataset_name} {row['model']}](../outputs_classification/{dataset_name}_{row['model']}.png)"
                    for _, row in dataset_frame.iterrows()
                ],
                "",
            ]
        )
        per_dataset_sections.append(dataset_section)

    leaderboard = pd.DataFrame(summary_rows).sort_values(
        by=["dataset", "pr_auc", "js_divergence", "roc_auc"],
        ascending=[True, False, False, False],
    )
    leaderboard_path = OUTPUT_DIR / "classification_leaderboard.csv"
    leaderboard.to_csv(leaderboard_path, index=False)

    report = "\n".join(
        [
            "# Classification Demo Report",
            "",
            "This report exercises the binary classification suite from `docs/specs_classification.md`.",
            "The emphasis is on three things:",
            "",
            "- scalar metrics that are easy to compare",
            "- visual diagnostics that explain threshold behavior",
            "- synthetic datasets ranging from easy to genuinely messy",
            "- persisted input datasets under `inputs_classification/` for reproducibility",
            "- color-coded input-space visualizations for every dataset",
            "",
            "## Global Leaderboard",
            "",
            _markdown_table(
                leaderboard[
                    [
                        "dataset",
                        "model",
                        "roc_auc",
                        "pr_auc",
                        "precision",
                        "recall",
                        "js_divergence",
                        "kl_divergence_0_to_1",
                        "kl_divergence_1_to_0",
                        "expected_cost_per_example",
                        "best_cost_threshold",
                        "brier_score",
                    ]
                ]
            ),
            "",
            "## Reading Guide",
            "",
            "- `ROC-AUC` and `PR-AUC` tell the ranking story.",
            "- `JSD` tells the class-separation story and is mandatory in this suite.",
            "- `KL` is included as a directional diagnostic, not the primary separation metric.",
            "- expected cost and best-cost threshold tell the deployment story.",
            "",
            *per_dataset_sections,
        ]
    )
    report_path = OUTPUT_DIR / "classification_demo_report.md"
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    run_demo()
