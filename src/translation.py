"""Translation evaluation utilities backed by sacrebleu chrF."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sacrebleu.metrics import CHRF


@dataclass(slots=True)
class TranslationEvaluation:
    """Container for corpus and per-example translation evaluation outputs."""

    summary: dict[str, Any]
    per_example: pd.DataFrame
    category_summary: pd.DataFrame
    signature: str

    def best_examples(self, top_k: int = 10) -> pd.DataFrame:
        return self.per_example.sort_values("chrf", ascending=False).head(top_k).reset_index(drop=True)

    def worst_examples(self, top_k: int = 10) -> pd.DataFrame:
        return self.per_example.sort_values("chrf", ascending=True).head(top_k).reset_index(drop=True)


def evaluate_chrf(
    frame: pd.DataFrame,
    *,
    char_order: int = 6,
    beta: int = 2,
    lowercase: bool = False,
    whitespace: bool = False,
    eps_smoothing: bool = False,
) -> TranslationEvaluation:
    """Evaluate a translation DataFrame with sacrebleu chrF."""

    required_columns = {"reference", "candidate"}
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(frame) == 0:
        raise ValueError("Translation evaluation requires at least one example.")

    metric = CHRF(
        char_order=char_order,
        beta=beta,
        lowercase=lowercase,
        whitespace=whitespace,
        eps_smoothing=eps_smoothing,
    )

    candidates = frame["candidate"].astype(str).tolist()
    references = frame["reference"].astype(str).tolist()
    corpus_result = metric.corpus_score(candidates, [references])

    scored_rows: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        sentence_result = metric.sentence_score(str(row["candidate"]), [str(row["reference"])])
        scored_rows.append({**row, "chrf": float(sentence_result.score)})
    per_example = pd.DataFrame(scored_rows)

    if "category" in per_example.columns:
        category_summary = (
            per_example.groupby("category", dropna=False)["chrf"]
            .agg(["count", "mean", "median", "min", "max"])
            .reset_index()
            .rename(
                columns={
                    "count": "num_examples",
                    "mean": "mean_chrf",
                    "median": "median_chrf",
                    "min": "min_chrf",
                    "max": "max_chrf",
                }
            )
            .sort_values(["mean_chrf", "num_examples"], ascending=[False, False])
            .reset_index(drop=True)
        )
    else:
        category_summary = pd.DataFrame(
            [
                {
                    "category": "all",
                    "num_examples": len(per_example),
                    "mean_chrf": per_example["chrf"].mean(),
                    "median_chrf": per_example["chrf"].median(),
                    "min_chrf": per_example["chrf"].min(),
                    "max_chrf": per_example["chrf"].max(),
                }
            ]
        )

    summary = {
        "chrf": float(corpus_result.score),
        "num_examples": int(len(per_example)),
        "char_order": int(char_order),
        "beta": int(beta),
        "lowercase": bool(lowercase),
        "whitespace": bool(whitespace),
        "eps_smoothing": bool(eps_smoothing),
        "mean_sentence_chrf": float(per_example["chrf"].mean()),
        "median_sentence_chrf": float(per_example["chrf"].median()),
        "min_sentence_chrf": float(per_example["chrf"].min()),
        "max_sentence_chrf": float(per_example["chrf"].max()),
    }

    return TranslationEvaluation(
        summary=summary,
        per_example=per_example,
        category_summary=category_summary,
        signature=str(metric.get_signature()),
    )


def plot_translation_report(
    evaluation: TranslationEvaluation,
    *,
    title: str,
    output_path: Path,
) -> Path:
    """Write a compact multi-panel chrF report."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    per_example = evaluation.per_example
    category_summary = evaluation.category_summary
    language_summary = None
    if "language" in per_example.columns:
        language_summary = (
            per_example.groupby("language")["chrf"]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
            .rename(columns={"chrf": "mean_chrf"})
        )

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    fig.suptitle(title, fontsize=15)

    axes[0, 0].hist(per_example["chrf"], bins=16, color="#1f77b4", alpha=0.85)
    axes[0, 0].set_title("Sentence chrF Distribution")
    axes[0, 0].set_xlabel("chrF")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].grid(alpha=0.25)

    category_plot = category_summary.sort_values("mean_chrf", ascending=True)
    axes[0, 1].barh(category_plot["category"], category_plot["mean_chrf"], color="#2ca02c")
    axes[0, 1].set_title("Mean chrF By Category")
    axes[0, 1].set_xlabel("Mean chrF")
    axes[0, 1].grid(alpha=0.25, axis="x")

    if language_summary is not None:
        axes[1, 0].barh(language_summary["language"], language_summary["mean_chrf"], color="#9467bd")
        axes[1, 0].set_title("Mean chrF By Language")
        axes[1, 0].set_xlabel("Mean chrF")
        axes[1, 0].grid(alpha=0.25, axis="x")
    else:
        axes[1, 0].axis("off")

    extremes = pd.concat(
        [
            per_example.sort_values("chrf", ascending=True).head(5),
            per_example.sort_values("chrf", ascending=False).head(5),
        ],
        ignore_index=True,
    )
    labels = [
        f"{row['id']} ({row.get('category', 'n/a')})"
        for _, row in extremes.iterrows()
    ]
    axes[1, 1].barh(labels, extremes["chrf"], color=["#d62728"] * 5 + ["#1f77b4"] * 5)
    axes[1, 1].set_title("Worst / Best Examples")
    axes[1, 1].set_xlabel("chrF")
    axes[1, 1].grid(alpha=0.25, axis="x")

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path
